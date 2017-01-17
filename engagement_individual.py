#!/usr/bin/env python
""" 
This is a command line email analysis tool,connects to an IMAP server, downloads emails and summarises who has been talking to whom.

Developed to assist in reporting on engagement between the UTS eResearch team and our stakeholders.

for usage:

python3 imap.py --help

OUTPUT: a JSON file summarising email interactions, which can be mined for reporting purposes later
 
"""

import argparse
import getpass
import os, sys, imaplib
import interactions


def main():
    parser = argparse.ArgumentParser(description='Build a social network graph')
    parser.add_argument('server')
    parser.add_argument('username')
    parser.add_argument('-i', '--ignore-headers', action='store_true', help='Ignore the actual to and from headers on email (for emails that have been forwarded)')
    parser.add_argument('-f', '--folder', default='Inbox', help='Specific a folder to look in eg archive, defaults to Inbox')
    parser.add_argument('-u', '--from-unit', default=None, help='Specific the name of an org-unit to place in the centre')
    parser.add_argument('-l', '--ldap', help='LDAP Server')
    parser.add_argument('-s', '--unit-string', default='utsUnitLevel1')
    parser.add_argument('-q', '--query', default='ALL', help='IMAP Query: eg SINCE 01-Dec-2016. Warning: Defaults to ALL')
    parser.add_argument('-m', '--mapping', default=None, help='JSON dictionary mapping between LDAP groups and human-readable names, use vale of false for groups to ignore')
    args = parser.parse_args()
    args.password = getpass.getpass('Password:')

    int = interactions.Interactions(args)
    int.deal_with_the_emails()
    int.report()
    int.close()




if __name__ == "__main__":
    main()
