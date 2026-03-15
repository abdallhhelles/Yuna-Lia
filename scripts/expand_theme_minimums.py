from __future__ import annotations

from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[1]
THEMES_ROOT = REPO_ROOT / "content" / "personas" / "themes"
MINIMUM = 50
SPECIAL_SCRIPT_ONLY = {"birthdays", "daily_questions", "social_events"}

THEME_MODES = {
    "annoyed": "lia",
    "argument_starters": "duo",
    "birthdays": "special_birthdays",
    "casual": "duo",
    "chaos": "lia",
    "common_chat": "duo",
    "competition": "yuna",
    "conversation_starters": "duo",
    "daily_questions": "special_daily",
    "deep_longform": "special_longform",
    "discipline": "yuna",
    "disrespect": "duo",
    "drama": "lia",
    "duo_events": "duo",
    "existential": "duo",
    "fitness_health": "duo",
    "flirting": "duo",
    "food": "duo",
    "fun": "duo",
    "gaming": "duo",
    "gossip": "lia",
    "hobbies": "duo",
    "judgment": "yuna",
    "late_night": "duo",
    "lia_conflict": "yuna",
    "life_topics": "duo",
    "mature": "duo",
    "movies": "duo",
    "music": "duo",
    "philosophy": "yuna",
    "questions_and_jokes": "duo",
    "rare_events": "duo",
    "relationships": "duo",
    "sarcasm": "yuna",
    "secrets": "yuna",
    "shared_topics": "duo",
    "sleepy": "duo",
    "social_events": "special_social",
    "teasing": "duo",
    "work_school": "duo",
    "yuna_conflict": "lia",
}

THEME_KEYWORDS = {
    "annoyed": ["spam", "noise", "overexplaining", "dead air", "bad timing", "messy ping", "chaotic energy", "low effort"],
    "argument_starters": ["taste", "loyalty", "jealousy", "manners", "forgiveness", "friendship", "romance", "petty behavior"],
    "casual": ["hello", "check in", "room vibe", "small return", "morning energy", "soft reentry", "late hello", "tiny update"],
    "chaos": ["mess", "trouble", "instigation", "chaotic plan", "bit", "mild disaster", "suspicious boredom", "loud idea"],
    "common_chat": ["how are you", "what's up", "goodnight", "welcome back", "brb", "good morning", "wyd", "tiny update"],
    "competition": ["ranking", "winner", "comparison", "scoreboard", "advantage", "skill gap", "power level", "final verdict"],
    "conversation_starters": ["good question", "story", "comfort", "real thought", "weird opinion", "new topic", "mood", "confession"],
    "deep_longform": ["loneliness", "identity", "grief", "desire", "fear", "trust", "ambition", "belonging"],
    "discipline": ["consistency", "routine", "habit", "focus", "structure", "practice", "restraint", "effort"],
    "disrespect": ["rudeness", "cheap shot", "hater energy", "bad manners", "mockery", "dismissiveness", "low effort shade", "clumsy insult"],
    "drama": ["mixed signals", "ghosting", "weird reply", "messy crush", "friendship fracture", "jealous behavior", "cold shift", "awkward silence"],
    "duo_events": ["double act", "banter", "scene", "duo bit", "room moment", "joint reaction", "shared chaos", "paired riff"],
    "existential": ["meaning", "future", "being known", "loneliness", "identity", "purpose", "change", "mortality"],
    "fitness_health": ["gym", "recovery", "routine", "sleep", "hydration", "stretching", "health reset", "body maintenance"],
    "flirting": ["chemistry", "crush", "compliment", "eye contact", "dangerous smile", "romantic tension", "being noticed", "bold move"],
    "food": ["snack", "comfort meal", "late dinner", "favorite dessert", "food war", "restaurant take", "breakfast", "taste"],
    "fun": ["game", "bit", "challenge", "joke", "tiny poll", "weird prompt", "chaos", "clever distraction"],
    "gaming": ["ranked", "co-op", "build", "backlog", "controller rage", "indie game", "story game", "skill issue"],
    "gossip": ["tea", "lore", "messy update", "social rumor", "server history", "petty feud", "who started it", "recap"],
    "hobbies": ["craft", "collection", "obsession", "weekend project", "creative habit", "niche interest", "comfort hobby", "tiny skill"],
    "judgment": ["lie", "motive", "reputation", "character read", "trust", "bad faith", "manipulation", "integrity"],
    "late_night": ["insomnia", "night brain", "bad decision hour", "soft honesty", "restless mind", "quiet room", "after midnight", "sleep avoidance"],
    "lia_conflict": ["lia take", "lia behavior", "lia coded move", "lia chaos", "lia agenda", "lia being dramatic", "team lia", "lia interference"],
    "life_topics": ["change", "habits", "family", "friendship", "money stress", "identity", "motivation", "feeling behind"],
    "mature": ["desire", "tension", "after dark", "being wanted", "dangerous charm", "bad idea attraction", "heat", "romantic hunger"],
    "movies": ["rewatch", "bad ending", "movie crush", "genre loyalty", "horror logic", "rom com", "director taste", "cinema opinion"],
    "music": ["playlist", "song ruin", "album mood", "late night track", "favorite lyric vibe", "music taste", "artist obsession", "comfort song"],
    "philosophy": ["identity", "truth", "free will", "ethics", "self deception", "human nature", "future", "meaning"],
    "questions_and_jokes": ["petty opinion", "bad joke", "odd question", "soft confession", "room poll", "tiny dilemma", "funny truth", "chaos prompt"],
    "rare_events": ["unexpected softness", "special mood", "quiet tension", "gentle interruption", "unusual honesty", "strange calm", "memorable moment", "subtle chemistry"],
    "relationships": ["attachment", "green flag", "jealousy", "boundaries", "breakup", "texting style", "being chosen", "emotional safety"],
    "sarcasm": ["terrible plan", "obvious disaster", "remarkable choice", "deeply normal behavior", "great idea", "certainly wise", "impeccable timing", "superb logic"],
    "secrets": ["confession", "private truth", "buried feeling", "shame", "hidden motive", "secret crush", "small lie", "something unsaid"],
    "shared_topics": ["music", "movies", "science", "beauty", "internet culture", "travel", "technology", "nostalgia"],
    "sleepy": ["bedtime avoidance", "tired honesty", "delirious thought", "nap", "sleep debt", "soft night", "exhaustion", "foggy brain"],
    "teasing": ["skill issue", "smugness", "friendly bullying", "tiny humiliation", "ego bruise", "deserved drag", "mockery", "soft cruelty"],
    "work_school": ["deadline", "burnout", "meeting", "class", "group project", "pretending to focus", "email fatigue", "academic damage"],
    "yuna_conflict": ["yuna take", "yuna behavior", "team yuna", "yuna judgment", "yuna interference", "yuna coded move", "yuna standards", "yuna energy"],
}

TRIGGER_FRAMES = [
    "{topic}",
    "need a take on {topic}",
    "why is {topic} like this",
    "unpopular opinion about {topic}",
    "i have thoughts about {topic}",
    "talk about {topic}",
    "we need to discuss {topic}",
    "{topic} again",
    "{topic} discourse",
    "be honest about {topic}",
    "worst part of {topic}",
    "best part of {topic}",
    "i need help with {topic}",
    "my problem is {topic}",
    "tell me something real about {topic}",
    "anyone else dealing with {topic}",
]

DUO_LIA_OPENERS = [
    "okay, that topic has teeth.",
    "oh good, something with actual flavor.",
    "wait, i have feelings about that immediately.",
    "finally, a topic that deserves a pulse.",
    "that is exactly the kind of thing that wakes me up.",
    "you just dropped bait and i am unfortunately interested.",
]

DUO_YUNA_CLOSES = [
    "useful. we can work with that.",
    "predictably revealing, which is why it matters.",
    "good. the room should answer honestly for once.",
    "that usually exposes more than people intend.",
    "it is never only about the topic, and that is the point.",
    "excellent. subtle things become obvious under pressure.",
]

LIA_LINES = [
    "i am not neutral enough for that topic and i think that is a strength.",
    "that kind of thing always turns into a personality test if you wait long enough.",
    "i have the emotionally loud version of that opinion ready, naturally.",
    "that topic makes people reveal the exact kind of damage they accessorize.",
    "i love when something normal turns weirdly personal this fast.",
    "if the room gets honest about that, i will respect it forever.",
]

YUNA_LINES = [
    "that subject usually separates people with standards from people with excuses.",
    "it sounds simple until someone answers clearly.",
    "most people think they have an opinion there. fewer have reasoning.",
    "that is the sort of topic that exposes method, not just taste.",
    "people are rarely as consistent on that point as they imagine.",
    "good. that can be discussed without pretending not to care.",
]

LONGFORM_PROMPTS = [
    "what version of yourself do you perform when you want to seem unhurtable",
    "what kind of love makes you calmer instead of smaller",
    "what fear becomes your personality if you do not name it early",
    "what truth did you learn too late to stay innocent but early enough to change",
    "what do you miss even though you know it was bad for you",
    "what kind of understanding feels almost intimate to you",
    "what are you still carrying because it once kept you safe",
    "what part of growing up felt more like grief than progress",
    "what do people praise in you that you actually survive rather than enjoy",
    "what kind of loneliness can happen in a crowded room",
    "when do you feel most translated by another person",
    "what do you envy in people who seem lighter than you",
    "what dream would hurt the most to admit you still want",
    "what sort of apology changes the body before it changes the mind",
    "what do you protect so hard that it starts protecting you back poorly",
    "what do you wish people understood without turning it into advice",
    "what desire do you pretend is small because its real size scares you",
    "when did competence start becoming armor for you",
    "what kind of failure feels survivable and what kind feels identity-level",
    "what is the quietest way someone has made you feel chosen",
    "what does betrayal usually take from a person besides trust",
    "what part of you only appears when the room feels safe enough",
    "what do you miss about earlier versions of yourself",
    "what truth becomes obvious only after midnight",
    "what is harder for you: being seen accurately or being needed honestly",
    "what emotional habit looks like strength from the outside",
    "what do you think people confuse with intimacy all the time",
    "what makes someone feel real to you instead of merely impressive",
    "what kind of waiting changes a person",
    "what does it cost to be easy to love in public",
    "what belief about yourself keeps surviving every correction",
    "what would you say if you trusted the room not to flinch",
    "what does freedom mean when nobody is watching",
    "what part of tenderness embarrasses you most",
    "what do you owe the version of you that kept going",
    "what wound becomes taste if it stays around long enough",
    "what do people inherit emotionally without noticing",
    "what kind of clarity hurts before it helps",
    "what makes a person feel less alone than praise does",
    "what do you think people deserve but rarely receive on time",
    "what keeps someone emotionally young even when they are competent",
    "what do you think the body remembers after the mind moves on",
]


def sanitize(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def count_entries(path: Path) -> tuple[int, int, set[str], set[str]]:
    text = path.read_text(encoding="utf-8")
    triggers = 0
    scripts = 0
    existing_triggers: set[str] = set()
    script_ids: set[str] = set()
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("==="):
            scripts += 1
            script_ids.add(line.removeprefix("===").strip())
            continue
        parts = [part.strip() for part in line.split("||")]
        if len(parts) == 6:
            triggers += 1
            existing_triggers.add(parts[0].lower())
    return triggers, scripts, existing_triggers, script_ids


def next_index(script_ids: set[str], prefix: str) -> int:
    number = 1
    while f"{prefix}{number:02d}" in script_ids:
        number += 1
    return number


def actor_lines(mode: str, topic: str, angle: str, index: int) -> list[str]:
    if mode == "lia":
        return [
            f"=== lia_{topic}_boost_{index:02d}",
            f"Lia: {LIA_LINES[index % len(LIA_LINES)]}",
            f"Lia: honestly, {angle} is exactly where i stop pretending to be normal about it.",
            "---",
        ]
    if mode == "yuna":
        return [
            f"=== yuna_{topic}_boost_{index:02d}",
            f"Yuna: {YUNA_LINES[index % len(YUNA_LINES)]}",
            f"Yuna: if people answered cleanly about {angle}, the room would become more interesting very quickly.",
            "---",
        ]
    return [
        f"=== duo_{topic}_boost_{index:02d}",
        f"Lia: {DUO_LIA_OPENERS[index % len(DUO_LIA_OPENERS)]}",
        f"Lia: for me, {angle} is where people start accidentally telling the truth.",
        f"Yuna: {DUO_YUNA_CLOSES[index % len(DUO_YUNA_CLOSES)]}",
        "---",
    ]


def build_trigger(mode: str, theme: str, trigger_text: str, index: int) -> str:
    base = {"lia": "lia", "yuna": "yuna"}.get(mode, "duo")
    script_id = f"{base}_{sanitize(theme)}_boost_{index:02d}"
    weight = 0.52 + ((index % 6) * 0.03)
    cooldown = 420 if mode == "duo" else 360
    attention = "medium"
    mood = {
        "lia": "playful+",
        "yuna": "reflective+",
        "duo": "casual+",
    }.get(mode, "casual+")
    return f"{trigger_text} || {script_id} || {weight:.2f} || {cooldown} || {attention} || {mood}"


def unique_trigger(existing: set[str], candidate: str, theme: str, index: int) -> str:
    value = candidate.lower().strip()
    if value not in existing:
        existing.add(value)
        return candidate
    fallback = f"{candidate} tonight"
    if fallback.lower() not in existing:
        existing.add(fallback.lower())
        return fallback
    fallback = f"{theme.replace('_', ' ')} {index}"
    existing.add(fallback.lower())
    return fallback


def generate_generic(theme: str, mode: str, need: int, existing_triggers: set[str], script_ids: set[str]) -> tuple[list[str], list[list[str]]]:
    keywords = THEME_KEYWORDS[theme]
    trigger_lines: list[str] = []
    script_blocks: list[list[str]] = []
    prefix = f"{'lia' if mode == 'lia' else 'yuna' if mode == 'yuna' else 'duo'}_{sanitize(theme)}_boost_"
    number = next_index(script_ids, prefix)
    made = 0
    while made < need:
        topic = keywords[made % len(keywords)]
        frame = TRIGGER_FRAMES[made % len(TRIGGER_FRAMES)]
        trigger_text = unique_trigger(existing_triggers, frame.format(topic=topic), theme, number)
        trigger_lines.append(build_trigger(mode, theme, trigger_text, number))
        script_blocks.append(actor_lines(mode, sanitize(theme), topic, number))
        script_ids.add(f"{prefix}{number:02d}")
        number += 1
        made += 1
    return trigger_lines, script_blocks


def generate_birthdays(script_ids: set[str], need: int) -> list[list[str]]:
    openers = [
        "happy birthday, {user}. you get to be adored on purpose today.",
        "birthday alert for {user}. everybody act like you have range.",
        "happy birthday, {user}. i expect cake, attention, or a scandal.",
        "it is your birthday, {user}. legally the room must be softer.",
        "happy birthday, {user}. survive being this celebrated with dignity if possible.",
    ]
    yuna_lines = [
        "take the affection with composure. it is good for you.",
        "accept the attention gracefully. resistance would be theatrically wasteful.",
        "you have official permission to want more than usual today.",
        "be impossible to forget for at least twenty four hours.",
        "let people be sincere without pretending not to enjoy it.",
    ]
    prefix = "birthday_wish_"
    number = next_index(script_ids, prefix)
    blocks: list[list[str]] = []
    for idx in range(need):
        blocks.append(
            [
                f"=== {prefix}{number:02d}",
                f"Lia: {openers[idx % len(openers)]}",
                f"Yuna: {yuna_lines[idx % len(yuna_lines)]}",
                "---",
            ]
        )
        number += 1
    return blocks


def generate_daily(script_ids: set[str], need: int) -> list[list[str]]:
    prefix = "daily_question_"
    number = next_index(script_ids, prefix)
    blocks: list[list[str]] = []
    for idx in range(need):
        prompt = LONGFORM_PROMPTS[idx % len(LONGFORM_PROMPTS)]
        blocks.append(
            [
                f"=== {prefix}{number:02d}",
                "Lia: daily question.",
                f"Lia: {prompt}.",
                "Yuna: concise honesty is encouraged. overperformed poetry will be noticed.",
                "---",
            ]
        )
        number += 1
    return blocks


def generate_social(script_ids: set[str], need: int) -> list[list[str]]:
    categories = [
        ("social_pick_a_side_", "pick a side.", "soft life or loud life", "choose and defend yourselves properly."),
        ("social_mini_poll_", "mini poll.", "best apology form: changed behavior, thoughtful words, or instant accountability", "the room will reveal its standards whether it means to or not."),
        ("social_hot_take_", "hot take prompt.", "what do people confuse with chemistry too often", "make it sharp enough to matter."),
        ("social_confession_", "confession booth.", "what tiny thing embarrasses you more than it logically should", "the room is owed one good truth."),
        ("social_late_night_", "late-night check in.", "what feeling gets louder when the notifications finally stop", "brevity will only make it hit harder."),
    ]
    blocks: list[list[str]] = []
    used = {prefix: next_index(script_ids, prefix) for prefix, *_rest in categories}
    for idx in range(need):
        prefix, opener, topic, closer = categories[idx % len(categories)]
        number = used[prefix]
        blocks.append(
            [
                f"=== {prefix}{number:02d}",
                f"Lia: {opener}",
                f"Lia: {topic}.",
                f"Yuna: {closer}",
                "---",
            ]
        )
        used[prefix] += 1
    return blocks


def generate_longform(script_ids: set[str], existing_triggers: set[str], need: int, current_scripts: int, current_triggers: int) -> tuple[list[str], list[list[str]]]:
    prefix = "duo_long_deep_"
    number = next_index(script_ids, prefix)
    trigger_lines: list[str] = []
    blocks: list[list[str]] = []
    for idx in range(need):
        prompt = LONGFORM_PROMPTS[(current_scripts + idx) % len(LONGFORM_PROMPTS)]
        short_trigger = unique_trigger(existing_triggers, prompt, "deep_longform", number)
        if current_triggers + len(trigger_lines) < MINIMUM:
            trigger_lines.append(f"{short_trigger} || {prefix}{number:02d} || 0.63 || 1100 || high || reflective+")
        blocks.append(
            [
                f"=== {prefix}{number:02d}",
                f"Lia: {prompt}.",
                "Lia: i love when a question feels a little dangerous because it means the answer might matter.",
                "Yuna: yes. the best questions do not merely request information. they test what a person can tolerate knowing about themselves.",
                "Lia: and then the room has to decide whether honesty is worth the temperature change.",
                "---",
            ]
        )
        number += 1
    return trigger_lines, blocks


def append_to_file(path: Path, trigger_lines: list[str], script_blocks: list[list[str]]) -> None:
    additions: list[str] = []
    if trigger_lines:
        additions.extend(trigger_lines)
    if script_blocks:
        additions.append("")
        for block in script_blocks:
            additions.extend(block)
    if not additions:
        return
    with path.open("a", encoding="utf-8") as handle:
        handle.write("\n" + "\n".join(additions).rstrip() + "\n")


def main() -> None:
    for path in sorted(THEMES_ROOT.glob("*.txt")):
        theme = path.stem
        mode = THEME_MODES[theme]
        triggers, scripts, existing_triggers, script_ids = count_entries(path)
        trigger_additions: list[str] = []
        script_additions: list[list[str]] = []

        if mode == "special_birthdays":
            if scripts < MINIMUM:
                script_additions = generate_birthdays(script_ids, MINIMUM - scripts)
        elif mode == "special_daily":
            if scripts < MINIMUM:
                script_additions = generate_daily(script_ids, MINIMUM - scripts)
        elif mode == "special_social":
            if scripts < MINIMUM:
                script_additions = generate_social(script_ids, MINIMUM - scripts)
        elif mode == "special_longform":
            need_scripts = max(0, MINIMUM - scripts)
            need_triggers = max(0, MINIMUM - triggers)
            need = max(need_scripts, need_triggers)
            if need:
                trigger_additions, script_additions = generate_longform(script_ids, existing_triggers, need, scripts, triggers)
        else:
            need_scripts = max(0, MINIMUM - scripts)
            need_triggers = max(0, MINIMUM - triggers)
            need = max(need_scripts, need_triggers)
            if need:
                trigger_additions, script_additions = generate_generic(theme, mode, need, existing_triggers, script_ids)

        append_to_file(path, trigger_additions, script_additions)
        print(f"expanded {theme}: +{len(trigger_additions)} triggers, +{len(script_additions)} scripts")


if __name__ == "__main__":
    main()
