#!/usr/bin/env python3
"""
Trello REST API client.

Credentials are loaded from Windows Credential Manager via secure_credentials.py
(never printed, never hardcoded). Board, list, label, and member IDs are loaded
from a local, gitignored config.json (see config.example.json). When no config is
present, use the discovery helpers (list_boards, list_lists) to find the IDs.
"""

import json
import os
import requests
from secure_credentials import load_trello_config

BASE_URL = "https://api.trello.com/1"
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def _auth_params():
    cfg = load_trello_config()
    return {"key": cfg["key"], "token": cfg["token"]}


def load_config():
    """Load board/list/label/member IDs from config.json.

    Returns an empty dict if config.json does not exist, so callers can fall
    back to live discovery (list_boards / list_lists).
    """
    if not os.path.exists(CONFIG_PATH):
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# --- Discovery -------------------------------------------------------------

def list_boards():
    resp = requests.get(f"{BASE_URL}/members/me/boards",
                        params={**_auth_params(), "fields": "name,id,closed"})
    resp.raise_for_status()
    return resp.json()


def list_lists(board_id):
    resp = requests.get(f"{BASE_URL}/boards/{board_id}/lists",
                        params={**_auth_params(), "fields": "name,id"})
    resp.raise_for_status()
    return resp.json()


def list_labels(board_id):
    resp = requests.get(f"{BASE_URL}/boards/{board_id}/labels",
                        params={**_auth_params(), "fields": "name,color", "limit": 1000})
    resp.raise_for_status()
    return resp.json()


def whoami():
    resp = requests.get(f"{BASE_URL}/members/me",
                        params={**_auth_params(), "fields": "username,fullName,id"})
    resp.raise_for_status()
    return resp.json()


# --- Reading ---------------------------------------------------------------

def get_board_cards(board_id, fields="name,id,idList,labels,due,shortUrl"):
    resp = requests.get(f"{BASE_URL}/boards/{board_id}/cards",
                        params={**_auth_params(), "fields": fields})
    resp.raise_for_status()
    return resp.json()


def get_member_cards(member_id, board_id=None,
                     fields="name,id,idList,idBoard,labels,due,shortUrl"):
    resp = requests.get(f"{BASE_URL}/members/{member_id}/cards",
                        params={**_auth_params(), "filter": "open", "fields": fields})
    resp.raise_for_status()
    cards = resp.json()
    if board_id:
        cards = [c for c in cards if c.get("idBoard") == board_id]
    return cards


def get_card(card_id, fields="name,desc,idList,labels,shortUrl", checklists="all"):
    resp = requests.get(f"{BASE_URL}/cards/{card_id}",
                        params={**_auth_params(), "fields": fields, "checklists": checklists})
    resp.raise_for_status()
    return resp.json()


def get_card_comments(card_id):
    resp = requests.get(f"{BASE_URL}/cards/{card_id}/actions",
                        params={**_auth_params(), "filter": "commentCard"})
    resp.raise_for_status()
    return resp.json()


# --- Writing ---------------------------------------------------------------

def create_card(list_id, name, description="", member_id=None, label_ids=None):
    params = {**_auth_params(), "idList": list_id, "name": name, "desc": description}
    if member_id:
        params["idMembers"] = member_id
    if label_ids:
        params["idLabels"] = ",".join(label_ids)
    resp = requests.post(f"{BASE_URL}/cards", params=params)
    resp.raise_for_status()
    return resp.json()


def add_label(card_id, label_id):
    resp = requests.post(f"{BASE_URL}/cards/{card_id}/idLabels",
                         params={**_auth_params(), "value": label_id})
    resp.raise_for_status()
    return resp.json()


def add_checklist(card_id, name, items=None):
    resp = requests.post(f"{BASE_URL}/checklists",
                         params={**_auth_params(), "idCard": card_id, "name": name})
    resp.raise_for_status()
    checklist = resp.json()
    for item in (items or []):
        ri = requests.post(f"{BASE_URL}/checklists/{checklist['id']}/checkItems",
                           params={**_auth_params(), "name": item})
        ri.raise_for_status()
    return checklist


def add_comment(card_id, text):
    resp = requests.post(f"{BASE_URL}/cards/{card_id}/actions/comments",
                         params={**_auth_params(), "text": text})
    resp.raise_for_status()
    return resp.json()


def update_card(card_id, **fields):
    """Update card fields, e.g. name='...', desc='...', idList='...'."""
    resp = requests.put(f"{BASE_URL}/cards/{card_id}",
                        params={**_auth_params(), **fields})
    resp.raise_for_status()
    return resp.json()


# --- CLI -------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "boards":
        for b in list_boards():
            print(f"{b['id']}  {b['name']}")
    elif len(sys.argv) > 2 and sys.argv[1] == "lists":
        for l in list_lists(sys.argv[2]):
            print(f"{l['id']}  {l['name']}")
    elif len(sys.argv) > 2 and sys.argv[1] == "labels":
        for l in list_labels(sys.argv[2]):
            print(f"{l['id']}  {l['color']}  {l['name']}")
    elif len(sys.argv) > 1 and sys.argv[1] == "whoami":
        me = whoami()
        print(f"{me['id']}  {me['username']}  {me['fullName']}")
    else:
        print("Usage:")
        print("  python trello_client.py whoami          # your member id")
        print("  python trello_client.py boards          # your boards")
        print("  python trello_client.py lists <board_id>")
        print("  python trello_client.py labels <board_id>")
