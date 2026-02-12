---
name: review-feature
description: Review a fully implemented feature to verify all acceptance criteria from the spec are met. Performs holistic end-to-end verification with quality checks. Automatically use when user requests to "review feature", "verify feature", "check feature implementation", "feature review", or "validate feature against spec".
---

# Review Feature

Perform a holistic review of a complete feature implementation to verify all acceptance criteria are satisfied and the feature works end-to-end.

## Core Principle: Zero Assumptions

Never assume when uncertain or when multiple valid options exist. Always ask the user. It's better to ask one extra question than to build a plan on a wrong assumption.

## How to Use This Skill

**Input:** A path to a feature folder: `features/<feature-name>/`
**Output:** Feature review report at `features/<feature-name>/reviews/feature-review.md`, all criteria verified, feature marked as ready or gaps documented.

### Step 1: Verify All Phases Complete

- Read `features/<feature-name>/progress.md` to confirm all phases are done
- If any phases are incomplete, inform the user and **stop**
- List all phase review reports found

### Step 2: Gather All Context

- Read the spec file for all acceptance criteria
- Read `README.md` for feature overview
- Read all phase files and their verification results
- Read the BDD test scenarios (if they exist)
- Collect all deviations documented across phases

### Step 3: Build Acceptance Criteria Checklist

- Extract every acceptance criterion from the spec
- Create a checklist to verify each one
- Include edge cases and error scenarios from the spec

### Step 4: Verify Each Acceptance Criterion (One at a Time)

For each criterion:

1. Explain what is being verified
2. Check the implementation satisfies it
3. Run relevant tests if applicable
4. Use agent-browser for UI criteria

Present result to user using `AskUserQuestion`:
- **Passed**: Criterion is fully met
- **Partial**: Criterion is partially met (explain the gap)
- **Failed**: Criterion is not met

If not passed, ask the user:
- **Fix now**: Address the gap immediately
- **Skip**: Log the gap and continue
- **Stop**: Exit the review

### Step 5: Visual End-to-End Verification (For UI Features)

- Walk through the complete user flow using agent-browser CLI
- Ask for the app URL and login credentials if not already known
- Test the happy path end-to-end
- Test key error scenarios
- Save screenshots to `features/<feature-name>/screenshots/`

### Step 6: Run All Quality Checks

Verify all quality checks pass with zero errors and zero warnings:

- Linting
- Type checking
- Unit tests
- Integration tests
- E2E tests

### Step 7: Review Deviations Impact

- Review all deviations collected across phases
- Verify deviations did not compromise acceptance criteria
- Flag any deviations that need reconsideration

### Step 8: Generate Feature Review Report

Save to `features/<feature-name>/reviews/feature-review.md`:

- All acceptance criteria with pass/fail status
- Coverage summary
- Deviations summary and their impact
- Any gaps or skipped items
- Screenshots of key flows
- Overall assessment: **Ready** or **Needs Work**

### Step 9: Update Progress

- Update `progress.md` with feature review status
- Mark feature as reviewed if all criteria passed

## Output Format

```
features/<feature-name>/reviews/
  feature-review.md    # Complete review report with criteria status and assessment
```

## Important Guidelines

**DO:**
- Verify every single acceptance criterion from the spec — skip none
- Run all quality checks and require zero errors/warnings
- Use agent-browser for visual verification of UI features
- Document all gaps, even skipped ones, in the review report
- Ask the user for each criterion result (Passed/Partial/Failed)

**DON'T:**
- Skip the phase completion check — all phases must be done first
- Assume a criterion passes without verifying it
- Continue past a "Stop" response from the user
- Generate the review report before completing all verification steps
- Ignore deviations — always assess their impact on acceptance criteria
