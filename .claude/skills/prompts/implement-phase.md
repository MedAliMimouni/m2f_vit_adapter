# Prompt: Create "implement-phase" Skill

Create a Claude Code skill called "implement-phase" that takes a phases folder and implements the next phase, tracking progress automatically.

## Core Principle: Zero Assumptions

Never assume when uncertain or when multiple valid options exist. Always ask the user. It's better to ask one extra question than to build a plan on a wrong assumption.

## Quality Policy

**Strict 0 errors / 0 warnings policy.** All quality checks must pass with zero errors and zero warnings, even if issues appear unrelated to the current changes. Fix everything before completing the phase.

**No workarounds or temporary solutions.** Every implementation must be proper and complete. No hacks, no "fix later" comments, no disabling rules, no skipping tests. If a proper solution isn't clear, ask the user - don't implement a shortcut.

**Tests are part of the deliverables.** Adding unit and integration tests is not optional - it's part of completing each step. Write tests as soon as it makes sense:
- Add unit tests when implementing functions/methods with clear inputs/outputs
- Add integration tests when connecting components/services
- **E2e tests are deferred** until all phases are complete (use the implement-e2e skill after feature review)
- However, don't write tests that:
  - Don't add real value (testing trivial getters/setters)
  - Will completely change in the next phases (test the stable parts first)
- Use judgment: test what's stable and valuable now, defer what's still in flux

## Goal

Execute one phase from a broken-down plan, implementing each step while tracking progress to allow resumption.

## Reference Files to Create

Before creating the skill, create the following reference files:

1. **Agent-Browser API Reference**
   - Fetch documentation from: https://github.com/vercel-labs/agent-browser
   - Create a reference file with the full API documentation
   - For visual exploration and debugging when needed

2. **Progress Template**
   - Create a reference file for progress.md structure
   - Include sections for: current phase, completed phases, step progress, deviations, blockers, learnings
   - Add examples of well-maintained progress files
   - Template should support resume from any point

## Input

The skill accepts:
- A path to a feature folder: `features/<feature-name>/`

## Progress Tracking

The skill uses `features/<feature-name>/phases/progress.md` to track execution state:
- Which phases are complete
- Current phase in progress
- Which steps within current phase are done
- Any blockers or notes
- Any deviations from the plan
- Learnings captured during implementation

If `progress.md` doesn't exist, create it and start from phase 1.
If it exists, resume from where it left off.

## Process

1. **Read Progress and Determine Starting Point**
   - Read `progress.md` if it exists
   - Identify which phase to start/resume
   - Read the README.md for overall context
   - Read the related spec for requirements context

2. **Verify Branch Strategy**
   - Check if on a feature branch
   - If this is the first phase (no phases completed yet):
     - Automatically create a feature branch: `feature/<feature-name>`
     - Inform the user the branch was created
   - If not first phase and on main/master:
     - Ask user if they want to create a feature branch
     - Do not proceed on main/master without explicit user confirmation

3. **Read Current Phase**
   - Read the phase file to implement
   - Understand the objective and steps
   - Check entry criteria are met

4. **Verify Entry Criteria**
   - Check all entry criteria are satisfied
   - If not, inform user what's missing and stop
   - Ask user if they want to proceed anyway (with warning)

5. **Check Dependencies**
   - Identify if phase requires new dependencies (npm packages, etc.)
   - If new dependencies needed:
     - List them and ask user for confirmation before installing
     - Install dependencies
     - Commit dependency changes separately

6. **Explore the Codebase**
   - Understand existing patterns for the files to be modified
   - Find similar implementations to follow as reference
   - Verify files to modify exist as expected
   - Identify quality check commands used in this project (lint, typecheck, test, e2e)

7. **Gather External Documentation (When Needed)**
   - If implementation involves unfamiliar libraries or frameworks
   - Ask the user for documentation links when it would help
   - Only ask when genuinely needed
   - Use documentation to ensure correct implementation

8. **Implement Step by Step**
   - Work through each step in order
   - If change aligns with the plan:
     - Implement without asking for confirmation
   - If change deviates from the plan:
     - Explain the deviation and why it's needed
     - Ask for confirmation using AskUserQuestion tool
     - Log the deviation in `progress.md`
   - After each step:
     - Write tests for the implemented code (unit/integration/e2e as appropriate)
     - Update `progress.md` to mark step complete
     - Run relevant tests to verify
     - Verify the step is complete
     - Capture any learnings in `progress.md`
   - If blocked or uncertain:
     - Ask the user using AskUserQuestion tool
     - Present options with pros/cons
     - Log blocker in `progress.md`
     - Never guess or assume
   - Never implement workarounds:
     - No `// TODO: fix later` comments
     - No `eslint-disable` or similar rule disabling
     - No `@ts-ignore` or type assertions to hide issues
     - No skipping or `.skip` on tests
     - No temporary implementations

9. **Visual Exploration / Debugging (When Needed)**
   - Use browser automation when:
     - Implementing UI changes that need visual verification
     - Debugging failing e2e tests
     - Understanding current UI behavior
   - If needed, ask for:
     - URL to the app (if not already known)
     - Login credentials if authentication is required (if not already known)
   - Use agent-browser CLI to explore and debug
   - Save screenshots to `features/<feature-name>/screenshots/` folder when helpful
   - Skip for backend-only phases

10. **Run All Quality Checks**
    - Run all quality checks based on the project's framework and language:
      - Linting (0 errors, 0 warnings)
      - Type checking (0 errors, 0 warnings)
      - Unit tests (all passing)
      - Integration tests (all passing)
      - E2E tests (all existing tests must pass - don't break existing e2e tests)
    - If any check fails:
      - Fix the issues properly, even if they appear unrelated to current changes
      - Use browser automation to debug failing e2e tests if needed
      - Re-run checks until all pass
      - Update `progress.md` with any fixes made
    - Do NOT proceed until all checks pass with 0 errors and 0 warnings
    - Note: New e2e tests are written after all phases are complete (implement-e2e skill)

11. **Run Verification Steps**
    - Execute all verification steps from the phase file
    - Report results to user
    - If any fail, discuss with user how to proceed

12. **Commit Changes**
    - After all checks pass, commit the changes
    - Use a descriptive commit message referencing the phase
    - Format: `feat(<feature-name>): complete phase N - <phase-name>`
    - Include summary of what was implemented in commit body

13. **Complete Phase**
    - Only if all quality checks AND verification steps pass:
      - Update phase file status to `done`
      - Update `progress.md` to mark phase complete
      - Update README.md status tracker
    - Summarize what was accomplished
    - **Report all deviations from the plan** (if any):
      - List each deviation
      - Explain why it was needed
      - Note if it affects future phases
    - **Report learnings** captured during implementation
    - Inform user of next phase (if any)

## Output

- One phase implemented with all steps completed
- All quality checks passing (0 errors, 0 warnings)
- Changes committed to feature branch
- `progress.md` updated with current state, deviations, and learnings
- Phase status updated to `done`
- Deviations report (if any)
- Learnings summary
- Can be run again to implement the next phase
