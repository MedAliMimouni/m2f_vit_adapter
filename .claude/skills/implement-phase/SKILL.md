---
name: implement-phase
description: Execute one phase from a broken-down plan, implementing each step while tracking progress for resumption. Automatically use when user requests to "implement phase", "execute phase", "start next phase", "implement the plan", or "continue implementation".
---

# Implement Phase

Execute one phase from a broken-down plan, implementing each step while tracking progress to allow resumption at any point.

## Core Principle: Zero Assumptions

Never assume when uncertain or when multiple valid options exist. Always ask the user. It's better to ask one extra question than to build a plan on a wrong assumption.

## Quality Policy

**Strict 0 errors / 0 warnings policy.** All quality checks must pass with zero errors and zero warnings. Fix everything before completing the phase.

**No workarounds or temporary solutions:**
- No `// TODO: fix later` comments
- No `eslint-disable` or similar rule disabling
- No `@ts-ignore` or type assertions to hide issues
- No `.skip` on tests or temporary implementations
- If a proper solution isn't clear, ask the user

**Tests are part of the deliverables:**
- Add unit tests when implementing functions/methods with clear inputs/outputs
- Add integration tests when connecting components/services
- E2e tests are deferred until all phases are complete (use implement-e2e skill)
- Use judgment: test what's stable and valuable now, defer what's still in flux

## How to Use This Skill

**Input:** A path to a feature folder: `features/<feature-name>/`
**Output:** One phase implemented, all checks passing, committed, `progress.md` updated.

### Process

1. **Read Progress** - Read `phases/progress.md` (or create from [references/progress-template.md](references/progress-template.md) if missing, starting at phase 1). Read README.md and related spec for context.

2. **Verify Branch Strategy** - On first phase (no phases completed): create `feature/<feature-name>` branch automatically. On later phases if on main/master: ask user before proceeding.

3. **Read Current Phase File** - Read the phase file, understand objective and steps, check entry criteria are met. If entry criteria fail, inform user and stop (offer to proceed with warning).

4. **Check Dependencies** - If new packages/dependencies are needed, list them and ask user for confirmation before installing. Commit dependency changes separately.

5. **Explore Codebase** - Find existing patterns, similar implementations, files to modify, and identify quality check commands (lint, typecheck, test, e2e).

6. **Gather External Docs (When Needed)** - If implementation involves unfamiliar libraries, ask user for documentation links. Only ask when genuinely needed.

7. **Implement Step by Step**
   - If change aligns with plan: implement without asking
   - If change deviates from plan: explain why, ask confirmation, log deviation
   - After each step:
     - Write tests (unit/integration as appropriate)
     - Update `progress.md` to mark step complete
     - Run relevant tests to verify
     - Capture learnings in `progress.md`
   - If blocked: ask user, present options with pros/cons, log blocker
   - **NEVER** implement workarounds of any kind

8. **Run All Quality Checks** - Linting, type checking, unit tests, integration tests, e2e tests (existing only). All must pass with 0 errors and 0 warnings. Fix issues and re-run until clean.

9. **Run Verification Steps** - Execute all verification steps from the phase file. Report results. If any fail, discuss with user.

10. **Commit Changes** - Format: `feat(<feature-name>): complete phase N - <phase-name>` with summary in commit body.

11. **Complete Phase** - Update phase status to `done`, update `progress.md` and phases README. Report deviations, learnings, and next phase info.

## Important Guidelines

**DO:**
- Resume from exactly where progress.md indicates
- Ask before installing any dependency
- Log every deviation, blocker, and learning in progress.md
- Run ALL quality checks before marking phase complete
- Write tests alongside implementation, not after

**DON'T:**
- Skip entry criteria verification
- Implement workarounds or temporary solutions
- Proceed on main/master without user confirmation
- Commit without all checks passing (0 errors, 0 warnings)
- Write e2e tests during phases (deferred to implement-e2e skill)
- Assume anything when multiple valid options exist
