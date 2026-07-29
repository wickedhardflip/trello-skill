---
name: trello
description: Read and write Trello cards directly (create from a template, list assigned cards, suggest labels, read and update cards) via the Trello REST API
---

# Trello Skill — Context Document

You are helping the user work with their Trello board directly through the Trello REST API.

## Project Location

- **Code:** the directory where this repo is cloned (e.g. `~/projects/trello-skill`)
- **Client:** `trello_client.py` (import its functions or call its CLI)
- **Credentials:** Windows Credential Manager, target `Trello_API` (via `secure_credentials.py`). Never printed, never in files.
- **Config:** `config.json` (gitignored) holds board id, list name to id map, label name to id map, and the user's member id. Load it with `trello_client.load_config()`. If it is missing, discover IDs with `list_boards`, `list_lists`, `list_labels`, `whoami`.

## Client Functions (trello_client.py)

- Discovery: `list_boards()`, `list_lists(board_id)`, `list_labels(board_id)`, `whoami()`
- Reading: `get_board_cards(board_id)`, `get_member_cards(member_id, board_id)`, `get_card(card_id)`, `get_card_comments(card_id)`
- Writing: `create_card(list_id, name, description, member_id, label_ids)`, `add_label(card_id, label_id)`, `add_checklist(card_id, name, items)`, `add_comment(card_id, text)`, `update_card(card_id, **fields)`
- Config: `load_config()`

## Commands

`/trello <subcommand>`

### create
Draft a card using the standard template, then post it after approval.

1. Fill the template (see Card Template below). Never fabricate stakeholder names, owners, or values. Use a fill in marker and ask when a needed value is unknown.
2. Suggest labels and a checklist that fit the project. Checklist name fits the project (for example Phases, Next Steps, Migration Checklist), not a fixed label.
3. Show the full draft: title, description, labels, checklist, target list, assignee.
4. Wait for approval. Only after the user approves, create the card, add labels, add the checklist, and assign the member.

### list
Show the user's open assigned cards grouped by list, with labels and due dates. Use `get_member_cards(member_id, board_id)`. Read only.

### review
Audit existing cards and suggest label or category additions based on card content. Present as suggestions only. Never apply a change without per card, per change approval.

### read <card>
Pull a card's full content (description, labels, checklist, comments). You may update the description, checklist, or labels, but only with explicit approval for each change.

## Card Template

Fill these fields, in order, with these exact labels:

Desired Outcome/Goal

Stakeholders
- Business:
- Technical:
- Impacted users:

Background

Success Criteria

Risks

Notes on the template:
- Technical stakeholders are tagged with @handles when known.
- Success Criteria can be dense prose or a short list depending on how many discrete items there are.
- Background is short, one or two sentences of context.
- Risks lead with a category label (for example Prod impacting, Resource constraint, Vendor dependent) then a colon and the specific detail, with real numbers and dates when known.
- Steps and checklist items are NOT part of the description. They go in a separate Trello checklist.

## Rules (mandatory)

1. **Never edit an existing card** (labels, description, checklist) without explicit approval for that specific change.
2. **Always show the draft** before posting anything new.
3. **No dashes** in prose that will be shared. Use periods and commas instead.
4. **Never fabricate** names, owners, or values. Display identifiers verbatim. Ask when a needed value is unknown.
5. New cards get labels and a checklist matching board conventions.
