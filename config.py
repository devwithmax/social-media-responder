"""
Configuration — all tuneable settings in one place.
"""

from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR        = Path(__file__).parent
PROMPTS_DIR     = BASE_DIR / "prompts"
LOGS_DIR        = BASE_DIR / "logs"
SYSTEM_PROMPT   = PROMPTS_DIR / "system_prompt.txt"
RESPONSE_LOG    = LOGS_DIR / "responses.json"

# ── Claude model ──────────────────────────────────────────────────────────────
MODEL           = "claude-haiku-4-5-20251001"   # fast & cost-effective
MAX_TOKENS      = 512

# ── Escalation ────────────────────────────────────────────────────────────────
# Any message containing one of these words (case-insensitive) is flagged
# instead of being auto-answered.
ESCALATION_KEYWORDS = [
    "klacht",
    "klachten",
    "juridisch",
    "advocaat",
    "rechtbank",
    "terugbetaling",
    "terugstorten",
    "refund",
    "dringend",
    "urgent",
    "bedreig",
    "aangifte",
    "schandaal",
    "fraude",
]

# ── Simulated platforms ───────────────────────────────────────────────────────
PLATFORMS = ["Facebook", "Instagram", "WhatsApp"]
