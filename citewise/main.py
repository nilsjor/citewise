#!/usr/bin/env python3
import argparse
import sys
import re

from citewise.biblib import bib as biblib
from citewise.biblib import algo as bibalg

import pyiso4
from pyiso4.ltwa import Abbreviate

from citewise import colors

def abbrev_journal(string, abbr=True):

    # Skip certain journals
    known_issues = 'arXiv PapersOnLine'.split()
    for name in known_issues:
        if name in string: return string

    # Create list for every new step
    process = [string]

    if abbr:

        # Remove any additional punctuation
        process.append( re.sub('[\,\;\:]', '', process[-1]) )

        # Apply abbreviation
        process.append( abbreviate(process[-1]+' ') )

        # Fix cases where abbreviation are equal to the original word
        string_copy =  process[-1]
        for word in process[-2].split(): # For all words in the unabbreviated string
            bad_abbrev = word + '.'
            if bad_abbrev in process[-1].split():
                string_copy = string_copy.replace(bad_abbrev, word)
        process.append( string_copy )

    return process[-1]


def abbrev_conference(string, proc=None, annu=False, order=False, abbr=True):

    # Create list for every new step
    process = [string]

    # Remove any "prefix" containing the year, e.g "IEEE INFOCOM 2017 - "
    process.append( re.sub('.*\s\d{2,4}\s?[\:\-\–\—]\s+', '', process[-1]) )

    # Remove all year (plus any punctuation), e.g. "2004."
    process.append( re.sub('(\d{4}|\'\d{2})[\.\,\;]?', '', process[-1]) )

    # Remove trailing acronyms, e.g. " (CDC)", ", AAMAS", or " - WWW"
    process.append( re.sub('(\s+\(.+\)|[\,\;\:\-\–\—]\s+\S+)\s*$', '', process[-1]) )

    # Apply title case on lower-case words longer than 3 characters
    process.append( re.sub(r'(\b)([a-z]{4,})',
        lambda s : s.group(1) + s.group(2).title(), process[-1]) )

    # Optional: Remove the number in the order, e.g. "4th", "Twenty-Sixth"
    if order:
        if re.search('\d+(st|nd|rd|th)\s+', process[-1], flags=re.IGNORECASE):
            process.append( re.sub('\d+(st|nd|rd|th)\s+', '', process[-1], flags=re.IGNORECASE) )
        else:
            process.append( re.sub('\S*(first|second|third|fourth|fifth|sixth|seventh|eight|ninth|tenth|tieth|dredth)\s+', '', process[-1], flags=re.IGNORECASE) )

    # Optional: Remove "Annual"
    if annu:
        process.append( re.sub('(Annual)\s+', '', process[-1], flags=re.IGNORECASE) )

    # Optional: Enforce/remove "Proceedings"
    if proc == 'remove':
        process.append( re.sub('(Proceedings)\s*(of the)?\s+', '', process[-1], flags=re.IGNORECASE) )
    elif proc != 'ignore' and 'Proceedings' not in process[-1].split():
        process.append( 'Proceedings of the ' + process[-1] )

    # Optional: Apply ISO4 abbreviations
    if abbr:

        # Remove additional punctuation
        process.append( re.sub('[\,\;\:]', '', process[-1]) )

        # Apply abbreviation
        process.append( abbreviate(process[-1]+' ') )

        # Fix cases where abbreviation are equal to the original word
        string_copy =  process[-1]
        for word in process[-2].split(): # For all words in the unabbreviated string
            bad_abbrev = word + '.'
            if bad_abbrev in process[-1].split():
                string_copy = string_copy.replace(bad_abbrev, word)
        process.append( string_copy )

    # Clean up whitespaces
    process.append( re.sub('\s+', ' ', process[-1]) )

    return process[-1]

def main():

    # Yes, I did it this way.
    global abbreviate

    # Create argument parser
    arg_parser = argparse.ArgumentParser(
        description='Abbreviate and shorten journal and conference names and prune ' +
                    'unnecessary fields from one or more .bib database(s)')

    # Positional arguments
    arg_parser.add_argument('bib', nargs='+', type=open,
        help='.bib file(s) to process')

    # Optional argument: output file
    arg_parser.add_argument('-o', '--outfile', default='output.bib',
        help='Name of output file')

    # Optional argument: quiet
    arg_parser.add_argument('-q', '--quiet', default=False, action='store_true',
        help='Suppress printing the changes to the console')

    # Optional argument: skip abbreviation
    arg_parser.add_argument('-n', '--no-abbrev', dest='abbrev', default=True,
        help='Skip the abbreviation step', action='store_false')

    # Optional argument: ignore ordering
    arg_parser.add_argument('--ignore-order', dest='order', default=True,
        help='Ignore any ordering in conference titles, e.g. "3rd"', action='store_false')

    # Optional argument: ignore "annual"
    arg_parser.add_argument('--ignore-annual', dest='annu', default=True,
        help='Ignore any "Annual" in conference titles', action='store_false')

    # Optional argument: ignore/remove "Proceedings"
    command_group = arg_parser.add_mutually_exclusive_group()
    command_group.add_argument('--ignore-proc', dest='proc', action='store_const',
        help='Ignore any "Proceedings" prefix in conference titles', const='ignore')
    command_group.add_argument('--remove-proc', dest='proc', action='store_const',
        help='Remove "Proceedings" prefix from conference titles', const='remove')

    # Parse arguments
    args = arg_parser.parse_args()

    # Load databases
    db = biblib.Parser().parse(args.bib, log_fp=sys.stderr).get_entries()

    # Create an empty file for the output - throws an exception if no write perm
    f = open(args.outfile,'w')
    f.close()

    # Create abbreviate object
    abbreviate = Abbreviate.create()

    # Iterate through the database
    for ent in db.values():

        # Fields to clear
        clear = 'shorttitle abstract pages keywords copyright note langid language urldate timestamp file groups'.split()

        # Find empty fields and add to the list
        for key in ent.keys():
            if key not in clear and not ent[key]:
                clear.append(key)

        # Clear unnecessary and empty fields for all entries
        for key in clear:
            try: del ent[key]
            except KeyError: pass

        if ent.typ == 'techreport':
            # It type not present, use default
            try:
                t = bibalg.tex_to_unicode(ent['type'])
            except biblib.FieldError:
                t = 'Technical Report'

            # Abbreviate techrep type
            if args.abbrev: t_abbrev = abbrev_journal(t)
            else: t_abbrev = t

            ent['type'] = '{' + t_abbrev + '}'

            # Print changes
            if not args.quiet and t != t_abbrev:
                t_c, t_abbrev_c = colors.colordiff(t,t_abbrev)
                print(f'{t_c} -> {t_abbrev_c}')

        if ent.typ == 'article':
            # Clear additional field for journal articles
            clear = 'editor publisher'.split()
            for key in clear:
                try: del ent[key]
                except KeyError: pass

            # Abbreviate journal names
            j = bibalg.tex_to_unicode(ent['journal'])
            j_abbrev = abbrev_journal(j, args.abbrev)
            ent['journal'] = j_abbrev

            # Special treatment for ePrints
            try:
                if ent['eprint'] + ent['eprinttype'] + ent['primaryclass'] != None:
                    # Remove the journal field
                    try: del ent['journal']
                    except KeyError: pass
            except biblib.FieldError: pass

            # Print changes
            if not args.quiet and j != j_abbrev:
                j_c, j_abbrev_c = colors.colordiff(j,j_abbrev)
                print(f'{j_c} -> {j_abbrev_c}')

        elif ent.typ == 'inproceedings':
            # Clear additional field for conference proceedings
            clear = 'editor publisher address series booktitleaddon eventtitle volume'.split()
            for key in clear:
                try: del ent[key]
                except KeyError: pass

            # Trim and abbreviate conference titles
            conf = bibalg.tex_to_unicode(ent['booktitle'])
            conf_abbrev = abbrev_conference(conf,
                proc=args.proc, annu=args.annu, order=args.order, abbr=args.abbrev)
            ent['booktitle'] = '{' + conf_abbrev + '}'

            # Print changes
            if not args.quiet and conf != conf_abbrev:
                conf_c, conf_abbrev_c = colors.colordiff(conf,conf_abbrev)
                print(f'{conf_c} -> {conf_abbrev_c}')

        # Write the updated entry to the output
        with open(args.outfile, 'a') as f:
            f.write(ent.to_bib())
            f.write('\n\n')

if __name__ == '__main__':
    main()
