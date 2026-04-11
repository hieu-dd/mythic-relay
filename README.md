# Mythic Relay

Mythic Relay turns trusted GitHub requests into automated engineering execution with clear progress, safety gates, and reliable outcomes.

## What it does
- Handles `/ai ...` requests from issues and PRs
- Routes to the selected backend agent
- Tracks work in a single progress comment
- Uses confirmation gates for risky actions (`/ai yes`, `/ai no`)
- Supports cancellation (`/ai cancel`)
- Preserves progress with WIP and memory checkpoints

## Docs
- `docs/handoff-spec.md`
- `docs/stakeholder-onepager.md`
