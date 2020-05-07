#!/usr/bin/env python
##
# Project: MOHD Mailboxes Quota
# Description: Get the mailboxes quota and usage
# Author: Fabio Castelli <fabio.c@mohd.it>
# License: GPL-3+
##

import argparse
import csv
import getpass
import imaplib
import operator
import shlex
import sys
import typing

from constants import APP_NAME, VERSION

from keepassx.db import Database


def get_mailbox_quota(server: str,
                      port: int,
                      use_ssl: bool,
                      root_dir: str,
                      username: str,
                      password: str
                      ) -> typing.Tuple[int, int]:
    """
    Get mailbox quota
    :param server: IMAP server
    :param port: IMAP port
    :param use_ssl: specifies whether to use SSL for IMAP connection
    :param root_dir: root directory
    :param username: mailbox username
    :param password: mailbox password
    :return: a tuple with used size and total size
    """
    mailbox = (imaplib.IMAP4_SSL(server, port)
               if use_ssl
               else imaplib.IMAP4(server, port))
    mailbox.login(username, password)
    # Format: b'"User quota" (STORAGE X Y)'
    quota_str = (mailbox.getquotaroot(root_dir)[1][1][0]
                 # Remove parenthesis
                 .translate(None, b'()')
                 # Convert to string
                 .decode('utf-8'))
    # Split preserving quotes
    items = shlex.split(quota_str, ' ')
    # Get results
    results = None
    if items and items[0] == 'User quota':
        # Calculate quota
        used_size = int(items[-2])
        total_size = int(items[-1])
        results = (used_size, total_size)
    return results


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments and return the options
    :return: a Namespace object with the arguments from argparse
    """
    parser = argparse.ArgumentParser()
    group = parser.add_argument_group(title="Mail server options")
    group.add_argument('-s',
                       '--server',
                       type=str,
                       required=True,
                       help="Mail server address")
    group.add_argument('-p',
                       '--port',
                       type=int,
                       required=True,
                       help="Mail server port")
    group.add_argument('-S',
                       '--ssl',
                       action='store_true',
                       default=False,
                       help="Mail server SSL usage")
    group.add_argument('-R',
                       '--root',
                       type=str,
                       default='INBOX',
                       help="Mail server root")
    group = parser.add_argument_group(title='Output options')
    group.add_argument('-o',
                       '--output',
                       type=str,
                       default='-',
                       help="Output for results (use - for stdout)")
    group.add_argument('-f',
                       '--format',
                       type=str,
                       choices=('text', 'csv'),
                       default='text',
                       help="Output format for results")
    group.add_argument('-q',
                       '--quiet',
                       action='store_true',
                       default=False,
                       help="Don't show messages about progress loading")
    group = parser.add_argument_group(title="KeePassX database options")
    group.add_argument('-d',
                       '--database',
                       type=str,
                       required=True,
                       help="KeePassX database file path")
    group.add_argument('-g',
                       '--group',
                       type=str,
                       required=True,
                       help="KeePassX group name")
    group.add_argument('-P',
                       '--password',
                       type=str,
                       required=False,
                       help="KeePassX database password")
    group.add_argument('-k',
                       '--key',
                       type=str,
                       required=False,
                       help='KeePassX key file path')
    group = parser.add_argument_group(title="Optional arguments")
    group.add_argument('-V',
                       '--version',
                       action='version',
                       version="{PROGRAM} {VERSION}".format(PROGRAM=APP_NAME,
                                                            VERSION=VERSION))
    return parser.parse_args()


if __name__ == '__main__':
    # Command line arguments
    arguments = parse_arguments()
    # Get password argument from command line
    if arguments.password == '-':
        arguments.password = getpass.getpass(
            'Please insert database password: ').encode('utf-8')
    # Get key file content
    if arguments.key:
        # Open key file
        with open(arguments.key, 'rb') as file_key:
            key_file_content = file_key.read()
    else:
        # No key needed
        key_file_content = None
    # Process results
    if True:
        # Get passwords from database
        with open(arguments.database, 'rb') as file_database:
            database = Database(contents=file_database.read(),
                                password=arguments.password,
                                key_file_contents=key_file_content)
        # Get selected group only
        selected_group = [group for group in database.groups if
                          group.group_name == arguments.group]
        if selected_group:
            # List entries for the selected group
            entries = [entry
                       for entry in database.entries
                       if entry.group is selected_group[0]
                       and entry.username
                       and entry.password]
            results = []
            for index, entry in enumerate(entries):
                # Process each entry and show progress on stderr
                quota = get_mailbox_quota(arguments.server,
                                          arguments.port,
                                          arguments.ssl,
                                          arguments.root,
                                          entry.username,
                                          entry.password)
                if not arguments.quiet:
                    sys.stderr.write('{:>3d}/{:d} {:50s}\n'.format(
                          index + 1, len(entries), entry.title))
                results.append({'title': entry.title,
                                'username': entry.username,
                                'total': quota[1] // 1000,
                                'used': quota[0] // 1000,
                                'percent': quota[0] / quota[1] * 100})
            # Get max title and username length
            max_title = max([len(item['title']) for item in results])
            max_username = max([len(item['username']) for item in results])
            str_format = ('{{:{:d}s}}'
                          '  {{:{:d}s}}'
                          '  {{:>5d}} / {{:<5d}}'
                          '  {{:>5.2f}}%'
                          ' {{}}\n').format(max_title, max_username)
            # Set output file for results
            if arguments.output == '-':
                file_output = sys.stdout
            else:
                file_output = open(arguments.output,
                                   mode='w',
                                   newline='\n',
                                   encoding='utf-8')
            # Set output format for results
            if arguments.format == 'csv':
                csv_writer = csv.writer(file_output,
                                        delimiter=';',
                                        quotechar='"',
                                        quoting=csv.QUOTE_NONNUMERIC)
                csv_writer.writerow(('Title',
                                     'Username',
                                     'Used space',
                                     'Total space',
                                     'User percent',
                                     'Info'))
            else:
                csv_writer = None
            # Show results
            for entry in sorted(results,
                                key=operator.itemgetter('percent'),
                                reverse=True):
                ouput_arguments = (entry['title'],
                                   entry['username'],
                                   entry['used'],
                                   entry['total'],
                                   round(entry['percent'], 2),
                                   'Warning' if entry['percent'] >= 80 else '')
                if arguments.format == 'csv':
                    csv_writer.writerow(ouput_arguments)
                else:
                    file_output.write(str_format.format(*ouput_arguments))
            # Close output
            file_output.close()
        else:
            # Passwords group not found
            print('Group "{GROUP}" not found'.format(
                GROUP=arguments.group))
            sys.exit(2)
