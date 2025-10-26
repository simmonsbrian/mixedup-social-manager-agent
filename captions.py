import os, re, random
from typing import Dict, List, Tuple, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

CORE_HASHTAGS = ["#MixedUpBand", "#CherokeeGA", "#WoodstockGA", "#LiveMusic", "#CoverBand", "#GeorgiaMusic"]
ARTIST_TAGS = {
    "Genesis": "#Genesis",
    "Phil Collins": "#PhilCollins",
    "Coldplay": "#Coldplay",
    "Blink-182": "#Blink182",
    "Toto": "#Toto",
}

STYLE_RULES = {"max_chars": 180, "no_em_dashes": True, "no_alcohol": True}

def _truncate(text: str, max_chars: int) -> str:
    return text if len(text) <= max_chars else text[:max_chars-1].rstrip() + "…"

def _sanitize(text: str) -> str:
    if STYLE_RULES["no_em_dashes"]:
        text = text.replace("—", "-")
    if STYLE_RULES["no_alcohol"]:
        text = re.sub(r"\b(beer|wine|whiskey|bourbon|vodka|tequila|alcohol)\b", "drink", text, flags=re.I)
    return text.strip()

def _local_caption(post_type: str, ctx: Dict) -> str:
    city = ctx.get("city", "Woodstock")
    if post_type.lower() == "gig teaser":
        base = f"Show vibes loading in {city}. What should we open with?"
    elif post_type.lower() == "behind the scenes":
        base = "Rehearsal night. Coffee, cables, and a metronome that never blinks."
    elif post_type.lower() == "throwback clip":
        base = "Throwback to the last set. Crowd was loud and the groove locked in."
    elif post_type.lower() == "poll":
        base = f"Help us choose the closer: {ctx.get('poll_a','Genesis')} or {ctx.get('poll_b','Coldplay')}?"
    elif post_type.lower() == "micro-lesson":
        base = "Bass tip of the week: keep the right hand light and let the drummer breathe."
    elif post_type.lower() == "setlist snapshot":
        base = "This week’s setlist is shaping up. Any requests to add next time?"
    elif post_type.lower() == "fan shoutout":
        base = "Shoutout to everyone who packed the patio last time. We heard you from the stage."
    else:
        base = f"{post_type}."
    return _sanitize(_truncate(base, STYLE_RULES["max_chars"]))

def _compose_hashtags(ctx: Dict) -> List[str]:
    tags = CORE_HASHTAGS.copy()
    text = " ".join([str(v) for v in ctx.values() if isinstance(v, str)])
    for k, tag in ARTIST_TAGS.items():
        if k.lower() in text.lower():
            tags.append(tag)
    seen, out = set(), []
    for t in tags:
        if t not in seen:
            seen.add(t); out.append(t)
    return out[:10]

def _openai_complete(prompt: str) -> Optional[str]:
    import requests
    if not OPENAI_API_KEY:
        return None
    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type":"application/json"},
            json={
                "model": OPENAI_MODEL,
                "messages": [
                    {"role":"system","content":"You write short, clean social captions for a local cover band. No em dashes, no alcohol references."},
                    {"role":"user","content": prompt}
                ],
                "temperature":0.7,
                "max_tokens":120
            },
            timeout=20
        )
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return None

def generate_caption_and_tags(post_type: str, context: Dict, mode: str = "auto") -> Tuple[str, List[str], str]:
    ctx = context or {}
    caption, source = None, "LOCAL"
    if mode in ("auto","ai") and OPENAI_API_KEY:
        prompt = (
            f"Post type: {post_type}\n"
            f"City: {ctx.get('city','Woodstock')}\n"
            f"Venue: {ctx.get('venue','MadLife')}\n"
            f"Details: {ctx.get('details','')}\n"
            f"Artist hint: {ctx.get('artist','')}\n\n"
            "Write a 1–2 sentence caption, <=180 characters, friendly, clean, no em dashes, no alcohol references. "
            "If teaser, ask 1 short question. Return only the caption."
        )
        ai = _openai_complete(prompt)
        if ai:
            caption = _sanitize(_truncate(ai, STYLE_RULES["max_chars"])); source = "AI"
    if not caption:
        caption = _local_caption(post_type, ctx); source = "LOCAL"
    tags = _compose_hashtags(ctx)
    return caption, tags, source
