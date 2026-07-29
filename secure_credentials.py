#!/usr/bin/env python3
"""
Secure Credential Management for Trello

Stores the Trello API key + token in the OS credential vault via keyring
(Windows Credential Manager / macOS Keychain / Linux Secret Service)
rather than plain text.
"""

import keyring

TRELLO_SERVICE = "Trello_API"


def store_trello_credentials(api_key, token):
    keyring.set_password(TRELLO_SERVICE, "api_key", api_key)
    keyring.set_password(TRELLO_SERVICE, "token", token)


def load_trello_config():
    api_key = keyring.get_password(TRELLO_SERVICE, "api_key")
    token = keyring.get_password(TRELLO_SERVICE, "token")

    if not api_key or not token:
        raise ValueError(
            "Trello credentials not found in Windows Credential Manager. "
            "Run setup_credentials.py first."
        )

    return {"key": api_key, "token": token}


def delete_trello_credentials():
    keyring.delete_password(TRELLO_SERVICE, "api_key")
    keyring.delete_password(TRELLO_SERVICE, "token")
