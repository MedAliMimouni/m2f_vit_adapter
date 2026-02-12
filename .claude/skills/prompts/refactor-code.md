# Prompt: Create "refactor-code" Skill

Create a Claude Code skill called "refactor-code" that improves code quality without changing functionality, following the scout-boy rule.

## Core Principle: Zero Assumptions

Never assume when uncertain or when multiple valid options exist. Always ask the user. It's better to ask one extra question than to build a plan on a wrong assumption.

## Quality Policy

**Strict 0 errors / 0 warnings policy.** All quality checks must pass with zero errors and zero warnings.

**No functionality changes.** Refactoring must preserve existing behavior. All tests must continue to pass.

**No workarounds or temporary solutions.** Every refactoring must be proper and complete.

## Goal

Improve code quality in a targeted area - make it more readable, testable, maintainable, or modular - without changing its behavior.

## Reference Files to Create

Before creating the skill, create the following reference files:

1. **Refactoring Catalog**
   - Create a reference file with common refactoring patterns
   - Include: Extract Function, Rename, Extract Variable, Inline, Move, Split Loop, Replace Conditional with Polymorphism, etc.
   - Add examples of before/after for each pattern
   - Note when each pattern is appropriate

2. **Agent-Browser API Reference**
   - Fetch documentation from: https://github.com/vercel-labs/agent-browser
   - Create a reference file with the full API documentation
   - For visual verification of UI components

## Input

The skill accepts:
- A path to a file or folder to refactor
- Optionally, a specific refactoring goal (e.g., "improve testability", "extract utilities", "simplify logic")

## Process

1. **Read and Understand the Code**
   - Read the target file(s) thoroughly
   - Understand the current functionality
   - Identify existing tests that cover this code
   - Note any code smells or areas for improvement

2. **Check Test Coverage**
   - Verify adequate test coverage exists for the code to be refactored
   - If coverage is insufficient:
     - Inform the user
     - Offer to add tests first before refactoring
     - If user agrees, write tests for current behavior
     - If user declines, warn about risk and ask for confirmation to proceed
   - Do not refactor untested code without explicit user approval

3. **Check for Breaking Changes**
   - Identify if the code is exported/public API
   - If refactoring might affect external consumers:
     - Warn the user about potential breaking changes
     - List what might break (function signatures, exports, etc.)
     - Ask for confirmation before proceeding
   - For internal code, proceed normally

4. **Explore the Codebase for Patterns**
   - Find similar code in the codebase
   - Understand established patterns and conventions
   - Identify utilities or abstractions that could be reused
   - Note how similar problems were solved elsewhere

5. **Identify Refactoring Opportunities**
   - Analyze the code for:
     - **Readability**: Unclear naming, complex conditionals, long functions
     - **Testability**: Hard-to-test code, tight coupling, hidden dependencies
     - **Maintainability**: Duplication, magic numbers, missing abstractions
     - **Modularity**: Large files, mixed concerns, poor separation
   - Prioritize by impact and risk

6. **Propose Refactorings (One at a Time)**
   - Present ONE refactoring at a time using AskUserQuestion tool
   - For each refactoring explain:
     - What will be changed
     - Why it improves the code
     - Risk level (low/medium/high)
     - Files that will be affected (including related files that import/use this code)
     - Before/after example if helpful
   - Ask user to:
     - **Approve**: Proceed with this refactoring
     - **Skip**: Move to next opportunity
     - **Stop**: End the refactoring session
   - There is NO LIMIT on the number of refactorings - continue until user stops or no more opportunities

7. **Implement Approved Refactoring**
   - Make the change in the target file
   - Update all related files that use/import the refactored code
   - Ensure no functionality is changed
   - Run all tests to verify behavior is preserved
   - If tests fail, revert and discuss with user

8. **Visual Verification (For UI Components)**
   - If refactoring UI components, offer to verify visually
   - If yes, ask for:
     - URL to the app (if not already known)
     - Login credentials if authentication is required (if not already known)
   - Use agent-browser CLI to verify UI looks and works the same
   - Save before/after screenshots to compare
   - If visual differences detected, revert and discuss with user

9. **Run All Quality Checks**
   - After each refactoring:
     - Linting (0 errors, 0 warnings)
     - Type checking (0 errors, 0 warnings)
     - Unit tests (all passing)
     - Integration tests (all passing)
     - E2E tests (all passing)
   - Fix any issues before proceeding to next refactoring

10. **Commit This Refactoring**
    - Commit after each successful refactoring (easier to revert if issues found later)
    - Use commit message: `refactor(<scope>): <specific change>`
    - Example: `refactor(auth): extract token validation to utility function`

11. **Capture Learnings**
    - Note any patterns discovered during refactoring
    - Document useful abstractions or utilities created
    - Record insights about the codebase for future reference

12. **Continue or Stop**
    - After successful refactoring, return to step 6 for next opportunity
    - Continue until user stops or no more opportunities

13. **Summary**
    - Provide summary of all refactorings made
    - List commits created
    - Share learnings captured
    - Note any remaining opportunities that were skipped

## Output

- Code refactored with improved quality
- Related files updated consistently
- All tests passing (behavior preserved)
- All quality checks passing (0 errors, 0 warnings)
- One commit per refactoring (easy to revert)
- Learnings documented
- Summary of improvements made
