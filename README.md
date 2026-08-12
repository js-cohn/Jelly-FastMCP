# Jelly FastMCP

A FastMCP-based Model Context Protocol (MCP) server for the [Jelly API](https://letsjelly.com/help/advanced/api).
It exposes the API as MCP tools for creating, reading, updating, and managing conversations, labels, contacts, drafts, autoresponder settings, comments, and more.

## Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended)

## Configuration

Configure the following environment variables to authenticate and set defaults:

| Environment Variable | Description |
| --- | --- |
| `JELLY_API_TOKEN` | Jelly API token from **Settings → API Tokens** |
| `JELLY_BASE_URL` | Optional override for the API base URL. Defaults to `https://app.letsjelly.com/api` |

## Running

### Direct execution

```bash
uv run server.py
```

### Install editable

```bash
uv pip install -e .
```

This registers the `jelly-mcp` command.

## Claude Desktop example

To use this with Claude Desktop (or other MCP hosts), add the following configuration. 

Using `sh -c` allows the use of `$HOME` (or other environment variables) dynamically across different user machines/setups, since most MCP hosts do not perform shell expansion on paths:

```json
{
  "mcpServers": {
    "LetsJelly": {
      "command": "sh",
      "args": [
        "-c",
        "uv --directory \"$HOME/.agents/Jelly-FastMCP\" run server.py"
      ],
      "env": {
        "JELLY_API_TOKEN": "your-api-token-here"
      }
    }
  }
}
```

*Note: If you prefer not to use `sh -c`, replace `"command"` with `"uv"` and use the absolute path in the `"--directory"` argument.*

## Available tools

### Conversations
- `list_conversations`
- `search_conversations`
- `get_conversation`
- `list_conversation_messages`
- `list_conversation_comments`
- `add_comment`
- `archive_conversation` / `unarchive_conversation`
- `trash_conversation` / `restore_conversation_from_trash`
- `spam_conversation` / `unspam_conversation`
- `snooze_conversation` / `unsnooze_conversation`
- `ignore_conversation`
- `set_conversation_mailboxes`
- `assign_conversation` / `unassign_conversation`
- `add_conversation_label` / `remove_conversation_label`

### Messages and drafts
- `get_message`
- `create_draft_conversation`
- `create_draft_reply`
- `update_draft`
- `resolve_attachment_download_url`

### Labels, members, and mailboxes
- `list_labels`
- `create_label`
- `update_label`
- `delete_label`
- `list_members`
- `list_mailboxes`
- `list_mailbox_members`

### Contacts and settings
- `find_contact_by_email`
- `upsert_contact`
- `get_autoresponder`
- `update_autoresponder`
- `list_saved_replies`

## Resources

- `jelly://conversations/{conversation_id}/markdown` — LLM-friendly markdown view of a conversation
