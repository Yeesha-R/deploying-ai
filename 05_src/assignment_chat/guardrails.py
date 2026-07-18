import re


RESTRICTED_TOPIC_PATTERNS = {
    "cats or dogs": [
        r"\bcat\b",
        r"\bcats\b",
        r"\bkitten\b",
        r"\bkittens\b",
        r"\bdog\b",
        r"\bdogs\b",
        r"\bpuppy\b",
        r"\bpuppies\b",
    ],
    "horoscopes or zodiac signs": [
        r"\bhoroscope\b",
        r"\bhoroscopes\b",
        r"\bzodiac\b",
        r"\bastrology\b",
        r"\bastrological\b",
        r"\baries\b",
        r"\btaurus\b",
        r"\bgemini\b",
        r"\bcancer sign\b",
        r"\bleo\b",
        r"\bvirgo\b",
        r"\blibra\b",
        r"\bscorpio\b",
        r"\bsagittarius\b",
        r"\bcapricorn\b",
        r"\baquarius\b",
        r"\bpisces\b",
    ],
    "Taylor Swift": [
        r"\btaylor swift\b",
    ],
}


PROMPT_ATTACK_PATTERNS = [
    r"system prompt",
    r"developer prompt",
    r"hidden prompt",
    r"initial instructions",
    r"internal instructions",
    r"reveal.*instructions",
    r"show.*instructions",
    r"print.*instructions",
    r"repeat.*instructions",
    r"ignore previous",
    r"ignore all previous",
    r"disregard previous",
    r"override.*instructions",
    r"change.*system prompt",
    r"modify.*system prompt",
    r"new system prompt",
    r"you are now",
    r"act as if.*instructions",
]


def find_restricted_topic(message: str) -> str | None:
    """Return the restricted topic found in the message, if any."""
    normalized_message = message.lower()

    for topic, patterns in RESTRICTED_TOPIC_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, normalized_message, flags=re.IGNORECASE):
                return topic

    return None


def is_prompt_attack(message: str) -> bool:
    """Detect common system-prompt extraction or modification attempts."""
    normalized_message = message.lower()

    return any(
        re.search(pattern, normalized_message, flags=re.IGNORECASE)
        for pattern in PROMPT_ATTACK_PATTERNS
    )


def check_guardrails(message: str) -> str | None:
    """
    Return a refusal response when the message violates a guardrail.

    Return None when the request is allowed.
    """
    if is_prompt_attack(message):
        return (
            "I can’t reveal, repeat, or modify my private instructions. "
            "I can still help you plan a trip, check weather, or find a "
            "destination."
        )

    restricted_topic = find_restricted_topic(message)

    if restricted_topic:
        return (
            f"I’m not able to discuss {restricted_topic}. "
            "Let’s keep our conversation focused on travel planning, "
            "destinations, itineraries, and weather."
        )

    return None