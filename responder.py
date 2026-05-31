"""
Core logic: escalation detection, Claude API call, and response logging.
"""

import json
import os
from datetime import datetime
from pathlib import Path

import anthropic

from config import (
    ESCALATION_KEYWORDS,
    LOGS_DIR,
    MAX_TOKENS,
    MODEL,
    RESPONSE_LOG,
    SYSTEM_PROMPT,
)


# ── Data model ────────────────────────────────────────────────────────────────

class IncomingMessage:
    """Represents a single message arriving from any social platform."""

    def __init__(self, platform: str, sender: str, text: str):
        self.platform  = platform          # e.g. "Facebook"
        self.sender    = sender            # display name or user ID
        self.text      = text.strip()
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "platform":  self.platform,
            "sender":    self.sender,
            "text":      self.text,
            "timestamp": self.timestamp,
        }


class ResponseResult:
    """Holds the outcome of processing one message."""

    ESCALATE = "ESCALATE"
    AUTO     = "AUTO"

    def __init__(
        self,
        message:        IncomingMessage,
        status:         str,
        reply:          str,
        escalation_hit: str | None = None,
    ):
        self.message        = message
        self.status         = status         # "AUTO" or "ESCALATE"
        self.reply          = reply
        self.escalation_hit = escalation_hit # which keyword triggered escalation

    def to_dict(self) -> dict:
        return {
            "message":        self.message.to_dict(),
            "status":         self.status,
            "reply":          self.reply,
            "escalation_hit": self.escalation_hit,
            "processed_at":   datetime.now().isoformat(),
        }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_system_prompt() -> str:
    """Read the system prompt from disk; raise a clear error if missing."""
    if not SYSTEM_PROMPT.exists():
        raise FileNotFoundError(
            f"System prompt not found at {SYSTEM_PROMPT}. "
            "Create the file or check your PROMPTS_DIR setting."
        )
    return SYSTEM_PROMPT.read_text(encoding="utf-8").strip()


def _check_escalation(text: str) -> str | None:
    """
    Return the first escalation keyword found in `text`, or None.
    Matching is case-insensitive and checks whole words to avoid false positives.
    """
    lower = text.lower()
    for keyword in ESCALATION_KEYWORDS:
        if keyword in lower:
            return keyword
    return None


def _append_log(result: ResponseResult) -> None:
    """Append the result dict to the JSON log file (creates it if needed)."""
    LOGS_DIR.mkdir(exist_ok=True)

    # Load existing log array, or start fresh
    if RESPONSE_LOG.exists():
        try:
            data = json.loads(RESPONSE_LOG.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = []
    else:
        data = []

    data.append(result.to_dict())
    RESPONSE_LOG.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ── Main processing function ──────────────────────────────────────────────────

def process_message(
    message: IncomingMessage,
    client:  anthropic.Anthropic,
) -> ResponseResult:
    """
    Process one incoming message:
      1. Check for escalation keywords.
      2. If clean, call Claude to generate a Dutch reply.
      3. Log the result and return it.
    """

    # ── Step 1: Escalation check ─────────────────────────────────────────────
    hit = _check_escalation(message.text)
    if hit:
        reply = (
            f"!! ESCALATE TO HUMAN\n"
            f"Reden: bericht bevat gevoelig trefwoord: '{hit}'\n"
            f"Platform: {message.platform} | Afzender: {message.sender}"
        )
        result = ResponseResult(
            message        = message,
            status         = ResponseResult.ESCALATE,
            reply          = reply,
            escalation_hit = hit,
        )
        _append_log(result)
        return result

    # ── Step 2: Call Claude ───────────────────────────────────────────────────
    system_prompt = _load_system_prompt()

    # Build the user turn: include platform context so the model can adapt
    user_content = (
        f"[Platform: {message.platform}] [Afzender: {message.sender}]\n\n"
        f"{message.text}"
    )

    api_response = client.messages.create(
        model      = MODEL,
        max_tokens = MAX_TOKENS,
        system     = system_prompt,
        messages   = [{"role": "user", "content": user_content}],
    )

    reply = api_response.content[0].text.strip()

    # ── Step 3: Log & return ─────────────────────────────────────────────────
    result = ResponseResult(
        message = message,
        status  = ResponseResult.AUTO,
        reply   = reply,
    )
    _append_log(result)
    return result


# ── Batch helper ──────────────────────────────────────────────────────────────

def process_batch(
    messages: list[IncomingMessage],
    client:   anthropic.Anthropic,
) -> list[ResponseResult]:
    """Process a list of messages and return all results."""
    return [process_message(msg, client) for msg in messages]
