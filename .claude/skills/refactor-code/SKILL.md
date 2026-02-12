---
name: refactor-code
description: Improve code quality without changing functionality, following the scout-boy rule. Automatically use when user requests to "refactor code", "improve code quality", "clean up code", "refactor this file", or "make code more readable".
---

# Refactor Code

Improve code quality in a targeted area — make it more readable, testable, maintainable, or modular — without changing its behavior.

## Core Principle: Zero Assumptions

Never assume when uncertain or when multiple valid options exist. Always ask the user. It's better to ask one extra question than to build a plan on a wrong assumption.

## Quality Policy

**Strict 0 errors / 0 warnings policy.** All quality checks must pass with zero errors and zero warnings.

**No functionality changes.** Refactoring must preserve existing behavior. All tests must continue to pass.

**No workarounds or temporary solutions.** Every refactoring must be proper and complete.

## How to Use This Skill

**Input:** A path to a file or folder to refactor. Optionally, a specific goal (e.g., "improve testability", "extract utilities", "simplify logic").
**Output:** Code refactored, all tests passing, one commit per refactoring, learnings documented, summary of improvements.

### Step 1: Read and Understand the Code

- Read the target file(s) thoroughly
- Understand the current functionality and its role in the codebase
- Note any code smells or areas for improvement

### Step 2: Check Test Coverage

- Verify adequate test coverage exists for the code to be refactored
- If coverage is insufficient:
  - Inform the user
  - Offer to add tests first before refactoring
  - If user declines, warn about risk and ask for explicit confirmation
- **Do not refactor untested code without explicit user approval**

### Step 3: Check for Breaking Changes

- Identify if the code is exported or part of a public API
- If refactoring might affect external consumers:
  - Warn the user about potential breaking changes
  - List what might break (function signatures, exports, etc.)
  - Ask for confirmation before proceeding
- For internal code, proceed normally

### Step 4: Explore Codebase for Patterns

- Find similar code in the codebase
- Understand established patterns and conventions
- Identify utilities or abstractions that could be reused

### Step 5: Identify Refactoring Opportunities

Analyze the code for:
- **Readability**: Unclear naming, complex conditionals, long functions
- **Testability**: Tight coupling, hidden dependencies, hard-to-test code
- **Maintainability**: Duplication, magic numbers, missing abstractions
- **Modularity**: Large files, mixed concerns, poor separation

Prioritize by impact and risk. See [references/refactoring-catalog.md](references/refactoring-catalog.md) for common patterns.

### Step 6: Propose Refactorings (One at a Time)

Present ONE refactoring at a time using `AskUserQuestion`. For each, explain:
- **What** will be changed
- **Why** it improves the code
- **Risk level**: low / medium / high
- **Affected files** (including files that import/use this code)
- **Before/after** example if helpful

Options: **Approve** / **Skip** / **Stop**

There is **no limit** on refactorings — continue until user stops or no more opportunities.

### Step 7: Implement Approved Refactoring

- Make the change in the target file
- Update all related files that use/import the refactored code
- Ensure no functionality is changed
- Run all tests to verify behavior is preserved
- If tests fail, **revert and discuss** with the user

### Step 8: Visual Verification (UI Components Only)

- If refactoring UI components, offer to verify visually using agent-browser
- Save before/after screenshots to compare
- If visual differences detected, **revert and discuss** with the user

### Step 9: Run All Quality Checks

After each refactoring, run and verify:
- Linting (0 errors, 0 warnings)
- Type checking (0 errors, 0 warnings)
- Unit tests (all passing)
- Integration tests (all passing)
- E2E tests (all passing)

Fix any issues before proceeding to next refactoring.

### Step 10: Commit Each Refactoring Separately

- Commit after each successful refactoring
- Format: `refactor(<scope>): <specific change>`
- Example: `refactor(auth): extract token validation to utility function`

### Step 11: Capture Learnings

- Note patterns discovered, useful abstractions created, and codebase insights

### Step 12: Continue or Stop

- Return to Step 6 for the next opportunity; continue until user stops or no more opportunities

### Step 13: Summary

- All refactorings made, commits created, learnings captured, remaining skipped opportunities

## Important Guidelines

**DO:**
- Propose one refactoring at a time and wait for approval
- Run all quality checks after every change
- Commit each refactoring separately for easy revert
- Check test coverage before refactoring
- Update all files that reference refactored code

**DON'T:**
- Change functionality — refactoring is behavior-preserving
- Skip the user approval loop for any refactoring
- Refactor untested code without explicit user consent
- Batch multiple refactorings into one commit
- Ignore lint or type errors introduced by a refactoring
