# Prompt: Create "review-phase" Skill

Create a Claude Code skill called "review-phase" that reviews a completed phase implementation against its plan and spec.

## Core Principle: Zero Assumptions

Never assume when uncertain or when multiple valid options exist. Always ask the user. It's better to ask one extra question than to build a plan on a wrong assumption.

## Goal

Thoroughly review a completed phase to ensure the implementation matches the plan, follows best practices, and meets quality standards. Optionally fix issues during review.

## Reference Files to Create

Before creating the skill, create the following reference files:

1. **Agent-Browser API Reference**
   - Fetch documentation from: https://github.com/vercel-labs/agent-browser
   - Create a reference file with the full API documentation
   - For visual verification when needed

2. **Review Checklist Template**
   - Create a structured review checklist
   - Include sections for: plan alignment, spec compliance, code quality, test quality, security, documentation
   - Add examples of thorough reviews
   - Template should be comprehensive but practical

3. **Security Review Checklist**
   - Create a security-focused review checklist
   - Include: input validation, authentication/authorization, data exposure, injection vulnerabilities, sensitive data handling, error messages leaking info
   - Based on common security best practices

## Input

The skill accepts:
- A path to a feature folder: `features/<feature-name>/`
- Optionally, a specific phase number to review (defaults to last completed phase)

## Process

1. **Identify Phase to Review**
   - Read `progress.md` to find completed phases
   - If specific phase provided, review that phase
   - Otherwise, review the most recently completed phase

2. **Gather Context**
   - Read the phase file
   - Read the related spec for requirements
   - Read the README.md for overall context
   - Review the git diff for changes made in this phase
   - Find similar features in the codebase for comparison

3. **Review Against Plan**
   - Verify all steps in the phase were completed
   - Check files modified match what was planned
   - Identify any deviations and whether they were documented
   - Review if documented deviations were appropriate choices
   - Flag any planned work that wasn't done

4. **Review Against Spec**
   - Verify implementation meets the acceptance criteria
   - Check edge cases are handled
   - Verify error scenarios are addressed

5. **Compare to Similar Features**
   - Compare implementation to similar features in the codebase
   - Check consistency with established patterns
   - Flag any inconsistencies that should be addressed

6. **Code Quality Review**
   - Check code follows existing patterns in the codebase
   - Review for:
     - Code readability and clarity
     - Proper error handling
     - No hardcoded values that should be configurable
     - No performance issues
     - Proper typing (no `any` types, proper interfaces)
   - Flag any workarounds or temporary solutions

7. **Test Quality Review**
   - Review tests are well-written, not just passing
   - Check for:
     - Meaningful test descriptions
     - Edge cases covered
     - Error scenarios tested
     - No flaky test patterns
     - Proper assertions (not just "doesn't throw")
     - Test isolation (no interdependencies)
   - Flag missing test coverage

8. **Security Review**
   - Use security checklist to review for:
     - Input validation on all user inputs
     - Proper authentication/authorization checks
     - No sensitive data exposure in logs or responses
     - Protection against injection attacks
     - Secure handling of credentials/tokens
     - Error messages don't leak internal details
   - Flag any security concerns

9. **Documentation Review**
   - Check code comments are adequate for complex logic
   - Verify any required documentation updates were made
   - Check for misleading or outdated comments
   - Verify function/method documentation where needed

10. **Visual Verification (For UI Changes)**
    - If phase involved UI changes, offer to verify visually
    - If yes, ask for:
      - URL to the app (if not already known)
      - Login credentials if authentication is required (if not already known)
    - Use agent-browser CLI to verify the UI works as expected
    - Compare against spec requirements
    - Save screenshots to `features/<feature-name>/screenshots/` folder

11. **Run Quality Checks**
    - Verify all quality checks still pass:
      - Linting (0 errors, 0 warnings)
      - Type checking (0 errors, 0 warnings)
      - Unit tests (all passing)
      - Integration tests (all passing)
      - E2E tests (all passing)

12. **Report and Handle Findings (One at a Time)**
    - Present ONE finding at a time using AskUserQuestion tool
    - For each finding explain:
      - What the issue is
      - Why it matters
      - Severity: Critical / Major / Minor / Suggestion
      - Suggested fix
    - Ask user how to proceed:
      - **Fix now**: Skill implements the fix immediately
      - **Skip**: Move to next finding (log as skipped)
      - **Stop review**: Exit and address all findings later
    - If user chooses "Fix now":
      - Implement the fix
      - Run relevant quality checks
      - Confirm fix is complete
      - Continue to next finding
    - Log all findings and their resolution in review report

13. **Re-run Quality Checks After Fixes**
    - If any fixes were made, re-run all quality checks
    - Ensure 0 errors, 0 warnings policy is maintained
    - If new issues arise from fixes, report them

14. **Commit Fixes (If Any)**
    - If fixes were made during review, commit them
    - Use commit message: `fix(<feature-name>): review fixes for phase N`
    - Include list of fixes in commit body

15. **Generate Review Report**
    - Save review report to `features/<feature-name>/reviews/phase-N.md`
    - Include:
      - Phase reviewed
      - Review date
      - Findings summary (by severity)
      - Fixed issues
      - Skipped issues (for future reference)
      - Reviewer learnings and observations
    - Mark phase as reviewed in `progress.md`

16. **Capture Learnings**
    - Document any learnings from the review
    - Note patterns to follow or avoid in future phases
    - Add learnings to review report and `progress.md`

## Output

- Review completed
- Review report saved to `features/<feature-name>/reviews/phase-N.md`
- All findings reported with resolution status
- Fixes committed (if any were made)
- `progress.md` updated with review status
- Phase marked as reviewed
- Learnings captured for future reference
