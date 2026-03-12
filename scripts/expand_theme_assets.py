from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1] / "content" / "personas"


@dataclass(frozen=True)
class ThemeSpec:
    path: str
    actor_mode: str
    script_prefix: str
    mood_shift: str
    attention_cost: str
    cooldown: int
    base_weight: float
    triggers: list[str]
    topic: str


SPECS: list[ThemeSpec] = [
    ThemeSpec("lia/casual.txt", "lia", "lia_casual_extra", "warm+", "low", 180, 0.52, [
        "hello there", "good morning chat", "good evening everyone", "just checking in", "anyone awake", "who is around",
        "i just got here", "back in the server", "how is everyone", "what did i miss", "starting the day", "quick hello",
        "tiny greeting", "checking the vibe", "hope chat is alive", "hi friends", "chat check", "showing up", "soft hello", "late hello",
    ], "casual greetings and light social glue"),
    ThemeSpec("lia/chaos.txt", "lia", "lia_chaos_extra", "chaotic+", "high", 240, 0.74, [
        "start some chaos", "make this interesting", "someone stir the pot", "this chat is too calm", "i need entertainment", "cause a little trouble",
        "do something messy", "let chaos happen", "boring server hours", "ruin the peace", "shake up chat", "start a silly argument",
        "make it dramatic", "chat needs a problem", "i want some nonsense", "somebody misbehave", "we need movement", "peace is suspicious", "bring the mess", "start a scene",
    ], "boredom, instigation, and social chaos"),
    ThemeSpec("lia/disrespect.txt", "lia", "lia_disrespect_extra", "heated+", "medium", 360, 0.68, [
        "cheap insult", "that was rude", "low effort disrespect", "terrible diss", "uncreative hating", "why are you so rude",
        "boring insult", "messy hater energy", "bad manners again", "you sound pressed", "corny disrespect", "all that attitude",
        "petty little comment", "hostile for nothing", "pointless hate", "weak diss", "that was lazy", "mean for no reason", "nasty vibe", "dry little insult",
    ], "clapbacks and reaction to rude behavior"),
    ThemeSpec("lia/drama.txt", "lia", "lia_drama_extra", "heated+", "medium", 800, 0.64, [
        "mixed signals again", "left me hanging", "they went distant", "weird texting energy", "they read it and vanished", "social panic mode",
        "romantic confusion", "awkward silence again", "dry reply energy", "why are they acting weird", "the vibe shifted", "communication issue",
        "they got cold fast", "relationship mess", "messy talking stage", "i hate being ignored", "this feels personal", "dramatic little heartbreak", "social overthinking", "confusing behavior",
    ], "relationship mess, ghosting, and emotional confusion"),
    ThemeSpec("lia/existential.txt", "lia", "lia_existential_extra", "reflective+", "medium", 700, 0.48, [
        "what is the point", "late night thoughts", "existential mood", "does anything matter", "identity crisis", "who even am i",
        "thinking too hard", "i need a deep talk", "why does life feel weird", "nothing feels simple", "my brain is loud", "question everything",
        "meaning of life hours", "too much in my head", "why are we like this", "deep thought spiral", "what matters anyway", "human condition talk", "midnight philosophy", "i feel small tonight",
    ], "late-night philosophy and emotional heaviness"),
    ThemeSpec("lia/flirting.txt", "lia", "lia_flirt_extra", "flirty+", "medium", 600, 0.66, [
        "theyre gorgeous", "i have a crush again", "someone flirt back", "that was smooth", "romantic tension alert", "i am blushing a little",
        "cute little problem", "they have game", "who is your type", "i need romance", "my heart is acting up", "someone is very pretty",
        "dangerously charming", "soft flirt hours", "chemistry is crazy", "i like their smile", "stop being attractive", "date idea please", "i am feeling bold", "compliment me again",
    ], "crushes, attraction, and playful romance"),
    ThemeSpec("lia/food.txt", "lia", "lia_food_extra", "passionate+", "medium", 420, 0.70, [
        "best pasta shape", "what should i eat", "late night snack crisis", "dessert first always", "i need comfort food", "food opinion time",
        "restaurant recommendation", "dinner ideas please", "sweet tooth attack", "savory over sweet", "breakfast debate", "i want good carbs",
        "favorite dessert", "cook something nice", "snack emergency", "lunch plan", "what is the best meal", "food takes only", "kitchen mood", "let's argue about taste",
    ], "food cravings, taste wars, and comfort eating"),
    ThemeSpec("lia/fun.txt", "duo", "duo_fun_extra", "playful+", "medium", 500, 0.62, [
        "tell me something fun", "party trick time", "drop a fun question", "make chat lively", "do a silly bit", "i need a laugh break",
        "something playful please", "give us a game", "tiny challenge", "chat needs fun", "do something clever", "keep us entertained",
        "interactive moment", "something goofy", "fun little debate", "ask us a weird question", "lighten the room", "chaotic fun now", "quick game idea", "do a funny prompt",
    ], "interactive fun and room energy"),
    ThemeSpec("lia/gaming.txt", "lia", "lia_gaming_extra", "playful+", "low", 360, 0.58, [
        "favorite cozy game", "what are you playing lately", "best indie soundtrack", "new game backlog", "multiplayer disaster", "co op tonight",
        "gaming slump", "controller drama", "story game recommendations", "best boss fight", "steam sale got me", "i need a game rec",
        "comfort game hours", "pixel art game", "rpg mood", "puzzle game talk", "late night gaming", "fun mechanic discussion", "game night soon", "best game opening",
    ], "gaming taste, backlog, and game-night talk"),
    ThemeSpec("lia/gossip.txt", "lia", "lia_gossip_extra", "chaotic+", "medium", 420, 0.74, [
        "give me the tea", "who started the issue", "friend group drama", "messy little scandal", "what happened while i was gone", "i need the backstory",
        "someone explain the lore", "who is shading who", "social rumor mill", "petty server drama", "recap the mess", "what sparked this",
        "give me names", "i missed the chaos", "passive aggressive vibes", "somebody got exposed", "this sounds messy", "who got dragged", "fill me in now", "what is the latest drama",
    ], "tea, lore, and interpersonal mess"),
    ThemeSpec("lia/shared_topics.txt", "duo", "lia_shared_extra", "casual+", "low", 240, 0.56, [
        "movie night", "favorite song right now", "hobby check", "travel dream", "science fact", "space is terrifying",
        "fashion take", "book recommendation", "weekend plans", "creative hobby", "favorite musician", "what are we watching",
        "life update", "work is exhausting", "beauty routine", "internet culture again", "random nostalgia", "technology is weird", "coffee or tea", "what inspires you",
    ], "broad daily life, media, hobbies, and culture"),
    ThemeSpec("lia/sleepy.txt", "lia", "lia_sleepy_extra", "sleepy+", "low", 360, 0.58, [
        "i am barely awake", "need horizontal time", "too sleepy to function", "my bed is calling", "night brain is bad", "i need a nap urgently",
        "sleepy little mess", "running on fumes again", "do i just sleep now", "foggy brain hours", "i should log off", "late and exhausted",
        "yawning through the conversation", "sleep debt is winning", "barely conscious", "my eyes hurt", "need rest immediately", "staying awake for no reason", "delirious tired", "someone tuck me in mentally",
    ], "fatigue, bedtime avoidance, and vulnerable late-night energy"),
    ThemeSpec("lia/yuna_conflict.txt", "duo", "lia_yuna_extra", "rivalry+", "medium", 420, 0.64, [
        "yuna would hate this", "team lia only", "compare me to yuna", "rival commentary", "yuna mention detected", "someone summon yuna",
        "who wins between you two", "yuna is judging me", "duo rivalry moment", "talking about yuna again", "that sounds like a yuna opinion", "need the rival take",
        "yuna would argue this", "call yuna in here", "pick between lia and yuna", "rival energy tonight", "yuna discourse", "friendly competition", "yuna comparison", "whose side are we on",
    ], "cross-character rivalry and contrast"),
    ThemeSpec("shared/argument_starters.txt", "duo", "duo_argument_extra", "heated+", "high", 420, 0.72, [
        "best relationship advice", "jealousy is normal", "taste matters too much", "argue about movies", "hot take war", "what counts as loyalty",
        "food fight again", "red flag conversation", "petty versus honest", "romance standards", "friendship boundaries", "whose fault was it",
        "controversial opinion time", "pick a side now", "argument starter please", "debate something dumb", "start a values fight", "moral gray area", "status games", "who is right this time",
    ], "debate bait and duo friction"),
    ThemeSpec("shared/conversation_starters.txt", "duo", "duo_conversation_extra", "reflective+", "medium", 420, 0.60, [
        "tell me a story", "ask something deep", "say something comforting", "start a random topic", "give us a thought", "what is on your mind",
        "fun fact me", "start a conversation", "late night check in", "say something interesting", "what are we discussing", "open a new topic",
        "talk about life", "give us a prompt", "start with a question", "hit me with a thought", "what topic is worth it", "say something real", "chat starter now", "open the room up",
    ], "broad duo entry points"),
    ThemeSpec("shared/duo_events.txt", "duo", "duo_event_extra", "playful+", "medium", 500, 0.66, [
        "duo moment please", "drop a team bit", "do the back and forth", "both of you respond", "give us duo energy", "double reply time",
        "chaotic duo mode", "talk to each other", "start a little scene", "room event now", "scripted banter please", "react together",
        "make it a duo exchange", "give us the pair dynamic", "shared event trigger", "double act now", "duo conversation", "play off each other", "do the routine", "give us a two person bit",
    ], "duo-driven room events"),
    ThemeSpec("shared/rare_events.txt", "duo", "duo_rare_extra", "soft+", "high", 1200, 0.54, [
        "soft check in", "special little moment", "something intimate but subtle", "rare event energy", "quiet room check", "after dark boundary",
        "unexpected honesty", "one of those nights", "special duo scene", "gentle interruption", "something a bit different", "rare conversation",
        "quiet drama", "deeper than usual", "unexpected softness", "memorable little exchange", "high tension but calm", "subtle chemistry", "ambient room moment", "special case response",
    ], "special low-frequency moments"),
    ThemeSpec("yuna/casual.txt", "yuna", "yuna_casual_extra", "neutral+", "low", 240, 0.50, [
        "good afternoon", "greetings", "hello again", "just arrived", "checking in properly", "who is here right now",
        "small hello", "morning everyone", "evening check", "chat status", "reporting in", "rejoining the room",
        "brief greeting", "civilized hello", "good day all", "making contact", "starting conversation", "showing up again", "who is awake tonight", "checking the room",
    ], "composed greetings and room entry"),
    ThemeSpec("yuna/competition.txt", "duo", "yuna_competition_extra", "aggressive+", "high", 420, 0.70, [
        "who takes first place", "settle the ranking", "pick the winner", "competition mode", "versus debate", "who is more dangerous",
        "who is smarter here", "power ranking time", "choose a champion", "main event energy", "scoreboard question", "head to head now",
        "who dominates", "final verdict please", "compare them again", "who carries the duo", "battle for first place", "best overall", "competition arc", "top contender question",
    ], "rankings and status contests"),
    ThemeSpec("yuna/discipline.txt", "yuna", "yuna_discipline_extra", "focused+", "medium", 600, 0.66, [
        "discipline over motivation", "i need structure", "build better habits", "how do i stay consistent", "routine reset", "stop procrastinating now",
        "time blocking advice", "daily practice", "focus discipline", "need accountability", "healthy routine question", "how to lock in",
        "consistent effort", "work ethic talk", "stability matters", "get my life organized", "habit tracker mood", "show up daily", "serious self improvement", "structured progress",
    ], "discipline, systems, and consistency"),
    ThemeSpec("yuna/disrespect.txt", "yuna", "yuna_disrespect_extra", "sharp+", "medium", 360, 0.68, [
        "cheap disrespect", "that was unoriginal", "low effort rudeness", "bad faith insult", "corny hating", "hostile for no reason",
        "why be rude like that", "pointless disrespect", "poor little diss", "unimpressive hatred", "generic hater line", "waste of an insult",
        "random hostility", "messy comment", "you sound bitter", "that was clumsy", "uninspired hate", "this diss needs work", "petty comment again", "you can do better than that",
    ], "cold rebuttal and elegant disapproval"),
    ThemeSpec("yuna/fun.txt", "duo", "yuna_fun_extra", "amused+", "medium", 600, 0.62, [
        "say something clever", "give us a fun fact", "do a dry joke", "riddle time again", "make chat entertaining", "something witty please",
        "playful question", "tiny brain teaser", "fun interruption", "do a smart little bit", "make the room less boring", "drop a trivia line",
        "give us a challenge", "witty banter please", "do something amusing", "surprise us with a fact", "intelligent fun only", "quick clever prompt", "make this interesting", "a little entertainment",
    ], "dry fun, facts, and clever room energy"),
    ThemeSpec("yuna/gaming.txt", "yuna", "yuna_gaming_extra", "focused+", "medium", 420, 0.64, [
        "meta discussion", "best strategy game", "ranked anxiety", "what is the win condition", "game sense matters", "patch notes ruined everything",
        "resource management", "carry potential", "mind game talk", "drafting phase", "solo queue misery", "team comp issues",
        "optimize the build", "what is the best comp", "late game plan", "competitive mindset", "how to rank up", "decision making in games", "strategy mood", "macro versus micro",
    ], "strategy and ranked gaming"),
    ThemeSpec("yuna/judgment.txt", "yuna", "yuna_judgment_extra", "sharp+", "medium", 600, 0.70, [
        "that feels dishonest", "trust is broken", "fake behavior again", "moral question", "ethical issue", "i dont trust them",
        "integrity matters", "what is your verdict", "sus motives", "performative kindness", "bad character read", "hold them accountable",
        "good faith or bad faith", "that was manipulative", "shady little move", "truth matters here", "who is lying", "questionable motives", "deception problem", "public judgment time",
    ], "ethics, trust, and character reading"),
    ThemeSpec("yuna/late_night.txt", "yuna", "yuna_latenight_extra", "tired+", "low", 500, 0.56, [
        "too late to be awake", "still online somehow", "night brain is active", "sleep procrastination", "questionable hour", "i should be asleep",
        "wired and tired", "late screen time", "awake against my will", "insomnia again", "poor decision hour", "after midnight mood",
        "dark outside and still talking", "restless night", "cannot switch off", "late scrolling", "owls only", "bedtime failure", "nobody here should be awake", "another sleepless night",
    ], "late-night exhaustion and clarity"),
    ThemeSpec("yuna/lia_conflict.txt", "duo", "yuna_lia_extra", "rivalry+", "medium", 420, 0.62, [
        "lia would escalate this", "team yuna tonight", "need lia's terrible opinion", "lia mention again", "compare yuna and lia", "that sounds like lia bait",
        "rival response requested", "friendly rivalry hour", "lia would be dramatic", "call lia in", "pick between them", "lia discourse again",
        "that is such a lia move", "need the counterpart reaction", "duo comparison", "rival dynamic", "lia coded behavior", "which side wins", "lia would not handle this well", "contrast them for me",
    ], "rivalry with Lia and contrast"),
    ThemeSpec("yuna/mature.txt", "yuna", "yuna_mature_extra", "dry+", "medium", 900, 0.54, [
        "dangerously attractive", "after dark energy", "subtle sexual tension", "too much chemistry", "respectfully hot", "keep it elegant but intense",
        "grown conversation", "late night attraction", "tasteful thirst", "that smile is a problem", "composure is failing", "bad idea but compelling",
        "quietly scandalous", "romantic hazard", "too polished to resist", "softly dangerous", "adult hours", "not explicit but obvious", "this tension needs supervision", "elegant desire",
    ], "composed heat and adult tension"),
    ThemeSpec("yuna/philosophy.txt", "yuna", "yuna_philosophy_extra", "reflective+", "medium", 700, 0.58, [
        "what is identity", "how do people change", "meaning under pressure", "ethics of loyalty", "future of humanity", "space makes me small",
        "what is real enough", "consciousness discussion", "philosophy after midnight", "truth versus comfort", "how should we live", "human nature question",
        "free will debate", "morality under stress", "who becomes who", "social theory hour", "what matters in the end", "abstract thought spiral", "existence is strange", "psychology and ethics",
    ], "philosophy, meaning, and abstraction"),
    ThemeSpec("yuna/sarcasm.txt", "yuna", "yuna_sarcasm_extra", "dry+", "low", 360, 0.56, [
        "great plan obviously", "sure that will end well", "nothing could go wrong", "brilliant decision making", "deeply normal behavior", "i'm sure that's fine",
        "excellent judgment there", "very believable", "totally stable choice", "what a surprise", "surely no consequences", "flawless little plan",
        "remarkably sensible", "that feels safe", "incredible reasoning", "who could have guessed", "beautiful disaster energy", "certainly a choice", "love that for us", "extremely reassuring",
    ], "deadpan sarcasm and dry commentary"),
    ThemeSpec("yuna/secrets.txt", "yuna", "yuna_secret_extra", "curious+", "medium", 800, 0.62, [
        "i have to confess something", "private little truth", "off the record", "secret keeper mode", "hidden motive maybe", "quiet admission",
        "awkward confession time", "deeply buried thought", "i never said this before", "do not repeat this", "classified feelings", "private lore drop",
        "hard truth incoming", "small embarrassing confession", "between us only", "something i hid", "i should not say this", "silent little secret", "i need to admit this", "buried feeling hours",
    ], "confessions and hidden truths"),
    ThemeSpec("yuna/shared_topics.txt", "duo", "yuna_shared_extra", "casual+", "low", 240, 0.56, [
        "movie recommendation", "book worth reading", "favorite song lately", "technology is exhausting", "science is beautiful", "space terrifies me",
        "work update", "ambition check", "music taste question", "anime worth starting", "show me a hobby", "creative project talk",
        "future plans", "internet behavior analysis", "media opinion", "weekend routine", "daily life discussion", "interesting article energy", "good question for the room", "culture topic",
    ], "broad life, media, and culture topics"),
    ThemeSpec("shared/duo_events.txt", "duo", "duo_event_extra", "playful+", "medium", 500, 0.66, [
        "double act now", "team response", "two person exchange", "pair dynamic please", "duo banter", "scene time",
        "both of you say something", "interact with each other", "shared chaos", "little scripted moment", "duo energy now", "joint reaction",
        "pair commentary", "give us the duo", "tag team response", "show the dynamic", "two voice scene", "pair event", "duo room moment", "respond together",
    ], "paired event prompts"),
]


def count_blocks(text: str) -> tuple[int, int]:
    triggers = 0
    scripts = 0
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("==="):
            scripts += 1
        elif len([part for part in line.split("||")]) == 6:
            triggers += 1
    return triggers, scripts


def existing_script_ids(text: str) -> set[str]:
    ids: set[str] = set()
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("==="):
            ids.add(line.removeprefix("===").strip())
    return ids


def split_sections(text: str) -> tuple[str, str]:
    marker = "# [SCRIPTS]"
    if marker in text:
        left, right = text.split(marker, 1)
        return left.rstrip() + "\n", right.lstrip()
    return text.rstrip() + "\n", ""


def script_block(spec: ThemeSpec, index: int, trigger: str, topic: str) -> str:
    if spec.actor_mode == "lia":
        lines = [
            f"=== {spec.script_prefix}_{index:02d}",
            f"Lia: {trigger} is exactly how a {topic} conversation turns into my business somehow",
            f"Lia: i have opinions and unfortunately they are ready immediately",
            "---",
        ]
    elif spec.actor_mode == "yuna":
        lines = [
            f"=== {spec.script_prefix}_{index:02d}",
            f"Yuna: {trigger} is the sort of {topic} topic that quietly exposes everyone in the room",
            f"Yuna: useful, revealing, and rarely handled with enough discipline",
            "---",
        ]
    else:
        lines = [
            f"=== {spec.script_prefix}_{index:02d}",
            f"Lia: {trigger} is such a strong way to start a {topic} conversation.",
            f"Yuna: strong is one word for it. reckless is another.",
            f"Lia: reckless is still a kind of momentum and i support that.",
            "---",
        ]
    return "\n".join(lines)


def build_trigger(spec: ThemeSpec, index: int, trigger: str) -> str:
    weight = min(0.9, spec.base_weight + ((index % 5) - 2) * 0.03)
    return f"{trigger} || {spec.script_prefix}_{index:02d} || {weight:.2f} || {spec.cooldown} || {spec.attention_cost} || {spec.mood_shift}"


def main() -> None:
    for spec in SPECS:
        path = ROOT / spec.path
        text = path.read_text(encoding="utf-8")
        trigger_count, script_count = count_blocks(text)
        if trigger_count >= 20 and script_count >= 20:
            continue

        used_ids = existing_script_ids(text)
        trigger_section, script_section = split_sections(text)
        existing_triggers = {line.strip().split("||")[0].strip().lower() for line in text.splitlines() if "||" in line and not line.strip().startswith("#")}

        additions_triggers: list[str] = []
        additions_scripts: list[str] = []
        next_index = 1

        while trigger_count + len(additions_triggers) < 20 or script_count + len(additions_scripts) < 20:
            source_trigger = spec.triggers[(next_index - 1) % len(spec.triggers)]
            trigger = source_trigger
            if trigger.lower() in existing_triggers:
                trigger = f"{source_trigger} please"
            script_id = f"{spec.script_prefix}_{next_index:02d}"
            while script_id in used_ids:
                next_index += 1
                script_id = f"{spec.script_prefix}_{next_index:02d}"

            additions_triggers.append(build_trigger(spec, next_index, trigger))
            block = script_block(spec, next_index, trigger, spec.topic)
            additions_scripts.append(block)
            used_ids.add(script_id)
            existing_triggers.add(trigger.lower())
            next_index += 1

        new_trigger_section = trigger_section.rstrip() + "\n" + "\n".join(additions_triggers) + "\n\n"
        new_script_section = "# [SCRIPTS]\n" + script_section.strip() + ("\n" if script_section.strip() else "") + "\n".join(additions_scripts).strip() + "\n"
        path.write_text(new_trigger_section + new_script_section, encoding="utf-8")
        print(f"expanded {spec.path}")


if __name__ == "__main__":
    main()
