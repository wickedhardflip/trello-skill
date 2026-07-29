# Trello Skill

A Claude Code skill that reads and writes Trello cards directly through the Trello REST API. Instead of drafting card text for you to copy and paste, Claude can create cards from a standard template, list your assigned cards, suggest labels, and read or update existing cards, all from inside a session.

Credentials never pass through a Claude conversation. Setup is done by you, in your own terminal, with masked input, and stored in Windows Credential Manager. Nothing secret or org identifying is ever committed to this repo.

## What it does

- **Create cards** from a consistent template (goal, stakeholders, background, success criteria, risks), with labels and a checklist, assigned to you.
- **List** your open assigned cards, grouped by list.
- **Review** existing cards and suggest label or category additions.
- **Read and update** a card's description, checklist, labels, and comments.

Every new card is shown to you as a draft before it is posted, and no existing card is ever changed without your approval.

## How it works

Three pieces:

1. **Connector code** (Python) talks to the Trello API and loads credentials from the OS vault.
2. **Skill files** (`skill/SKILL.md` and `skill/trello.md`) tell Claude the conventions and the `/trello` command behavior. You copy these into your `.claude/` directory.
3. **Local config** (`config.json`, gitignored) holds your board, list, label, and member IDs so the commands work without a lookup every time.

### Repo layout

```
trello-skill/
  README.md                 this file
  secure_credentials.py     stores and loads the API key and token (Windows Credential Manager)
  setup_credentials.py      one time interactive credential setup
  trello_client.py          Trello API wrapper and CLI
  config.example.json       template for your local config
  .gitignore                keeps config.json and any secrets out of git
  skill/
    SKILL.md                skill context and conventions
    trello.md               the /trello command definition
```

## Prerequisites

- Python 3.x
- Python packages: `keyring` and `requests`

  ```
  pip install keyring requests
  ```

- Windows Credential Manager (built into Windows) for credential storage. On macOS the `keyring` library uses the Keychain, and on Linux it uses the Secret Service or KWallet, so the same code works there for future team use.

## Step 1: Get a Trello API key and token

Trello issues API keys through its Power-Up admin, not a plain signup form.

### Create a Power-Up (one time)

1. Go to **https://trello.com/power-ups/admin** and click **New**.
2. Give it a name (for example Claude Code) and pick your workspace.
3. It asks for an **Iframe connector URL**. This is only used if you build an in app Trello UI extension, which this skill does not. Put any placeholder such as `https://example.com` so the form will save.
4. Open the new Power-Up, go to the **API Key** tab, and click **Generate a new API Key**.

The API Key is a low sensitivity client identifier, similar to an OAuth client ID. It is reasonable to type into your terminal, but still keep it out of chat.

### Generate a token

The admin page does not always show a token link, so build the authorization URL yourself:

```
https://trello.com/1/authorize?expiration=never&scope=read,write&response_type=token&name=Claude+Code&key=YOUR_API_KEY
```

Query parameters explained:

- `expiration=never` the token does not expire. Use `1day` or `30days` if you prefer a shorter life.
- `scope=read,write` the skill needs both to create and update cards.
- `response_type=token` returns the token on the page.
- `name=Claude+Code` the app name shown on the authorization screen.
- `key=YOUR_API_KEY` your API key from the previous step.

Steps:

1. Replace `YOUR_API_KEY` with your key and paste the full URL into your browser while logged into Trello.
2. Click **Allow** on the authorization screen.
3. Trello shows a long token string on the page.

The token is a real credential. It grants read and write access to your boards. Treat it like a password. Never paste it into chat, Slack, email, or a ticket.

## Step 2: Store your credentials

Run the setup script yourself from the project directory. Do not have Claude run it, because it needs to read your terminal input directly so the values never appear in a conversation.

```
python setup_credentials.py
```

It prompts for the API Key and Token with hidden input, then stores both in Windows Credential Manager under the target `Trello_API`. Nothing is written to disk in plain text, and the values are never printed back (only their length, as a sanity check).

To rotate credentials later, run `setup_credentials.py` again. It overwrites the stored values.

## Step 3: Configure your board

Copy the example config and fill in your own IDs.

```
cp config.example.json config.json
```

`config.json` is gitignored and stays local. Find your IDs with the client CLI:

```
python trello_client.py whoami            # your member id
python trello_client.py boards            # your boards and their ids
python trello_client.py lists <board_id>  # list ids on a board
python trello_client.py labels <board_id> # label ids on a board
```

Fill `board_id`, `member_id`, the `lists` map (list name to id), and the `labels` map (label name to id) in `config.json`. The skill reads this so it does not have to look everything up on every run. If `config.json` is absent, the skill falls back to live discovery using the same commands.

## Step 4: Install the skill

Copy the two skill files into your Claude Code config so the `/trello` command is available:

```
cp skill/SKILL.md   ~/.claude/skills/trello/SKILL.md
cp skill/trello.md  ~/.claude/commands/trello.md
```

On Windows the paths are `C:\Users\<you>\.claude\skills\trello\SKILL.md` and `C:\Users\<you>\.claude\commands\trello.md` (or the `.claude` directory of the project you run Claude Code from). Create the `trello` folder under `skills` if it does not exist.

## Usage

- `/trello create` draft a card from the template, with labels and a checklist, assigned to you. Claude shows the full draft and posts only after you approve.
- `/trello list` show your open assigned cards, grouped by list, with labels and due dates.
- `/trello review` audit your cards and suggest label or category additions. Claude applies only what you approve.
- `/trello read <card>` pull a card's full content. Claude can update the description, checklist, or labels with your approval.

You can also use the client directly:

```
python trello_client.py boards
python trello_client.py lists <board_id>
```

## Conventions

The skill follows a consistent card style so your board stays readable.

- **Template:** Desired Outcome/Goal; Stakeholders (Business, Technical, Impacted users); Background; Success Criteria; Risks.
- **Labels and a checklist** on every new card. The checklist name fits the project, for example Phases, Next Steps, or Migration Checklist.
- **No dashes** in card prose. Sentences use periods and commas.
- **Never fabricate** names, owners, or values. Unknown values are left as a fill in marker and raised as a question.
- **Approval first.** New cards are shown as a draft before posting. Existing cards are never changed without approval for that specific change.

## Security notes

- No secrets are stored in this repo. The API key and token live only in Windows Credential Manager.
- `config.json` holds board and member IDs and is gitignored. Only `config.example.json` with placeholders is committed.
- `.gitignore` also excludes `credentials.env`, any `.env`, and `__pycache__`.
- Before pushing, scan tracked files to confirm no key, token, board id, member id, hostname, or email is present.

## Sharing with the team

The repo is built to share. A new teammate does the same three steps: create their own Power-Up and token, run `setup_credentials.py` to store their own credentials, and create their own `config.json` for their board. No code changes are needed, because all personal and org values live in credentials or the gitignored config.

## Troubleshooting

- **401 Unauthorized:** the API key or token is wrong or the token was revoked. Re-run `setup_credentials.py` with a fresh token.
- **Invalid key or token in a browser test:** confirm you copied the full key and token with no trailing spaces.
- **Card lands on the wrong board or list:** check the IDs in `config.json` against `python trello_client.py boards` and `lists`.
- **keyring errors on setup:** confirm `keyring` is installed and, on Linux, that a Secret Service backend is available.
- **Nothing returned by list:** confirm `member_id` in `config.json` matches `python trello_client.py whoami`.
