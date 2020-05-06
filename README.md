# MOHD Mailboxes Quota

**Description:** A Python application to get the mailboxes quota and usage.

**Copyright:** 2020 Fabio Castelli <fabio.c@mohd.it>

**License:** GPL-3+

**Source code:** https://github.com/mohd-dev/mohd-mailboxes-quota

# Description

Get mailbox quota for each IMAP account.

The credentials are get from a KeepassX database protected by password and key.

# Usage

You can execute the script using the following syntax:

    python mohd_mailboxes_quota.py
      --server IMAP_SERVER
      --port IMAP_PORT
      [--ssl]
      [--root ROOT_DIRECTORY]
      --database DATABASE
      --group GROUP
      [--password PASSWORD]
      [--key KEY]
     

The following command line arguments are provided:

    -s, --server IMAP_SERVER
        Specifies the Mail server address
    -p, --port IMAP_PORT
        Specifies the Mail server port
    -S, --ssl
        Specifies whether to use SSL during connection
    -R, --root ROOT_DIRECTORY
        Specifies the IMAP root directory (default INBOX)
    -d, --database DATABASE_PATH
        Specifies the KeePassX database file path
    -g, --group GROUP_NAME
        Specifies the KeePassX database group name with the credentials to use
    -P, --password PASSWORD (optional)
        Specifies the KeePassX database password
        If you use the password '-' it will be asked interactivily
    -k, --key DATABASE_KEY_FILE
        Specifies the KeePassX database key file path

# System Requirements

* Python 3.x
* keepassx (<https://pypi.org/project/keepassx/>)
