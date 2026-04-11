# Mythic Relay - Stakeholder One-Pager

## Goal
Mythic Relay is an automation system that receives engineering requests from GitHub and drives them to completion with transparent progress and risk controls.

## Business value
- Reduce turnaround time for repetitive issue and PR tasks.
- Standardize how work is tracked and communicated.
- Increase automation while preserving safety gates.
- Keep an auditable history for operations and leadership.

## What the system does
- Accepts requests from GitHub comments (for example `/ai ...`).
- Selects the right backend agent for execution.
- Creates and updates a dedicated progress comment during the run.
- Pauses for explicit confirmation on risky actions (`/ai yes` or `/ai no`).
- Supports run cancellation (`/ai cancel`).
- Supports trusted label-based and scheduled triggers.
- Persists run memory so future runs can continue with context.

## High-level operating flow
1. Receive trigger from comment, label, or schedule.
2. Validate trust and classify request type.
3. Evaluate risk (auto-run vs confirmation required).
4. Execute agent and continuously update progress.
5. Checkpoint work safely on dedicated branches.
6. Finalize with clear outcome: completed, failed, or cancelled.

## Safety and governance
- Trusted-actor validation for sensitive triggers.
- Confirmation gates for risky/destructive/security-impacting actions.
- Checkpointing to avoid progress loss between runs.
- Standardized logs and metrics for observability and audits.

## Expected outcomes
- Faster engineering response cycles.
- Less manual workflow overhead in GitHub.
- Better SLA consistency for issue and PR handling.
- Clear accountability with transparent progress visibility.
