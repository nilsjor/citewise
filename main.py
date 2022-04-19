#!/usr/bin/env python3
import argparse
import sys
import re

import biblib.bib
import biblib.messages
import biblib.algo

import pyiso4
from pyiso4.ltwa import Abbreviate

import colors

def abbrev_journal(string, abbr=True):

    # Skip certain journals
    known_issues = 'arXiv PapersOnLine'.split()
    for name in known_issues:
        if name in string: return string

    # Create list for every new step
    process = [string]

    # Remove trailing acronyms, e.g. " (CDC)", ", AAMAS", or " - WWW"
    process.append( re.sub('(\s+\(.+\)|[\,\;\:\-\–\—]\s+\S+)\s*$', '', process[-1]) )

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

    # Remove the number in the order, e.g. "4th", "Twenty-Sixth"
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
    elif proc != 'keep' and 'Proceedings' not in process[-1].split():
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

    # Parse arguments
    arg_parser = argparse.ArgumentParser(
        description='Abbreviate and shorten journal and conference names and prune ' +
                    'unnecessary fields from one or more .bib database(s)')

    arg_parser.add_argument('bib', nargs='+', type=open,
        help='.bib file(s) to process')

    arg_parser.add_argument('-o', '--outfile', default='output.bib',
        help='Name of output file')

    arg_parser.add_argument('-v', '--verbose', default=False, action='store_true',
        help='Highlight changes made to titles')

    arg_parser.add_argument('--no-abbrev', dest='abbrev', default=True,
        help='Skip the abbreviation step', action='store_false')

    command_group = arg_parser.add_mutually_exclusive_group()
    command_group.add_argument('--remove-proc', dest='proc', action='store_const',
        help='Remove "Proceedings" prefix from conference titles', const='remove')
    command_group.add_argument('--keep-proc', dest='proc', action='store_const',
        help='Ignore any "Proceedings" prefix in conference titles', const='keep')

    arg_parser.add_argument('--keep-order', dest='order', default=True,
        help='Ignore any ordering in conference titles, e.g. "3rd"', action='store_false')

    arg_parser.add_argument('--keep-annual', dest='annu', default=True,
        help='Ignore any "Annual" in conference titles', action='store_false')

    args = arg_parser.parse_args()

    # Load databases
    db = biblib.bib.Parser().parse(args.bib, log_fp=sys.stderr).get_entries()

    # Create an empty file for the output - throws an exception if no write perm
    f = open(args.outfile,'w')
    f.close()

    # Create abbreviate object
    abbreviate = Abbreviate.create()

    # Iterate through the database
    for ent in db.values():

        # Find empty fields
        clear = 'shorttitle abstract keywords copyright note langid language urldate timestamp file groups'.split()
        for key in ent.keys():
            if key not in clear and not ent[key]:
                clear.append(key)

        # Clear unnecessary and empty fields for all entries
        for key in clear:
            try: del ent[key]
            except KeyError: pass

        if ent.typ == 'article':
            # Clear additional field for journal articles
            clear = 'editor publisher'.split()
            for key in clear:
                try: del ent[key]
                except KeyError: pass

            # Abbreviate journal names
            j = biblib.algo.tex_to_unicode(ent['journal'])
            j_abbrev = abbrev_journal(j, args.abbrev)
            ent['journal'] = j_abbrev
            if args.verbose and j != j_abbrev:
                j_c, j_abbrev_c = colors.colordiff(j,j_abbrev)
                print(f'{j_c} -> {j_abbrev_c}')

        elif ent.typ == 'inproceedings':
            # Clear additional field for conference proceedings
            clear = 'editor publisher address series booktitleaddon eventtitle'.split()
            for key in clear:
                try: del ent[key]
                except KeyError: pass

            # Trim and abbreviate conference titles
            conf = biblib.algo.tex_to_unicode(ent['booktitle'])
            conf_abbrev = abbrev_conference(conf,
                proc=args.proc, annu=args.annu, order=args.order, abbr=args.abbrev)
            ent['booktitle'] = '{' + conf_abbrev + '}'
            if args.verbose and conf != conf_abbrev:
                conf_c, conf_abbrev_c = colors.colordiff(conf,conf_abbrev)
                print(f'{conf_c} -> {conf_abbrev_c}')

        # Write the updated entry to the output
        with open(args.outfile, 'a') as f:
            f.write(ent.to_bib())
            f.write("\n\n")

if __name__ == '__main__':
    main()
