---
name: implement-e2e
description: Implement e2e tests based on approved BDD test scenarios, ensuring all acceptance criteria are covered by automated tests. Automatically use when user requests to "implement e2e tests", "write e2e tests", "create end-to-end tests", "add e2e tests", or "implement BDD scenarios".
---

# Implement E2E

Implement end-to-end tests from approved BDD scenarios, producing reliable, maintainable test suites with full coverage.

## Core Principle: Zero Assumptions

Never assume when uncertain or when multiple valid options exist. Always ask the user. It's better to ask one extra question than to build a plan on a wrong assumption.

## Quality Policy

**Strict 0 errors / 0 warnings policy.** All quality checks must pass with zero errors and zero warnings.

**No workarounds or temporary solutions.** No flaky tests, no skipped tests, no hardcoded waits.

## How to Use This Skill

**Input:** A path to a feature folder: `features/<feature-name>/` (with `test-plan.md` from the plan-tests skill)
**Output:** E2e tests implemented, page objects/fixtures/utilities created, all tests passing, coverage mapping updated, committed.

### Step 1: Read and Understand Test Scenarios

- Read `test-plan.md` and related BDD scenarios thoroughly
- Understand preconditions, scenarios, and example data
- Read the related spec for additional context
- Review the coverage mapping to acceptance criteria

### Step 2: Explore the Codebase for Testing Patterns

- Find existing e2e tests in the codebase
- Identify the testing framework (Playwright, Cypress, etc.)
- Identify existing page objects, test utilities, helpers, and fixtures
- Note naming conventions and file organization

### Step 3: Visual Exploration

- Use agent-browser to understand the implemented UI
- Ask the user for the app URL and login credentials if not already known
- Walk through each scenario manually first
- Identify selectors and interaction patterns
- Save screenshots to `features/<feature-name>/screenshots/` for reference

### Step 4: Clarify Implementation Details (Interview Style)

Ask **ONE question at a time** using the `AskUserQuestion` tool:

- Clarify ambiguities in scenarios
- Confirm test data setup/teardown requirements
- Confirm selector strategy (data-testid, aria roles, etc.)

There is **no limit** on questions -- ask as many as needed.

### Step 5: Create/Update Page Objects

- Create or update page objects for pages/components in the scenarios
- Follow existing page object patterns in the codebase
- Include: element selectors (prefer `data-testid` or aria roles), action methods, assertion helpers, wait methods for dynamic content

### Step 6: Create/Update Test Data Fixtures

- Create reusable fixtures for user accounts, entity data, and edge cases
- Follow existing fixture patterns; ensure fixtures are isolated (no production data dependency)
- Include setup and teardown as needed

### Step 7: Create/Update Reusable Test Utilities

- Create or update utilities for: auth helpers, navigation, common assertions, data generation, API helpers for test setup
- Follow existing utility patterns; avoid duplication

### Step 8: Implement Tests Scenario by Scenario

For each scenario in order:

- Use page objects for interactions, fixtures for data, utilities for common operations
- Implement Given/When/Then steps with meaningful assertions
- Handle preconditions properly

**Avoid:** hardcoded waits (use proper wait strategies), flaky selectors (no positional/index-based), test interdependencies (each test must be isolated), code duplication

### Step 9: Run and Verify Tests

- Run each test after implementation; verify it passes consistently (run multiple times)
- If a test fails, debug using browser automation; fix the test or report the UI issue to the user
- Ensure no flakiness

### Step 10: Run All Quality Checks

- Linting (0 errors, 0 warnings)
- Type checking (0 errors, 0 warnings)
- All e2e tests (new and existing must pass)
- Fix any issues before proceeding

### Step 11: Update Coverage Mapping

- Update `test-plan.md` to mark which scenarios now have e2e tests
- Note the test file and test name for each scenario

### Step 12: Commit Changes

- Commit message: `test(<feature-name>): add e2e tests`
- Include summary of scenarios covered and new page objects/fixtures/utilities in commit body

## Important Guidelines

**DO:**
- Prefer `data-testid` or aria roles for selectors
- Make each test independently runnable (isolated setup/teardown)
- Run tests multiple times to catch flakiness
- Reuse existing page objects, fixtures, and utilities

**DON'T:**
- Use hardcoded waits (`sleep`, fixed timeouts)
- Skip tests or mark them as `.todo`/`.skip`
- Create tests that depend on other tests' state
- Duplicate code across test files (extract to page objects/utilities)
- Proceed without reading `test-plan.md` first
