# Prompt: Create "review-feature" Skill

Create a Claude Code skill called "review-feature" that reviews a fully implemented feature to ensure all acceptance criteria from the spec are met.

## Core Principle: Zero Assumptions

Never assume when uncertain or when multiple valid options exist. Always ask the user. It's better to ask one extra question than to build a plan on a wrong assumption.

## Goal

Perform a holistic review of the complete feature implementation to verify all acceptance criteria are satisfied and the feature works end-to-end.

## Reference Files to Create

Before creating the skill, create the following reference files:

1. **Agent-Browser API Reference**
   - Fetch documentation from: https://github.com/vercel-labs/agent-browser
   - Create a reference file with the full API documentation
   - For visual verification of the complete feature

## Input

The skill accepts:
- A path to a feature folder: `features/<feature-name>/`

## Process

1. **Verify All Phases Complete**
   - Read `progress.md` to confirm all phases are done
   - If any phases incomplete, inform user and stop
   - List all phase review reports

2. **Gather All Context**
   - Read the spec file for all acceptance criteria
   - Read the README.md for feature overview
   - Read all phase files and their verification results
   - Read the BDD test scenarios (if exists)
   - Collect all deviations documented across phases

3. **Build Acceptance Criteria Checklist**
   - Extract every acceptance criterion from the spec
   - Create a checklist to verify each one
   - Include edge cases and error scenarios from spec

4. **Verify Each Acceptance Criterion (One at a Time)**
   - For each criterion:
     - Explain what's being verified
     - Check the implementation satisfies it
     - Run relevant tests if applicable
     - Use browser automation for UI criteria
   - Present result to user using AskUserQuestion:
     - **Passed**: Criterion is fully met
     - **Partial**: Criterion is partially met (explain gap)
     - **Failed**: Criterion is not met
   - If not passed, ask user:
     - **Fix now**: Address the gap
     - **Skip**: Log and continue
     - **Stop**: Exit review

5. **Visual End-to-End Verification (For UI Features)**
   - Walk through the complete user flow
   - Ask for:
     - URL to the app (if not already known)
     - Login credentials if authentication is required (if not already known)
   - Use agent-browser CLI to verify full feature works
   - Test happy path end-to-end
   - Test key error scenarios
   - Save screenshots to `features/<feature-name>/screenshots/` folder

6. **Run All Quality Checks**
   - Verify all quality checks pass:
     - Linting (0 errors, 0 warnings)
     - Type checking (0 errors, 0 warnings)
     - Unit tests (all passing)
     - Integration tests (all passing)
     - E2E tests (all passing)

7. **Review Deviations Impact**
   - Review all deviations across phases
   - Verify deviations didn't compromise acceptance criteria
   - Flag any deviations that need reconsideration

8. **Generate Feature Review Report**
   - Save to `features/<feature-name>/reviews/feature-review.md`
   - Include:
     - All acceptance criteria with pass/fail status
     - Coverage summary
     - Deviations summary and their impact
     - Any gaps or skipped items
     - Screenshots of key flows
     - Overall assessment: Ready / Needs Work

9. **Update Progress**
   - Update `progress.md` with feature review status
   - Mark feature as reviewed if all criteria passed

## Output

- Feature review completed
- Report saved to `features/<feature-name>/reviews/feature-review.md`
- All acceptance criteria verified with status
- Feature marked as ready (or gaps documented)
