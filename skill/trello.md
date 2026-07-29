# Trello Card Manager

You are helping the user read and write Trello cards directly through the Trello REST API.

## Setup

- **Code:** the directory where this repo is cloned (e.g. `~/projects/trello-skill`)
- **Client:** `trello_client.py` — import its functions or call its CLI from that directory.
- **Credentials:** loaded from Windows Credential Manager (target `Trello_API`) via `secure_credentials.py`. Never print them, never put them in files or commands.
- **Config:** `trello_client.load_config()` returns board id, list name to id map, label name to id map, and the user's member id from the gitignored `config.json`. If config is empty, discover with `list_boards`, `list_lists`, `list_labels`, `whoami`.

## Prerequisites

If credentials are not set up, tell the user to run `python setup_credentials.py` from the project directory themselves (masked input, stored in Windows Credential Manager). See the repo README for how to get a Trello API key and token.

## Parse Arguments

- `/trello` or `/trello create` — Draft and create a card (with approval)
- `/trello list` — Show the user's open assigned cards grouped by list
- `/trello review` — Audit cards and suggest label additions (approval required)
- `/trello read <card>` — Read a card's full content; update with approval

## create

1. Ask what the card is about if not given. Fill the standard template (Desired Outcome/Goal; Stakeholders with Business, Technical, Impacted users; Background; Success Criteria; Risks). Never fabricate names or values. Use a fill in marker and ask when something needed is unknown.
2. Suggest labels (from the config label map) and a checklist (name fits the project) that match the content.
3. Ask which list to post to if not given.
4. Show the complete draft: title, full description, labels, checklist items, target list, assignee.
5. Wait for explicit approval. Then create the card with `create_card`, add labels with `add_label`, add the checklist with `add_checklist`, and assign the member. Return the card short URL.

## list

Use `get_member_cards(member_id, board_id)` with IDs from `load_config()`. Group by list, show labels and due dates. Read only.

## review

Fetch cards with `get_board_cards` or `get_member_cards`, read each description, and suggest label or category additions based on the content. Present as a table of suggestions. Apply only the ones the user approves, one confirmation set at a time.

## read

Use `get_card(card_id)` and `get_card_comments(card_id)` to show full content. If the user wants changes, propose them and apply with `update_card`, `add_label`, or `add_checklist` only after approval for each change.

## Rules (mandatory)

1. Never edit an existing card without explicit per change approval.
2. Always show the draft before posting anything new.
3. No dashes in prose that will be shared.
4. Never fabricate names, owners, or values. Identifiers verbatim. Ask when unsure.
5. New cards get labels and a checklist.
