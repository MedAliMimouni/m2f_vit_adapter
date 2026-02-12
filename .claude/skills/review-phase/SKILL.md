---
name: review-phase
description: Review a completed phase implementation against its plan and spec. Thoroughly checks code quality, tests, security, and documentation. Automatically use when user requests to "review phase", "check phase implementation", "verify phase", "review completed phase", or "phase review".
---

# Review Phase

Thoroughly review a completed phase to ensure the implementation matches the plan, follows best practices, and meets quality standards. Optionally fix issues during review.

## Core Principle: Zero Assumptions

Never assume when uncertain or when multiple valid options exist. Always ask the user. It's better to ask one extra question than to build a plan on a wrong assumption.

## How to Use This Skill

**Input:** A path to a feature folder: `features/<feature-name>/`, and optionally a specific phase number (defaults to last completed phase from `progress.md`).
**Output:** A review report at `features/<feature-name>/reviews/phase-N.md`, fixes committed, and `progress.md` updated with review status.

### Step 1: Identify Phase to Review

- Read `progress.md` to find completed phases
- If a specific phase number is provided, review that phase
- Otherwise, review the most recently completed phase
- If no completed phases exist, inform the user and stop

### Step 2: Gather Context

- Read the phase file (`phases/phase-N-<name>.md`)
- Read the related spec (`spec.md`) for requirements and acceptance criteria
- Read the `README.md` for overall feature context
- Review the git diff for changes made in this phase
- Find similar features in the codebase for pattern comparison

### Step 3: Review Against Plan

- Verify all steps in the phase were completed
- Check files modified match what was planned
- Identify any deviations and whether they were documented
- Flag any planned work that was not done

### Step 4: Review Against Spec

- Verify implementation meets the acceptance criteria
- Check edge cases are handled
- Verify error scenarios are addressed

### Step 5: Compare to Similar Features

- Compare implementation to similar features in the codebase
- Check consistency with established patterns
- Flag inconsistencies that should be addressed

### Step 6: Code Quality Review

Use [references/review-checklist.md](references/review-checklist.md) for detailed checks:
- Code readability and clarity
- Proper error handling
- No hardcoded values that should be configurable
- Proper typing (no `any` types, proper interfaces)
- No performance issues or workarounds

### Step 7: Test Quality Review

- Meaningful test descriptions
- Edge cases and error scenarios covered
- No flaky test patterns
- Proper assertions (not just "doesn't throw")
- Test isolation (no interdependencies)

### Step 8: Security Review

Use [references/security-checklist.md](references/security-checklist.md) for detailed checks:
- Input validation on all user inputs
- Proper authentication/authorization checks
- No sensitive data exposure in logs or responses
- Protection against injection attacks
- Secure handling of credentials/tokens
- Error messages do not leak internal details

### Step 9: Documentation Review

- Code comments adequate for complex logic
- Required documentation updates were made
- No misleading or outdated comments

### Step 10: Visual Verification (UI Changes Only)

- If the phase involved UI changes, offer to verify visually
- If user agrees, use `agent-browser` CLI to verify the UI
- Save screenshots to `features/<feature-name>/screenshots/`

### Step 11: Run All Quality Checks

Run and verify all pass with **0 errors, 0 warnings**:
- Linting, Type checking, Unit tests, Integration tests, E2E tests

### Step 12: Present Findings One at a Time

Use `AskUserQuestion` for **each** finding individually:
- Explain what the issue is and why it matters
- Severity: **Critical** / **Major** / **Minor** / **Suggestion**
- Provide a suggested fix
- Options: **Fix now** / **Skip** / **Stop review**
- If "Fix now": implement fix, run relevant checks, confirm, continue
- Log all findings and resolutions in the review report

### Step 13: Post-Fix Verification

- If any fixes were made, re-run all quality checks (Step 11)
- Ensure 0 errors, 0 warnings policy is maintained
- Report any new issues introduced by fixes

### Step 14: Commit and Report

- If fixes were made, commit: `fix(<feature-name>): review fixes for phase N`
- Generate review report to `features/<feature-name>/reviews/phase-N.md`
- Update `progress.md` with review status and learnings
- Capture patterns to follow or avoid in future phases

## Important Guidelines

**DO:**
- Present findings ONE at a time — never dump a full list
- Run all quality checks before and after fixes
- Document all deviations found, even if skipped
- Compare against similar features for consistency
- Capture learnings for future phases

**DON'T:**
- Skip the quality checks — always run lint, typecheck, and tests
- Auto-fix without user approval — always ask first
- Assume a phase is complete without checking `progress.md`
- Ignore minor issues — log them even if severity is low
- Proceed without reading the spec and plan first
