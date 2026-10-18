# Changelog

## 0.2.0 — 2026-10-17

First standalone release (split out of a combined portfolio folder).

### Fixed
- World Memory: a newer contradicting observation now outweighs an older, more confident
  one (`contradiction_discount`). Before, the README's own `mug` example returned the stale
  value.
- Guardian: a rule that raises (for example on a malformed parameter) now denies the
  action with `rule_error:<rule>` instead of crashing the caller.
- FleetMind: robot load (`active_tasks`) is now tracked on allocation, release and
  reassignment, so the load term in the bid has an effect. Unknown robots are treated as
  unhealthy instead of raising `KeyError`.

### Added
- 11 tests (20 in total) covering the fixes, e-stop, NaN sensor input, audit sequencing,
  low battery and partial missions.
- CI on Python 3.11–3.13, including the end-to-end demo.

## 0.1.0 — 2026-06

Initial reference implementations of Guardian, TaskForge, World Memory and FleetMind.
