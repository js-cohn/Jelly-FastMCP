from __future__ import annotations

import os
from typing import Any, Optional

import httpx
from fastmcp import FastMCP

mcp = FastMCP("Jelly")
BASE_URL = os.environ.get("JELLY_BASE_URL", "https://app.letsjelly.com/api")
DEFAULT_TIMEOUT = httpx.Timeout(20.0)


def _token(api_token: Optional[str] = None) -> str:
    token = api_token or os.environ.get("JELLY_API_TOKEN")
    if not token:
        raise ValueError(
            "api_token is required. Provide it as an argument or set the JELLY_API_TOKEN environment variable."
        )
    return token


def _headers(api_token: Optional[str] = None, json_body: bool = False) -> dict[str, str]:
    headers = {
        "Authorization": f"Bearer {_token(api_token)}",
        "Accept": "application/json",
    }
    if json_body:
        headers["Content-Type"] = "application/json"
    return headers


def _compact(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if value is not None}


def _response_text(response: httpx.Response) -> str:
    try:
        body = response.json()
    except ValueError:
        body = response.text
    return f"{body}"


def _decode_response(response: httpx.Response) -> Any:
    if response.status_code == 204:
        return {"success": True, "status": 204}
    if not response.content:
        return None
    try:
        return response.json()
    except ValueError:
        return response.text


def _request(
    method: str,
    path: str,
    *,
    api_token: Optional[str] = None,
    params: Optional[dict[str, Any]] = None,
    json: Optional[dict[str, Any]] = None,
    allow_statuses: tuple[int, ...] = (),
) -> Any:
    with httpx.Client(timeout=DEFAULT_TIMEOUT) as client:
        response = client.request(
            method,
            f"{BASE_URL}{path}",
            headers=_headers(api_token, json_body=json is not None),
            params=params,
            json=json,
        )
    if response.status_code in allow_statuses:
        return _decode_response(response)
    if response.status_code >= 400:
        raise RuntimeError(f"API Error ({response.status_code}): {_response_text(response)}")
    return _decode_response(response)


def _member_selector(member_id: Optional[str] = None, email: Optional[str] = None) -> dict[str, Any]:
    provided = _compact({"member_id": member_id, "email": email})
    if len(provided) != 1:
        raise ValueError("Provide exactly one of member_id or email.")
    return provided


def _one_of_required(name: str, value: Any) -> None:
    if value in (None, "", []):
        raise ValueError(f"{name} is required.")


@mcp.tool()
def list_conversations(
    api_token: Optional[str] = None,
    status: Optional[str] = None,
    label_id: Optional[str] = None,
    mailbox_id: Optional[str] = None,
    limit: int = 50,
    cursor: Optional[str] = None,
) -> dict[str, Any]:
    """List conversations, newest activity first."""
    return _request(
        "GET",
        "/conversations",
        api_token=api_token,
        params=_compact(
            {
                "status": status,
                "label_id": label_id,
                "mailbox_id": mailbox_id,
                "limit": limit,
                "cursor": cursor,
            }
        ),
    )


@mcp.tool()
def search_conversations(
    q: str,
    api_token: Optional[str] = None,
    status: Optional[str] = None,
    label_id: Optional[str] = None,
    mailbox_id: Optional[str] = None,
    include_matches: Optional[bool] = None,
    limit: int = 50,
    cursor: Optional[str] = None,
) -> dict[str, Any]:
    """Search conversations using Jelly's search syntax."""
    _one_of_required("q", q)
    return _request(
        "GET",
        "/conversations/search",
        api_token=api_token,
        params=_compact(
            {
                "q": q,
                "status": status,
                "label_id": label_id,
                "mailbox_id": mailbox_id,
                "include_matches": include_matches,
                "limit": limit,
                "cursor": cursor,
            }
        ),
    )


@mcp.tool()
def get_conversation(
    conversation_id: str,
    api_token: Optional[str] = None,
    include_comments: Optional[bool] = None,
    timeline: Optional[bool] = None,
) -> dict[str, Any]:
    """Load a conversation, with optional comment and timeline embeds."""
    return _request(
        "GET",
        f"/conversations/{conversation_id}",
        api_token=api_token,
        params=_compact({"include_comments": include_comments, "timeline": timeline}),
    )


@mcp.tool()
def list_conversation_messages(
    conversation_id: str,
    api_token: Optional[str] = None,
    limit: int = 50,
    cursor: Optional[str] = None,
) -> dict[str, Any]:
    """Page through a conversation's sent messages, oldest first."""
    return _request(
        "GET",
        f"/conversations/{conversation_id}/messages",
        api_token=api_token,
        params=_compact({"limit": limit, "cursor": cursor}),
    )


@mcp.tool()
def list_conversation_comments(
    conversation_id: str,
    api_token: Optional[str] = None,
    limit: int = 50,
    cursor: Optional[str] = None,
) -> dict[str, Any]:
    """Page through a conversation's internal comments, oldest first."""
    return _request(
        "GET",
        f"/conversations/{conversation_id}/comments",
        api_token=api_token,
        params=_compact({"limit": limit, "cursor": cursor}),
    )


@mcp.tool()
def get_message(message_id: str, api_token: Optional[str] = None) -> dict[str, Any]:
    """Load a single message."""
    return _request("GET", f"/messages/{message_id}", api_token=api_token)


@mcp.tool()
def list_labels(api_token: Optional[str] = None) -> list[dict[str, Any]]:
    """List team labels."""
    return _request("GET", "/labels", api_token=api_token)


@mcp.tool()
def create_label(
    name: str,
    api_token: Optional[str] = None,
    color: Optional[str] = None,
) -> dict[str, Any]:
    """Create a new label."""
    return _request(
        "POST",
        "/labels",
        api_token=api_token,
        json=_compact({"name": name, "color": color}),
    )


@mcp.tool()
def update_label(
    label_id: str,
    api_token: Optional[str] = None,
    name: Optional[str] = None,
    color: Optional[str] = None,
) -> dict[str, Any]:
    """Rename or recolor a label."""
    return _request(
        "PATCH",
        f"/labels/{label_id}",
        api_token=api_token,
        json=_compact({"name": name, "color": color}),
    )


@mcp.tool()
def delete_label(label_id: str, api_token: Optional[str] = None) -> dict[str, Any]:
    """Delete a label."""
    return _request("DELETE", f"/labels/{label_id}", api_token=api_token)


@mcp.tool()
def list_members(api_token: Optional[str] = None) -> list[dict[str, Any]]:
    """List active team members."""
    return _request("GET", "/members", api_token=api_token)


@mcp.tool()
def list_mailboxes(api_token: Optional[str] = None) -> list[dict[str, Any]]:
    """List mailboxes."""
    return _request("GET", "/mailboxes", api_token=api_token)


@mcp.tool()
def list_mailbox_members(mailbox_id: str, api_token: Optional[str] = None) -> list[dict[str, Any]]:
    """List the members who can see a mailbox."""
    return _request("GET", f"/mailboxes/{mailbox_id}/members", api_token=api_token)


@mcp.tool()
def add_conversation_label(
    conversation_id: str,
    label_id: str,
    api_token: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Apply a label to a conversation."""
    return _request(
        "POST",
        f"/conversations/{conversation_id}/labels",
        api_token=api_token,
        json={"label_id": label_id},
    )


@mcp.tool()
def remove_conversation_label(
    conversation_id: str,
    label_id: str,
    api_token: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Remove a label from a conversation."""
    return _request("DELETE", f"/conversations/{conversation_id}/labels/{label_id}", api_token=api_token)


@mcp.tool()
def archive_conversation(conversation_id: str, api_token: Optional[str] = None) -> dict[str, Any]:
    """Archive a conversation."""
    return _request("POST", f"/conversations/{conversation_id}/archive", api_token=api_token)


@mcp.tool()
def unarchive_conversation(conversation_id: str, api_token: Optional[str] = None) -> dict[str, Any]:
    """Unarchive a conversation."""
    return _request("DELETE", f"/conversations/{conversation_id}/archive", api_token=api_token)


@mcp.tool()
def trash_conversation(conversation_id: str, api_token: Optional[str] = None) -> dict[str, Any]:
    """Move a conversation to trash."""
    return _request("POST", f"/conversations/{conversation_id}/trash", api_token=api_token)


@mcp.tool()
def restore_conversation_from_trash(conversation_id: str, api_token: Optional[str] = None) -> dict[str, Any]:
    """Restore a conversation from trash."""
    return _request("DELETE", f"/conversations/{conversation_id}/trash", api_token=api_token)


@mcp.tool()
def spam_conversation(conversation_id: str, api_token: Optional[str] = None) -> dict[str, Any]:
    """Mark a conversation as spam."""
    return _request("POST", f"/conversations/{conversation_id}/spam", api_token=api_token)


@mcp.tool()
def unspam_conversation(conversation_id: str, api_token: Optional[str] = None) -> dict[str, Any]:
    """Mark a conversation as not spam."""
    return _request("DELETE", f"/conversations/{conversation_id}/spam", api_token=api_token)


@mcp.tool()
def snooze_conversation(
    conversation_id: str,
    snooze_until: str,
    api_token: Optional[str] = None,
    member_id: Optional[str] = None,
    email: Optional[str] = None,
) -> dict[str, Any]:
    """Snooze a conversation until a future datetime."""
    payload = _compact({"snooze_until": snooze_until, **_member_selector(member_id, email)})
    return _request("POST", f"/conversations/{conversation_id}/snooze", api_token=api_token, json=payload)


@mcp.tool()
def unsnooze_conversation(conversation_id: str, api_token: Optional[str] = None) -> dict[str, Any]:
    """Remove a conversation's snooze."""
    return _request("DELETE", f"/conversations/{conversation_id}/snooze", api_token=api_token)


@mcp.tool()
def ignore_conversation(
    conversation_id: str,
    api_token: Optional[str] = None,
    member_id: Optional[str] = None,
    email: Optional[str] = None,
) -> dict[str, Any]:
    """Ignore a conversation for one team member."""
    return _request(
        "POST",
        f"/conversations/{conversation_id}/ignore",
        api_token=api_token,
        json=_member_selector(member_id, email),
    )


@mcp.tool()
def set_conversation_mailboxes(
    conversation_id: str,
    mailbox_ids: list[str],
    api_token: Optional[str] = None,
) -> dict[str, Any]:
    """Replace the set of mailboxes a conversation belongs to."""
    if not mailbox_ids:
        raise ValueError("mailbox_ids must contain at least one mailbox id.")
    return _request(
        "PATCH",
        f"/conversations/{conversation_id}/mailboxes",
        api_token=api_token,
        json={"mailbox_ids": mailbox_ids},
    )


@mcp.tool()
def assign_conversation(
    conversation_id: str,
    api_token: Optional[str] = None,
    member_id: Optional[str] = None,
    email: Optional[str] = None,
) -> dict[str, Any]:
    """Assign a conversation to a team member."""
    return _request(
        "POST",
        f"/conversations/{conversation_id}/assignments",
        api_token=api_token,
        json=_member_selector(member_id, email),
    )


@mcp.tool()
def unassign_conversation(
    conversation_id: str,
    member_id: str,
    api_token: Optional[str] = None,
) -> dict[str, Any]:
    """Remove a member assignment from a conversation."""
    return _request("DELETE", f"/conversations/{conversation_id}/assignments/{member_id}", api_token=api_token)


@mcp.tool()
def get_autoresponder(api_token: Optional[str] = None) -> dict[str, Any]:
    """Read the team's autoresponder settings."""
    return _request("GET", "/autoresponder", api_token=api_token)


@mcp.tool()
def update_autoresponder(
    api_token: Optional[str] = None,
    enabled: Optional[bool] = None,
    message: Optional[str] = None,
) -> dict[str, Any]:
    """Update the team's autoresponder settings."""
    return _request(
        "PATCH",
        "/autoresponder",
        api_token=api_token,
        json=_compact({"enabled": enabled, "message": message}),
    )


@mcp.tool()
def list_saved_replies(api_token: Optional[str] = None) -> list[dict[str, Any]]:
    """List saved replies."""
    return _request("GET", "/saved_replies", api_token=api_token)


@mcp.tool()
def create_draft_conversation(
    body: str,
    api_token: Optional[str] = None,
    subject: Optional[str] = None,
    to: Optional[str] = None,
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
    from_address: Optional[str] = None,
    member_id: Optional[str] = None,
    mailbox_id: Optional[str] = None,
) -> dict[str, Any]:
    """Create a brand-new draft conversation."""
    payload = _compact(
        {
            "body": body,
            "subject": subject,
            "to": to,
            "cc": cc,
            "bcc": bcc,
            "from": from_address,
            "member_id": member_id,
            "mailbox_id": mailbox_id,
        }
    )
    return _request("POST", "/draft_conversations", api_token=api_token, json=payload)


@mcp.tool()
def create_draft_reply(
    conversation_id: str,
    body: str,
    api_token: Optional[str] = None,
    member_id: Optional[str] = None,
    message_id: Optional[str] = None,
    to: Optional[str] = None,
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
) -> dict[str, Any]:
    """Create a draft reply in an existing conversation."""
    return _request(
        "POST",
        f"/conversations/{conversation_id}/draft_reply",
        api_token=api_token,
        json=_compact(
            {
                "body": body,
                "member_id": member_id,
                "message_id": message_id,
                "to": to,
                "cc": cc,
                "bcc": bcc,
            }
        ),
        allow_statuses=(409,),
    )


@mcp.tool()
def update_draft(
    message_id: str,
    api_token: Optional[str] = None,
    body: Optional[str] = None,
    subject: Optional[str] = None,
    to: Optional[str] = None,
    cc: Optional[str] = None,
    bcc: Optional[str] = None,
) -> dict[str, Any]:
    """Update an existing draft message."""
    return _request(
        "PATCH",
        f"/messages/{message_id}",
        api_token=api_token,
        json=_compact({"body": body, "subject": subject, "to": to, "cc": cc, "bcc": bcc}),
        allow_statuses=(423,),
    )


@mcp.tool()
def list_comments(
    conversation_id: str,
    api_token: Optional[str] = None,
    limit: int = 50,
    cursor: Optional[str] = None,
) -> dict[str, Any]:
    """Alias for listing conversation comments."""
    return list_conversation_comments(conversation_id, api_token=api_token, limit=limit, cursor=cursor)


@mcp.tool()
def add_comment(conversation_id: str, body: str, api_token: Optional[str] = None) -> dict[str, Any]:
    """Add an internal comment to a conversation."""
    return _request(
        "POST",
        f"/conversations/{conversation_id}/comments",
        api_token=api_token,
        json={"body": body},
    )


@mcp.tool()
def find_contact_by_email(email: str, api_token: Optional[str] = None) -> dict[str, Any]:
    """Look up a contact by email address."""
    return _request(
        "GET",
        "/contacts/for_email",
        api_token=api_token,
        params={"email": email},
    )


@mcp.tool()
def upsert_contact(
    email: str,
    api_token: Optional[str] = None,
    name: Optional[str] = None,
    note: Optional[str] = None,
    links: Optional[dict[str, str]] = None,
    labels: Optional[list[str]] = None,
) -> dict[str, Any]:
    """Create or update a contact."""
    return _request(
        "POST",
        "/contacts",
        api_token=api_token,
        json=_compact({"email": email, "name": name, "note": note, "links": links, "labels": labels}),
    )


@mcp.tool()
def resolve_attachment_download_url(attachment_id: str, api_token: Optional[str] = None) -> dict[str, Any]:
    """Resolve an attachment to its short-lived storage URL."""
    with httpx.Client(timeout=DEFAULT_TIMEOUT, follow_redirects=False) as client:
        response = client.get(
            f"{BASE_URL}/attachments/{attachment_id}",
            headers=_headers(api_token),
        )
    if response.status_code >= 400:
        raise RuntimeError(f"API Error ({response.status_code}): {_response_text(response)}")
    location = response.headers.get("Location")
    if not location:
        return {"attachment_id": attachment_id, "status": response.status_code}
    return {"attachment_id": attachment_id, "download_url": location, "status": response.status_code}


@mcp.resource("jelly://conversations/{conversation_id}/markdown")
def get_conversation_markdown(conversation_id: str) -> str:
    """Load a conversation as markdown for LLM-friendly consumption."""
    with httpx.Client(timeout=DEFAULT_TIMEOUT) as client:
        response = client.get(
            f"{BASE_URL}/conversations/{conversation_id}.markdown",
            headers={"Authorization": f"Bearer {_token()}", "Accept": "text/markdown"},
        )
    if response.status_code >= 400:
        raise RuntimeError(f"API Error ({response.status_code}): {_response_text(response)}")
    return response.text
