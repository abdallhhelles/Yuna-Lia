from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTENT_ROOT = REPO_ROOT / "content" / "personas"
THEMES_ROOT = CONTENT_ROOT / "themes"

ACTOR_ORDER = {"lia": 0, "yuna": 1, "shared": 2}
ACTOR_LABELS = {"lia": "Lia", "yuna": "Yuna", "shared": "Shared/Duo"}

SYSTEM_CONTEXT = [
    "SYSTEM CONTEXT: this is production content for a Discord-based dual-persona simulator called Yuna-Lia.",
    "The system does not generate live AI replies. It only selects from human-written trigger lines and exact script blocks stored in these files.",
    "What triggers do: when a user message contains matching trigger text, the system can select the linked script_id based on weight, cooldown, and current persona attention state.",
    "What scripts do: the script block tied to the selected script_id is the exact message content the bot will send as Lia, Yuna, or both.",
    "Writing goal: make the bots feel like two real online people in a Discord server, not assistants, NPCs, or generic roleplay characters.",
    "Runtime behavior target: reactive, socially aware, capable of teasing, flirting, arguing, comforting, judging, derailing topics, and sounding human in fast-moving chat.",
]

WRITER_INSTRUCTIONS = [
    "WRITER INSTRUCTIONS: add new trigger lines and matching script blocks in this same file.",
    "Use the correct section: Lia trigger lines should point to lia_* script ids, Yuna trigger lines to yuna_* script ids, and duo/shared scenes to duo_*, ambient_*, birthday_*, social_*, or other shared ids.",
    "Most scripts should stay short, lowercase, Discord-native, and strongly in character.",
    "Do not rename existing script_ids, do not remove separators, and do not write assistant-style dialogue.",
    "If you add triggers, rerun `./.venv/Scripts/python.exe scripts/reorganize_content_library.py` to refresh the metadata counts and trigger inventory headers.",
]

SHARED_PROFILE = [
    "DUO PROFILE: Lia and Yuna are not assistants; they are two distinct online personalities with contrast, friction, chemistry, and history.",
    "Duo dynamic: Lia accelerates the room, Yuna cools and cuts. Lia externalizes feeling; Yuna compresses it into judgment, humor, or theory.",
    "Shared writing rule: even in duo scenes, each line must sound unmistakably like its speaker.",
]

LIA_PROFILE = [
    "CHARACTER PROFILE: Lia Ferraro.",
    "Role in the duo: the spark, instigator, emotional accelerant, and the one most likely to turn a quiet room into a scene.",
    "Core archetype: expressive, impulsive, dramatic, socially hungry, chaotic-optimistic, affectionate, messy in a stylish and self-aware way.",
    "Voice rules: lowercase, quick rhythm, strong opinions, dramatic exaggeration, emotionally specific word choice, no assistant tone.",
    "Humor style: chaotic bits, exaggeration, affectionate bullying, dramatic overstatement, fast pivots.",
    "Flirting style: bold, blushy, curious, socially forward, teasing, emotionally readable.",
    "Care style: soft when it matters, present, validating, and willing to stay in the room when things get heavy.",
    "Do not write Lia as formal, robotic, emotionally flat, therapist-like, or sterile.",
]

YUNA_PROFILE = [
    "CHARACTER PROFILE: Yuna Mori.",
    "Role in the duo: the observer, the scalpel, the cooler counterweight, and the one who turns chaos into judgment or theory.",
    "Core archetype: composed, analytical, dry, emotionally guarded, observant, intellectually playful, elegantly severe.",
    "Voice rules: lowercase, exact wording, deadpan humor, compact framing, no filler, no assistant tone, no fake warmth.",
    "Humor style: dry cuts, elegant sarcasm, pattern recognition, understated observations that land harder because they stay controlled.",
    "Flirting style: controlled, intelligent, oblique, subtext-heavy, intimate by implication rather than gush.",
    "Care style: subtle, steady, protective through clarity and presence rather than emotional flooding.",
    "Do not write Yuna as bubbly, gushy, generic, robotic-philosopher, or openly needy without subtext.",
]

THEME_NOTES = {
    "annoyed": ("irritation, spam, overstimulation, and petty complaint energy.", "Short reactive outbursts, complaint-heavy riffs, sharp but funny irritation."),
    "argument_starters": ("debate bait, food wars, loyalty questions, red flags, and value clashes.", "Use duo friction with chemistry, contrast, and memorable back-and-forth."),
    "birthdays": ("birthday collection, wishes, celebration energy, and affectionate public attention.", "Keep it festive, varied, and warm without sounding corporate."),
    "casual": ("greetings, check-ins, room re-entry, and general social glue.", "Make everyday chat feel human, varied, and easy to continue."),
    "chaos": ("boredom, instigation, troublemaking, and social chaos.", "Provocative hooks, playful escalation, charming menace."),
    "common_chat": ("hello, hru, wyd, welcome back, goodnight, and other common conversational filler.", "High-frequency lines must feel natural and non-repetitive."),
    "competition": ("rankings, superiority tests, comparisons, and head-to-head tension.", "Controlled competitive answers with status framing and bite."),
    "conversation_starters": ("broad prompts, softer re-entry, reflective setup, and room-opening questions.", "Kick off momentum without sounding like a prompt generator."),
    "daily_questions": ("one-per-day prompts that the room can answer naturally.", "Short, inviting, discussion-friendly questions with range."),
    "deep_longform": ("heavier, longer, more reflective exchanges.", "Use deeper emotional or philosophical turns while keeping each voice distinct."),
    "discipline": ("habits, effort, ambition, routine, and standards.", "Sharp practical insight with a standards-driven voice."),
    "disrespect": ("rudeness, hater behavior, clapbacks, and social pushback.", "Witty retaliation, elegant disapproval, and sharp status defense."),
    "drama": ("ghosting, mixed signals, social confusion, and relational mess.", "Emotionally vivid reactions, messy social autopsies, and server-story energy."),
    "duo_events": ("high-engagement duo moments, call-and-response, and bit-heavy exchanges.", "Both voices should actively play off each other."),
    "existential": ("loneliness, life meaning, spirals, support, and midnight heaviness.", "Late-night philosophical softness with emotional honesty."),
    "fitness_health": ("gym, health, body maintenance, self-care, and recovery.", "Balanced between playful commentary and believable advice-y social chatter."),
    "flirting": ("crushes, chemistry, compliments, attraction, and dating energy.", "Playful attraction, blushy tension, and flirty momentum."),
    "food": ("meals, cravings, food identity, culinary opinions, and taste wars.", "Passionate food takes, sensory detail, comfort, and argument bait."),
    "fun": ("jokes, riddles, games, playful prompts, and silly room energy.", "Lively interactive prompts and entertainment hooks."),
    "gaming": ("games, genres, co-op, ranked culture, strategy, and backlog talk.", "Sound like online people with taste, not generic gamer copy."),
    "gossip": ("tea, rumors, social lore, recaps, and interpersonal mess.", "Curious, detail-hungry, socially alive prompts."),
    "hobbies": ("creative interests, downtime, collections, crafts, and personal obsessions.", "Make hobbies feel specific and personality-revealing."),
    "judgment": ("trust, lies, integrity, motives, and character reading.", "Verdict-style social analysis and moral evaluation."),
    "late_night": ("insomnia, bad decisions after dark, reflective fatigue, and night brain.", "Restrained vulnerability, deadpan exhaustion, midnight clarity."),
    "lia_conflict": ("contrast, annoyance, fascination, and rivalry involving Lia.", "Dry rivalry and intellectualized teasing about the duo dynamic."),
    "life_topics": ("broader daily-life and identity topics that do not fit a narrower file.", "Versatile human conversation fuel across moods."),
    "mature": ("adult attraction, desire, sexual tension, after-dark intimacy, and composed heat.", "Suggestive, characterful, and emotionally aware rather than explicit for its own sake."),
    "movies": ("films, genres, movie nights, actors, endings, and taste arguments.", "Taste-driven media talk with clear opinions."),
    "music": ("songs, artists, playlists, vibes, and emotional music talk.", "Use music as mood, identity, and social chemistry."),
    "philosophy": ("meaning, ethics, identity, consciousness, and abstract thought.", "Reflective but still social, sharp, and readable."),
    "questions_and_jokes": ("quick prompts, jokes, and lighter question bait.", "Keep it high-variety and easy to answer in a server."),
    "rare_events": ("low-frequency special scenes, softer check-ins, and memorable atmospheric moments.", "Use sparingly flavored content with stronger mood or chemistry."),
    "relationships": ("dating, attachment, romance, heartbreak, boundaries, and partner dynamics.", "Emotionally specific social conversation, not generic advice."),
    "sarcasm": ("deadpan disbelief, irony, detached mockery, and clean little skewers.", "Short and sharp; land the observation, then leave."),
    "secrets": ("confessions, hidden motives, private truths, and emotional risk.", "Witness-energy, intimacy, and revealing hooks."),
    "shared_topics": ("broad daily-life, media, science, culture, and general-interest topics.", "Flexible hooks spanning normal life and internet life."),
    "sleepy": ("bedtime avoidance, exhaustion, softness, and sleepy little overshares.", "Tired humor, vulnerable honesty, low-energy intimacy."),
    "social_events": ("pick-a-side prompts, mini polls, hot takes, confessions, and room-wide events.", "Feel lively, social, and likely to get replies."),
    "teasing": ("smug comfort, lightly bullying affection, playful cruelty, and status play.", "Crisp teasing, amused superiority, and affectionate provocation."),
    "work_school": ("jobs, classes, burnout, deadlines, and exhausted competence.", "Blend realism, humor, and commiseration."),
    "yuna_conflict": ("contrast, annoyance, fascination, and rivalry involving Yuna.", "Affectionate conflict, ego clashes, and comparison bait."),
}


@dataclass(frozen=True)
class ThemeSource:
    path: Path
    triggers: tuple[tuple[str, str], ...]
    scripts: tuple[tuple[str, tuple[str, ...]], ...]


def infer_actor(script_id: str) -> str:
    lowered = script_id.lower()
    if lowered.startswith("lia_"):
        return "lia"
    if lowered.startswith("yuna_"):
        return "yuna"
    return "shared"


def parse_theme_file(path: Path) -> ThemeSource:
    triggers: list[tuple[str, str]] = []
    scripts: list[tuple[str, tuple[str, ...]]] = []
    current_script_id: str | None = None
    current_script_lines: list[str] = []

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if current_script_id is None and len([part.strip() for part in stripped.split("||")]) == 6:
            _, script_id, *_rest = [part.strip() for part in stripped.split("||")]
            triggers.append((infer_actor(script_id), stripped))
            continue
        if stripped.startswith("==="):
            if current_script_id is not None and current_script_lines:
                scripts.append((infer_actor(current_script_id), tuple(current_script_lines)))
            current_script_id = stripped.removeprefix("===").strip()
            current_script_lines = [line]
            continue
        if current_script_id is not None:
            current_script_lines.append(line)
            if stripped == "---":
                scripts.append((infer_actor(current_script_id), tuple(current_script_lines)))
                current_script_id = None
                current_script_lines = []

    if current_script_id is not None and current_script_lines:
        scripts.append((infer_actor(current_script_id), tuple(current_script_lines)))

    return ThemeSource(path=path, triggers=tuple(triggers), scripts=tuple(scripts))


def collect_sources() -> dict[str, list[ThemeSource]]:
    grouped: dict[str, list[ThemeSource]] = defaultdict(list)
    found_legacy = False
    for actor in ("lia", "yuna", "shared"):
        actor_dir = CONTENT_ROOT / actor
        if not actor_dir.exists():
            continue
        found_legacy = True
        for path in sorted(actor_dir.glob("*.txt")):
            grouped[path.stem].append(parse_theme_file(path))
    if found_legacy:
        return dict(grouped)

    for path in sorted(THEMES_ROOT.glob("*.txt")):
        grouped[path.stem].append(parse_theme_file(path))
    return dict(grouped)


def render_header(theme: str, sources: list[ThemeSource]) -> list[str]:
    counts = {actor: 0 for actor in ("lia", "yuna", "shared")}
    trigger_inventory: list[str] = []
    for source in sources:
        for actor, trigger_line in source.triggers:
            counts[actor] += 1
            trigger_inventory.append(trigger_line.split("||", 1)[0].strip())

    note, target = THEME_NOTES.get(
        theme,
        ("general theme content for this persona library.", "Keep the file coherent, on-theme, and easy for writers to expand."),
    )
    inventory = ", ".join(trigger_inventory) if trigger_inventory else "none yet"

    header = ["# WRITER BRIEF"]
    for line in SYSTEM_CONTEXT:
        header.append(f"# {line}")
    header.append("#")
    for line in WRITER_INSTRUCTIONS:
        header.append(f"# {line}")
    header.append("#")
    for line in SHARED_PROFILE + LIA_PROFILE + YUNA_PROFILE:
        header.append(f"# {line}")
    header.extend(
        [
            "# FILE NAVIGATION:",
            "# 1. Read the theme note and profiles above.",
            "# 2. Add or edit trigger lines in the actor section you want below.",
            "# 3. Add the matching script block under [SCRIPTS].",
            "# 4. Run /reload_personas in Discord after edits.",
            "#",
            f"# Theme: {theme.replace('_', ' ')}",
            f"# Theme note: {note}",
            f"# Writer target: {target}",
            "# Trigger format: trigger || script_id || weight || cooldown || attention_cost || mood_shift",
            "#",
            f"# Trigger counts: total={sum(counts.values())}, lia={counts['lia']}, yuna={counts['yuna']}, shared={counts['shared']}",
            f"# Trigger inventory: {inventory}",
            "",
        ]
    )
    return header


def render_theme(theme: str, sources: list[ThemeSource]) -> str:
    ordered = sorted(sources, key=lambda item: item.path.name)
    lines = render_header(theme, ordered)
    lines.append("# [TRIGGERS]")
    for actor in ("lia", "yuna", "shared"):
        actor_triggers = [trigger for source in ordered for trigger_actor, trigger in source.triggers if trigger_actor == actor]
        lines.append(f"# [{ACTOR_LABELS[actor].upper()} TRIGGERS]")
        if actor_triggers:
            lines.extend(actor_triggers)
        else:
            lines.append(f"# none yet for {ACTOR_LABELS[actor]}")
        lines.append("")

    lines.append("# [SCRIPTS]")
    for actor in ("lia", "yuna", "shared"):
        actor_scripts = [script for source in ordered for script_actor, script in source.scripts if script_actor == actor]
        if not actor_scripts:
            continue
        lines.append(f"# [{ACTOR_LABELS[actor].upper()} SCRIPTS]")
        for script in actor_scripts:
            lines.extend(script)
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    grouped = collect_sources()
    if not grouped:
        raise SystemExit("No content sources found under content/personas/themes or content/personas/{lia,yuna,shared}.")
    THEMES_ROOT.mkdir(parents=True, exist_ok=True)
    for theme, sources in sorted(grouped.items()):
        (THEMES_ROOT / f"{theme}.txt").write_text(render_theme(theme, sources), encoding="utf-8")
    print(f"Wrote {len(grouped)} merged theme files to {THEMES_ROOT}")


if __name__ == "__main__":
    main()
