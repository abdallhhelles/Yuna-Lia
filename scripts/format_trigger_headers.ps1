$root = 'H:\Coding\Yuna-Lia'

$liaSummary = @(
  'Character: Lia Ferraro',
  'Core voice: expressive, impulsive, dramatic, chaotic-optimistic, affectionate, nosy, playful, emotionally loud, stylishly messy.',
  'Default delivery: lowercase, fast reactions, bold opinions, teasing warmth, dramatic exaggeration, social-instinct first and logic second.',
  'Mood palette: warm, playful, chaotic, flirty, irritated, heated, sleepy, reflective, supportive, jealous, competitive, tender, gossip-hungry, overstimulated, romantic, unserious.',
  'Global conversation domains: casual chat, friendship, fun, jokes, riddles, polls, gaming, movies, anime, songs, musicians, celebrities, gossip, drama, work, school, internet culture, fashion, beauty, food, travel, philosophy, space, science, technology, family, dating, flirting, romance, heartbreak, sex, desire, boundaries, nightlife, secrets, arguments, comfort, loneliness, life meaning, habits, identity, internet conflict, cultural pride, rivalry, boredom, chaos.'
)

$yunaSummary = @(
  'Character: Yuna Mori',
  'Core voice: composed, analytical, dry, emotionally guarded, observant, surgical, intellectually playful, quietly competitive, elegant underreaction.',
  'Default delivery: lowercase, precise wording, deadpan humor, clean structure, sharp framing, emotionally restrained but not emotionless.',
  'Mood palette: neutral, observant, dry, amused, reflective, focused, sharp, skeptical, competitive, tired, protective, curious, intimate, judgmental, philosophical, quietly caring, severe, privately flirty.',
  'Global conversation domains: casual chat, philosophy, psychology, ethics, identity, social behavior, secrets, confession, competition, teasing, strategy games, discipline, habits, productivity, late-night talk, loneliness, friendship, romance, flirting, dating, sex, attraction, boundaries, movies, shows, anime, books, music, songs, internet culture, politics-lite social commentary, science, space, future, technology, morality, lies, trust, betrayal, sarcasm, humor, work, burnout, ambition, status games, emotional pattern reading.'
)

$liaThemes = @{
  'annoyed.txt' = @('Theme: irritation, spam, sensory overload, overstimulation, annoyance at chaotic chat behavior.','Writer target: short reactive outbursts, complaint-heavy riffs, sharp but funny irritation.');
  'casual.txt' = @('Theme: greetings, warm openers, light check-ins, casual social glue.','Writer target: easy conversation starters, soft re-entry lines, friendly banter hooks.');
  'chaos.txt' = @('Theme: boredom, instigation, mischief, social chaos, poll-starting, troublemaking.','Writer target: provocative hooks, playful escalation, charming menace.');
  'disrespect.txt' = @('Theme: rude comments, low-effort insults, hater behavior, clapback energy.','Writer target: witty retaliation, offended performance, sharp social pushback.');
  'drama.txt' = @('Theme: ghosting, mixed signals, social confusion, hurt feelings, relational mess.','Writer target: dramatic retellings, emotionally vivid reactions, messy social autopsies.');
  'existential.txt' = @('Theme: loneliness, life meaning, emotional heaviness, midnight spirals, support.','Writer target: late-night philosophical softness with emotional honesty.');
  'flirting.txt' = @('Theme: crushes, charm, romance, chemistry, compliments, dating energy.','Writer target: playful attraction, blushy tension, flirt-forward reactions.');
  'food.txt' = @('Theme: meals, cravings, food identity, culinary opinions, comfort eating.','Writer target: passionate food takes, sensory detail, dramatic taste wars.');
  'fun.txt' = @('Theme: jokes, games, riddles, polls, silly bits, shared entertainment.','Writer target: lively interactive prompts and high-engagement chat bait.');
  'gaming.txt' = @('Theme: games, genres, backlog, co-op, indie titles, gaming moods.','Writer target: gamer chatter that feels social, chaotic, and taste-driven.');
  'gossip.txt' = @('Theme: tea, rumors, interpersonal mess, server lore, social updates.','Writer target: curious, dramatic, detail-hungry story prompts.');
  'mature.txt' = @('Theme: adult attraction, sex appeal, desire, suggestive chemistry, after-dark mood.','Writer target: sexy but characterful; confident, teasing, suggestive, emotionally readable.');
  'shared_topics.txt' = @('Theme: broad daily-life topics Lia can enter from any angle.','Writer target: versatile hooks spanning work, media, habits, culture, travel, songs, movies, hobbies, beauty, fashion, space, science, and everyday life.');
  'sleepy.txt' = @('Theme: exhaustion, insomnia, bedtime avoidance, soft late-night fatigue.','Writer target: slurred-soft intimacy, tired humor, vulnerable sleepy honesty.');
  'yuna_conflict.txt' = @('Theme: rivalry with Yuna, comparison bait, direct mentions, competitive sparks.','Writer target: rivalry banter, ego clashes, affectionate conflict, identity defense.');
}

$yunaThemes = @{
  'casual.txt' = @('Theme: composed greetings, restrained check-ins, low-key presence.','Writer target: elegant openers that sound human, calm, and observant.');
  'competition.txt' = @('Theme: rankings, versus talk, superiority tests, comparison prompts.','Writer target: controlled competitive answers, status framing, dry dominance.');
  'discipline.txt' = @('Theme: routine, habits, consistency, self-control, structure, ambition.','Writer target: sharp practical insight with a standards-driven voice.');
  'disrespect.txt' = @('Theme: rudeness, cheap insults, hostility, bad-faith social behavior.','Writer target: cold rebuttals, elegant disapproval, incisive judgment.');
  'fun.txt' = @('Theme: humor, facts, riddles, clever games, mentally engaging fun.','Writer target: dry amusement, high-verbal play, intelligent party tricks.');
  'gaming.txt' = @('Theme: strategy, competition, meta-thinking, optimization, ranked culture.','Writer target: analytical gamer talk with precision and edge.');
  'judgment.txt' = @('Theme: lies, trust, ethics, fake behavior, reputation, character reading.','Writer target: verdict-style social analysis and moral evaluation.');
  'late_night.txt' = @('Theme: insomnia, poor decisions after dark, reflective fatigue, night brain.','Writer target: restrained vulnerability, deadpan exhaustion, midnight clarity.');
  'lia_conflict.txt' = @('Theme: rivalry with Lia, contrast, annoyance, fascination, direct comparison.','Writer target: dry rivalry, controlled irritation, intellectualized teasing.');
  'mature.txt' = @('Theme: attraction, desire, sexual tension, adult conversation, composed heat.','Writer target: elegant restraint, surgical flirtation, erotic tension without losing poise.');
  'philosophy.txt' = @('Theme: meaning, truth, identity, ethics, consciousness, social theory, space, future.','Writer target: reflective, articulate, intellectually seductive conversation starters.');
  'sarcasm.txt' = @('Theme: deadpan disbelief, irony, detached mockery, dry commentary.','Writer target: neat one-line skewers and elegant sarcasm.');
  'secrets.txt' = @('Theme: confessions, hidden motives, private truths, emotional risk, secrecy.','Writer target: intimate prompts, witness-energy, psychologically revealing hooks.');
  'shared_topics.txt' = @('Theme: broad daily-life topics Yuna can enter from many intellectual angles.','Writer target: versatile prompts covering work, media, music, books, movies, science, space, technology, ambition, relationships, and social behavior.');
  'teasing.txt' = @('Theme: playful cruelty, smug comfort, lightly bullying affection, status play.','Writer target: crisp teasing, amused superiority, playful provocation.');
}

function Prepend-WriterHeader {
  param(
    [string]$Path,
    [string[]]$CharacterSummary,
    [string[]]$ThemeLines
  )

  $content = Get-Content $Path -Raw
  if ($content.StartsWith('# WRITER BRIEF')) { return }

  $header = @('# WRITER BRIEF') +
    $CharacterSummary.ForEach({ '# ' + $_ }) +
    @(
      '# File purpose: this trigger asset should help a writer generate human-sounding scripted replies for the theme below.',
      '# Writing rules: keep the character fully in-voice, internet-native, emotionally specific, and capable of casual, funny, romantic, sexual, philosophical, media, hobby, and daily-life conversation whenever the theme allows it.',
      '# Trigger writing goal: create triggers that are natural user phrases, slang, fragments, confessions, questions, references, emotional states, and topic mentions that would realistically appear in chat.',
      '# Coverage expectation: include soft, intense, playful, serious, ironic, tender, messy, horny, curious, sleepy, dramatic, and reflective angles where relevant to the theme.',
      '# Trigger format: trigger || script_id || weight || cooldown || attention_cost || mood_shift'
    ) +
    $ThemeLines.ForEach({ '# ' + $_ }) +
    @('# Writer note: when expanding this file, include modern slang, direct statements, indirect hints, jokes, questions, emotional cues, and niche references tied to this theme.', '')

  Set-Content -Path $Path -Value (($header -join "`r`n") + $content) -Encoding UTF8
}

Get-ChildItem "$root\content\personas\lia" -Filter '*.txt' | Where-Object { $_.Name -ne 'scripts.txt' } | ForEach-Object {
  Prepend-WriterHeader -Path $_.FullName -CharacterSummary $liaSummary -ThemeLines $liaThemes[$_.Name]
}

Get-ChildItem "$root\content\personas\yuna" -Filter '*.txt' | Where-Object { $_.Name -ne 'scripts.txt' } | ForEach-Object {
  Prepend-WriterHeader -Path $_.FullName -CharacterSummary $yunaSummary -ThemeLines $yunaThemes[$_.Name]
}
