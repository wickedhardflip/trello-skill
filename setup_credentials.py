#!/usr/bin/env python3
"""
Interactive one-time setup for Trello API credentials.

Run this yourself in your own terminal (not via Claude) so the key/token
are typed directly by you and never pass through the conversation.

Get your API key + token first from: https://trello.com/app-key
  - Your API Key is shown on that page.
  - Click the "Token" link on that same page to generate a token
    (grants this app read/write access to your boards).
"""

import getpass
from secure_credentials import store_trello_credentials, load_trello_config


def main():
    print("Trello API credential setup")
    print("Get these from https://trello.com/app-key if you don't have them yet.")
    print()

    api_key = getpass.getpass("Paste your Trello API Key (input hidden): ").strip()
    token = getpass.getpass("Paste your Trello Token (input hidden): ").strip()

    if not api_key or not token:
        print("Both values are required. Aborting.")
        return

    store_trello_credentials(api_key, token)
    print()
    print("Stored in Windows Credential Manager under target 'Trello_API'.")

    # Verify round-trip without printing the actual values
    cfg = load_trello_config()
    print(f"Verified: api_key length={len(cfg['key'])}, token length={len(cfg['token'])}")


if __name__ == "__main__":
    main()
