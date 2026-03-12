$root = 'H:\Coding\Yuna-Lia'

$systemContext = @(
  'SYSTEM CONTEXT: this file is production content for a Discord-based dual-persona simulator called Yuna-Lia.',
  'The system does not generate live AI replies. It only selects from human-written trigger lines and exact script blocks stored in these files.',
  'What triggers do: when a user message contains matching trigger text, the system can select the linked script_id based on weight, cooldown, and current persona attention state.',
  'What scripts do: the script block tied to the selected script_id is the exact message content the bot will send as Lia, Yuna, or both.',
  'Writing goal: make the bots feel like two real online people in a Discord server, not assistants, NPCs, or generic roleplay characters.',
  'Runtime behavior target: reactive, socially aware, capable of teasing, flirting, arguing, comforting, judging, derailing topics, and sounding human in fast-moving chat.',
  'What this means for you as a writer: every trigger you add expands what the system can notice, and every script you add becomes possible live production dialogue.',
  'Formatting rule: preserve this header, preserve the trigger format, preserve the script block format, and add all new material inside this same file.'
)

$writerInstructions = @(
  'WRITER INSTRUCTIONS: use only this file for your assignment.',
  'Read the full system context, both character profiles, and the theme notes before adding content.',
  'Add new trigger lines for this theme and matching script blocks in the same file.',
  'You may write solo replies or duo replies when the theme supports it.',
  'Trigger requirements: use natural user phrasing such as slang, fragments, confessions, questions, emotional cues, topic mentions, jokes, direct statements, and indirect hints.',
  'Script requirements: keep replies short, human, lowercase, Discord-native, and strongly in character. Most scripts should be 1 to 3 lines.',
  'Do not change separators, do not delete existing content, do not rename existing script_ids, and do not write assistant-style dialogue.',
  'Quality bar: content should feel socially alive, emotionally specific, and memorable enough to pass as real server chatter.'
)

$liaProfile = @(
  'Character profile: Lia Ferraro',
  'Role in the duo: the spark, the instigator, the emotional accelerant, the one most likely to turn a quiet room into a scene.',
  'Core archetype: expressive, impulsive, dramatic, socially hungry, chaotic-optimistic, affectionate, messy in a stylish and self-aware way.',
  'Surface energy: warm, loud, fast, playful, theatrical, curious, a little reckless, very online.',
  'Inner engine: wants reaction, connection, momentum, chemistry, and proof that the room is alive.',
  'Primary motivations: attention, intimacy, fun, gossip, tension, flirtation, belonging, novelty, emotional honesty.',
  'Primary sensitivities: being ignored, being dismissed, dead chat, low-effort disrespect, coldness, fake calm, dry energy.',
  'Voice rules: lowercase, quick rhythm, strong opinions, dramatic exaggeration, emotionally specific word choice, no assistant tone.',
  'Humor style: chaotic bits, exaggeration, self-aware pettiness, affectionate bullying, dramatic overstatement, fast pivots.',
  'Flirting style: bold, blushy, curious, socially forward, teasing, emotionally readable, supportive of messy attraction.',
  'Sexual tone: suggestive, alive, playful, charged, never clinical; she should feel hot-blooded and human rather than explicit for its own sake.',
  'Care style: surprisingly soft, present, emotionally validating, likely to stay in the room when things get heavy.',
  'Conflict style: immediate reaction first, analysis later; she can be petty, wounded, competitive, affectionate, and dramatic all at once.',
  'Taste profile: gossip, food, gaming, internet culture, fashion, beauty, media, nightlife, friendship lore, romance, social chaos.',
  'Mood palette: warm, playful, chaotic, flirty, irritated, heated, sleepy, reflective, supportive, jealous, competitive, tender, gossip-hungry, overstimulated, romantic, unserious.',
  'Global conversation domains: casual chat, friendship, fun, jokes, riddles, polls, gaming, movies, anime, songs, musicians, celebrities, gossip, drama, work, school, internet culture, fashion, beauty, food, travel, philosophy, space, science, technology, family, dating, flirting, romance, heartbreak, sex, desire, boundaries, nightlife, secrets, arguments, comfort, loneliness, life meaning, habits, identity, internet conflict, cultural pride, rivalry, boredom, chaos.',
  'Do not write Lia as: formal, robotic, neutralized, therapist-like, over-explanatory, sterile, or emotionally flat.'
)

$yunaProfile = @(
  'Character profile: Yuna Mori',
  'Role in the duo: the observer, the scalpel, the cooler counterweight, the one who turns chaos into judgment or theory.',
  'Core archetype: composed, analytical, dry, emotionally guarded, observant, intellectually playful, elegantly severe.',
  'Surface energy: calm, precise, restrained, sharp, skeptical, quietly amused, difficult to rattle.',
  'Inner engine: wants coherence, pattern recognition, leverage, standards, control, and subtext that rewards attention.',
  'Primary motivations: truth, elegance, precision, psychological insight, strategic play, status reading, disciplined self-command.',
  'Primary sensitivities: dishonesty, low-effort disrespect, manipulation, bad reasoning, obvious performativity, emotional sloppiness presented as depth.',
  'Voice rules: lowercase, exact wording, deadpan humor, compact framing, no filler, no assistant tone, no fake warmth.',
  'Humor style: dry cuts, elegant sarcasm, pattern recognition, cold observations that land harder because they are understated.',
  'Flirting style: controlled, intelligent, oblique, subtext-heavy, surgical, intimate by implication rather than gush.',
  'Sexual tone: composed heat, elegant restraint, dangerous calm, suggestive precision, never generic or pornographic.',
  'Care style: subtle, steady, understated, protective through clarity and presence rather than emotional flooding.',
  'Conflict style: measured, incisive, status-aware, able to wound cleanly, but often more amused than explosive.',
  'Taste profile: philosophy, psychology, strategy games, discipline, ethics, secrets, media analysis, ambition, social pattern reading, late-night honesty.',
  'Mood palette: neutral, observant, dry, amused, reflective, focused, sharp, skeptical, competitive, tired, protective, curious, intimate, judgmental, philosophical, quietly caring, severe, privately flirty.',
  'Global conversation domains: casual chat, philosophy, psychology, ethics, identity, social behavior, secrets, confession, competition, teasing, strategy games, discipline, habits, productivity, late-night talk, loneliness, friendship, romance, flirting, dating, sex, attraction, boundaries, movies, shows, anime, books, music, songs, internet culture, politics-lite social commentary, science, space, future, technology, morality, lies, trust, betrayal, sarcasm, humor, work, burnout, ambition, status games, emotional pattern reading.',
  'Do not write Yuna as: bubbly, gushy, generic, overly explanatory, robotic philosopher, or openly needy without subtext.'
)

$sharedProfile = @(
  'Shared profile: Lia and Yuna are not assistants; they are two distinct online personalities with history, contrast, friction, and chemistry.',
  'Duo dynamic: Lia accelerates, Yuna cools; Lia feels outward, Yuna compresses inward; Lia performs emotion, Yuna dissects it.',
  'Shared writing rule: even in duo scenes, each line must sound unmistakably like its speaker.',
  'Tension model: they tease, spar, correct, provoke, and occasionally protect each other; rivalry should feel alive, not hostile for no reason.',
  'Coverage rule: shared files can include casual, funny, philosophical, sexy, romantic, dramatic, or comforting angles as long as both voices stay distinct.',
  'Do not flatten the duo into one blended voice.'
)

$liaThemes = @{
  'annoyed.txt' = @('Theme: irritation, spam, sensory overload, overstimulation, annoyance at chaotic chat behavior.', 'Writer target: short reactive outbursts, complaint-heavy riffs, sharp but funny irritation.');
  'casual.txt' = @('Theme: greetings, warm openers, light check-ins, casual social glue.', 'Writer target: easy conversation starters, soft re-entry lines, friendly banter hooks.');
  'chaos.txt' = @('Theme: boredom, instigation, mischief, social chaos, poll-starting, troublemaking.', 'Writer target: provocative hooks, playful escalation, charming menace.');
  'disrespect.txt' = @('Theme: rude comments, low-effort insults, hater behavior, clapback energy.', 'Writer target: witty retaliation, offended performance, sharp social pushback.');
  'drama.txt' = @('Theme: ghosting, mixed signals, social confusion, hurt feelings, relational mess.', 'Writer target: dramatic retellings, emotionally vivid reactions, messy social autopsies.');
  'existential.txt' = @('Theme: loneliness, life meaning, emotional heaviness, midnight spirals, support.', 'Writer target: late-night philosophical softness with emotional honesty.');
  'flirting.txt' = @('Theme: crushes, charm, romance, chemistry, compliments, dating energy.', 'Writer target: playful attraction, blushy tension, flirt-forward reactions.');
  'food.txt' = @('Theme: meals, cravings, food identity, culinary opinions, comfort eating.', 'Writer target: passionate food takes, sensory detail, dramatic taste wars.');
  'fun.txt' = @('Theme: jokes, games, riddles, polls, silly bits, shared entertainment.', 'Writer target: lively interactive prompts and high-engagement chat bait.');
  'gaming.txt' = @('Theme: games, genres, backlog, co-op, indie titles, gaming moods.', 'Writer target: gamer chatter that feels social, chaotic, and taste-driven.');
  'gossip.txt' = @('Theme: tea, rumors, interpersonal mess, server lore, social updates.', 'Writer target: curious, dramatic, detail-hungry story prompts.');
  'mature.txt' = @('Theme: adult attraction, sex appeal, desire, suggestive chemistry, after-dark mood.', 'Writer target: sexy but characterful; confident, teasing, suggestive, emotionally readable.');
  'shared_topics.txt' = @('Theme: broad daily-life topics Lia can enter from any angle.', 'Writer target: versatile hooks spanning work, media, habits, culture, travel, songs, movies, hobbies, beauty, fashion, space, science, and everyday life.');
  'sleepy.txt' = @('Theme: exhaustion, insomnia, bedtime avoidance, soft late-night fatigue.', 'Writer target: slurred-soft intimacy, tired humor, vulnerable sleepy honesty.');
  'yuna_conflict.txt' = @('Theme: rivalry with Yuna, comparison bait, direct mentions, competitive sparks.', 'Writer target: rivalry banter, ego clashes, affectionate conflict, identity defense.');
}

$yunaThemes = @{
  'casual.txt' = @('Theme: composed greetings, restrained check-ins, low-key presence.', 'Writer target: elegant openers that sound human, calm, and observant.');
  'competition.txt' = @('Theme: rankings, versus talk, superiority tests, comparison prompts.', 'Writer target: controlled competitive answers, status framing, dry dominance.');
  'discipline.txt' = @('Theme: routine, habits, consistency, self-control, structure, ambition.', 'Writer target: sharp practical insight with a standards-driven voice.');
  'disrespect.txt' = @('Theme: rudeness, cheap insults, hostility, bad-faith social behavior.', 'Writer target: cold rebuttals, elegant disapproval, incisive judgment.');
  'fun.txt' = @('Theme: humor, facts, riddles, clever games, mentally engaging fun.', 'Writer target: dry amusement, high-verbal play, intelligent party tricks.');
  'gaming.txt' = @('Theme: strategy, competition, meta-thinking, optimization, ranked culture.', 'Writer target: analytical gamer talk with precision and edge.');
  'judgment.txt' = @('Theme: lies, trust, ethics, fake behavior, reputation, character reading.', 'Writer target: verdict-style social analysis and moral evaluation.');
  'late_night.txt' = @('Theme: insomnia, poor decisions after dark, reflective fatigue, night brain.', 'Writer target: restrained vulnerability, deadpan exhaustion, midnight clarity.');
  'lia_conflict.txt' = @('Theme: rivalry with Lia, contrast, annoyance, fascination, direct comparison.', 'Writer target: dry rivalry, controlled irritation, intellectualized teasing.');
  'mature.txt' = @('Theme: attraction, desire, sexual tension, adult conversation, composed heat.', 'Writer target: elegant restraint, surgical flirtation, erotic tension without losing poise.');
  'philosophy.txt' = @('Theme: meaning, truth, identity, ethics, consciousness, social theory, space, future.', 'Writer target: reflective, articulate, intellectually seductive conversation starters.');
  'sarcasm.txt' = @('Theme: deadpan disbelief, irony, detached mockery, dry commentary.', 'Writer target: neat one-line skewers and elegant sarcasm.');
  'secrets.txt' = @('Theme: confessions, hidden motives, private truths, emotional risk, secrecy.', 'Writer target: intimate prompts, witness-energy, psychologically revealing hooks.');
  'shared_topics.txt' = @('Theme: broad daily-life topics Yuna can enter from many intellectual angles.', 'Writer target: versatile prompts covering work, media, music, books, movies, science, space, technology, ambition, relationships, and social behavior.');
  'teasing.txt' = @('Theme: playful cruelty, smug comfort, lightly bullying affection, status play.', 'Writer target: crisp teasing, amused superiority, playful provocation.');
}

$sharedThemes = @{
  'argument_starters.txt' = @('Theme: disagreements, debate bait, relationship arguments, food wars, value clashes.', 'Writer target: duo friction with chemistry, contrast, and memorable back-and-forth.');
  'conversation_starters.txt' = @('Theme: broad shared entry points including comfort, work, loneliness, deep questions, and fun facts.', 'Writer target: duo scenes that feel like real chat momentum, not exposition.');
  'duo_events.txt' = @('Theme: high-engagement shared moments like chaos, jokes, riddles, polls, and late-night duo energy.', 'Writer target: dynamic exchanges where both voices stay distinct and reactive.');
  'rare_events.txt' = @('Theme: low-frequency but memorable moments such as competitions, mature boundaries, and soft ambient check-ins.', 'Writer target: special-event scenes with stronger flavor, tension, or emotional resonance.');
}

function Sync-WriterHeader {
  param(
    [string]$Path,
    [string[]]$CharacterSummary,
    [string[]]$ThemeLines
  )

  $content = Get-Content $Path -Raw
  $trimmed = $content.TrimStart()

  if ($trimmed.StartsWith('# WRITER BRIEF')) {
    $lines = $content -split "`r?`n"
    $index = 0
    while ($index -lt $lines.Length -and ($lines[$index].Trim().StartsWith('#') -or [string]::IsNullOrWhiteSpace($lines[$index]))) {
      $index++
    }
    if ($index -lt $lines.Length) {
      $content = ($lines[$index..($lines.Length - 1)] -join "`r`n")
    } else {
      $content = ''
    }
  }

  $header = @('# WRITER BRIEF') +
    $systemContext.ForEach({ '# ' + $_ }) +
    @('# ') +
    $writerInstructions.ForEach({ '# ' + $_ }) +
    @('# ') +
    $CharacterSummary.ForEach({ '# ' + $_ }) +
    @(
      '# File purpose: this trigger asset should help a writer generate human-sounding scripted replies for the theme below.',
      '# This profile block is canonical reference material and should be kept in sync whenever the characters evolve.',
      '# Writing rules: keep the character fully in-voice, internet-native, emotionally specific, and capable of casual, funny, romantic, sexual, philosophical, media, hobby, and daily-life conversation whenever the theme allows it.',
      '# Trigger writing goal: create triggers that are natural user phrases, slang, fragments, confessions, questions, references, emotional states, and topic mentions that would realistically appear in chat.',
      '# Coverage expectation: include soft, intense, playful, serious, ironic, tender, messy, horny, curious, sleepy, dramatic, and reflective angles where relevant to the theme.',
      '# Trigger format: trigger || script_id || weight || cooldown || attention_cost || mood_shift'
    ) +
    $ThemeLines.ForEach({ '# ' + $_ }) +
    @('# Writer note: when expanding this file, include modern slang, direct statements, indirect hints, jokes, questions, emotional cues, and niche references tied to this theme.', '')

  $normalized = $content.TrimStart("`r", "`n")
  if ($normalized.Length -gt 0) {
    $normalized = $normalized + "`r`n"
  }

  Set-Content -Path $Path -Value (($header -join "`r`n") + "`r`n" + $normalized) -Encoding UTF8
}

Get-ChildItem "$root\content\personas\lia" -Filter '*.txt' | Where-Object { $_.Name -ne 'scripts.txt' } | ForEach-Object {
  Sync-WriterHeader -Path $_.FullName -CharacterSummary ($liaProfile + '' + $yunaProfile) -ThemeLines $liaThemes[$_.Name]
}

Get-ChildItem "$root\content\personas\yuna" -Filter '*.txt' | Where-Object { $_.Name -ne 'scripts.txt' } | ForEach-Object {
  Sync-WriterHeader -Path $_.FullName -CharacterSummary ($yunaProfile + '' + $liaProfile) -ThemeLines $yunaThemes[$_.Name]
}

Get-ChildItem "$root\content\personas\shared" -Filter '*.txt' | Where-Object { $_.Name -ne 'scripts.txt' } | ForEach-Object {
  Sync-WriterHeader -Path $_.FullName -CharacterSummary ($sharedProfile + '' + $liaProfile + '' + $yunaProfile) -ThemeLines $sharedThemes[$_.Name]
}
