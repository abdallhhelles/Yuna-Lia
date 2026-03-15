# Roadmap

## Near Term

- Move more swallowed exceptions to structured warnings with context.
- Add test coverage for dual-bot startup, ambient scheduling, and slash command handlers.
- Add log rotation or pruning for long-lived deployments.

## Mid Term

- Migrate JSON runtime state to SQLite for stronger integrity and better queryability.
- Add guild-level configuration so each server can tune intensity, pacing, and allowed themes.
- Expand analytics into server and channel dashboards instead of only global counters.
- Add moderator controls for enabling or muting certain systems.

## Long Term

- Support multi-server isolation with per-guild memory partitions and configurable content packs.
- Introduce seasonality systems: arcs, rivalries, callbacks, and server-specific lore progression.
- Build retention mechanics around streaks, unlockable scenes, recurring events, and community milestones.
