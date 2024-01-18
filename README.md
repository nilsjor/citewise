# citewise
BibTeX reference abbreviation tool implementing the ISO 4 standard

## Background

This tool was written out of necessity, when I was working on a conference paper and needed to "compress" the list of citations as much as possible, without removing any references or any of the required fields.

The main purpose is to automatically prune and abbreviate journal and conference names, as well as some minor touches on other bib-fields.
It is also possible to skip the abbreviation stage, which will still harmonize some of the formatting of your references; see Usage below.

Currently, it handles Journal Articles, Conference Proceedings, Technical Reports, and ePrints.

Please note that all text processing is rule-based, there is no NPL or high-level AI operating here.

## Dependencies
This requires [`pyiso4`](https://github.com/pierre-24/pyiso4) to be installed, read the instructions on their webpage.
```sh
pip install pyiso4
```

It also comes bundled with [`biblib`](https://github.com/aclements/biblib/tree/master) by Austin Clements. This is not to be confused with https://pypi.org/project/biblib/0.1.3/.

## Prerequisites
`PYTHONUTF8=1`

## Installing from source
```sh
python setup.py sdist && pip install dist/citewise*.gz
```

## Usage
Example usage
```sh
citewise refs.bib -o refs-abbrev.bib
```

### Conference Proceedings
Conference Proceedings are treated more extensively. It will do the following extra steps:

  1. Remove any "prefix" containing the year, e.g "IEEE INFOCOM 2017 - "
  2. Remove all year (plus any punctuation), e.g. "2004."
  3. Remove trailing acronyms, e.g. " (CDC)", ", AAMAS", or " - WWW"
  4. Apply title case on lower-case words longer than 3 characters

Next, it applies the following extra, optional steps:

  6. Remove the number in the order, e.g. "4th", or "Twenty-Sixth" (skip using `--ignore-order`)
  7. Remove the word "Annual" (skip using `--ignore-annual`)
  8. Insert "Proceedings of the ..." if missing (skip using `--ignore-proc`, or *remove* using `--remove-proc`)
  9. Finally, apply ISO4 abbreviations (skip using `--no-abbrev`)

### Examples
Default settings
```
IEEE Transactions on Control of Network Systems -> IEEE Trans. Control Netw. Syst.
2022 IEEE International Conference on Robotics and Automation (ICRA 2022) -> Proc. IEEE Int. Conf. Robot. Autom.
2022 IEEE 23rd International Symposium on a World of Wireless, Mobile and Multimedia Networks (WoWMoM) -> Proc. IEEE Int. Symp. World Wirel. Mob. Multimed. Netw.
IEEE International Conference on Communications (ICC 2021) -> Proc. IEEE Int. Conf. Commun.
IEEE Transactions on Intelligent Transportation Systems -> IEEE Trans. Intell. Transp. Syst.
Annual Review of Control, Robotics, and Autonomous Systems -> Annu. Rev. Control Robot. Auton. Syst.
IEEE Internet of Things Journal -> IEEE Internet Things J.
2023 IEEE 20th Consumer Communications & Networking Conference, CCNC -> Proc. IEEE Consum. Commun. Netw. Conf.
Distributed Autonomous Robotic Systems -> Proc. Distrib. Auton. Robot. Syst.
IEEE INFOCOM 2017 - IEEE Conference on Computer Communications -> Proc. IEEE Conf. Comput. Commun.
Journal of Communications and Networks -> J. Commun. Netw.
IEEE Transactions on Vehicular Technology -> IEEE Trans. Veh. Technol.
```

Skip abbreviation
```
2022 IEEE International Conference on Robotics and Automation (ICRA 2022) -> Proceedings of the IEEE International Conference on Robotics and Automation
2022 IEEE 23rd International Symposium on a World of Wireless, Mobile and Multimedia Networks (WoWMoM) -> Proceedings of the IEEE International Symposium on a World of Wireless, Mobile and Multimedia Networks
IEEE International Conference on Communications (ICC 2021) -> Proceedings of the IEEE International Conference on Communications
2023 IEEE 20th Consumer Communications & Networking Conference, CCNC -> Proceedings of the IEEE Consumer Communications & Networking Conference
Distributed Autonomous Robotic Systems -> Proceedings of the Distributed Autonomous Robotic Systems
IEEE INFOCOM 2017 - IEEE Conference on Computer Communications -> Proceedings of the IEEE Conference on Computer Communications
```
