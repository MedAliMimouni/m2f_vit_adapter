# Prompt: Create "implement-e2e" Skill

Create a Claude Code skill called "implement-e2e" that takes a BDD test scenarios file and implements e2e tests for the feature.

## Core Principle: Zero Assumptions

Never assume when uncertain or when multiple valid options exist. Always ask the user. It's better to ask one extra question than to build a plan on a wrong assumption.

## Quality Policy

**Strict 0 errors / 0 warnings policy.** All quality checks must pass with zero errors and zero warnings.

**No workarounds or temporary solutions.** Every test must be proper and complete. No flaky tests, no skipped tests, no hardcoded waits.

## Goal

Implement e2e tests based on approved BDD test scenarios, ensuring all acceptance criteria are covered by automated tests.

## Reference Files to Create

Before creating the skill, create the following reference files:

1. **Agent-Browser API Reference**
   - Fetch documentation from: https://github.com/vercel-labs/agent-browser
   - Create a reference file with the full API documentation
   - For understanding current UI behavior while writing tests

## Input

The skill accepts:
- A path to a feature folder: `features/<feature-name>/` (with test-plan.md)

## Process

1. **Read and Understand Test Scenarios**
   - Read the BDD scenarios file thoroughly
   - Understand preconditions, scenarios, and example data
   - Read the related spec for additional context
   - Review the coverage mapping to acceptance criteria

2. **Explore the Codebase for Testing Patterns**
   - Find existing e2e tests in the codebase
   - Understand the testing framework used (Playwright, Cypress, etc.)
   - Identify existing page objects and their patterns
   - Identify existing test utilities and helpers
   - Identify existing test data fixtures
   - Note naming conventions and file organization

3. **Visual Exploration**
   - Use browser automation to understand the implemented UI
   - Ask for:
     - URL to the app (if not already known)
     - Login credentials if authentication is required (if not already known)
   - Walk through each scenario manually first
   - Identify selectors and interaction patterns
   - Save screenshots to `features/<feature-name>/screenshots/` folder for reference

4. **Clarify Implementation Details (Interview Style)**
   - Ask ONE question at a time using AskUserQuestion tool
   - Clarify any ambiguities in scenarios
   - Ask about test data setup/teardown requirements
   - Confirm selectors strategy (data-testid, aria roles, etc.)
   - There is NO LIMIT on the number of questions - ask as many as needed

5. **Create/Update Page Objects**
   - Identify pages and components involved in the scenarios
   - Create new page objects for new pages/components
   - Update existing page objects if new interactions are needed
   - Follow existing page object patterns in the codebase
   - Include:
     - Element selectors (prefer data-testid or aria roles)
     - Action methods (click, fill, select, etc.)
     - Assertion helpers
     - Wait methods for dynamic content

6. **Create/Update Test Data Fixtures**
   - Identify test data needed for scenarios
   - Create reusable fixtures for:
     - User accounts (different roles if applicable)
     - Entity data (products, orders, etc. based on domain)
     - Edge case data
   - Follow existing fixture patterns in the codebase
   - Ensure fixtures are isolated (don't depend on production data)
   - Include setup and teardown as needed

7. **Create/Update Reusable Test Utilities**
   - Identify common patterns across scenarios
   - Create or update utilities for:
     - Authentication (login/logout helpers)
     - Navigation helpers
     - Common assertions
     - Data generation helpers
     - API helpers for test setup (if applicable)
   - Follow existing utility patterns in the codebase
   - Avoid duplication - reuse what exists

8. **Implement Tests Scenario by Scenario**
   - Work through each scenario in order
   - For each scenario:
     - Create or update test file following project conventions
     - Use page objects for interactions
     - Use fixtures for test data
     - Use utilities for common operations
     - Implement the Given/When/Then steps
     - Add meaningful assertions
     - Handle preconditions properly
   - Avoid:
     - Hardcoded waits (use proper wait strategies)
     - Flaky selectors (no positional or index-based)
     - Test interdependencies (each test should be isolated)
     - Duplicating code (use page objects, fixtures, utilities)

9. **Run and Verify Tests**
   - Run each test after implementation
   - Verify it passes consistently (run multiple times)
   - If test fails:
     - Debug using browser automation
     - Fix the test or report UI issue to user
   - Ensure no flakiness

10. **Run All Quality Checks**
    - Run all quality checks:
      - Linting (0 errors, 0 warnings)
      - Type checking (0 errors, 0 warnings)
      - All e2e tests (new and existing)
    - Fix any issues before proceeding

11. **Update Coverage Mapping**
    - Update the test-plan.md to mark which scenarios now have e2e tests
    - Note the test file and test name for each scenario

12. **Commit Changes**
    - Commit the e2e tests
    - Use commit message: `test(<feature-name>): add e2e tests`
    - Include summary of scenarios covered in commit body
    - List new page objects, fixtures, and utilities created

## Output

- E2e tests implemented for all scenarios
- Page objects created/updated as needed
- Test data fixtures created/updated as needed
- Reusable utilities created/updated as needed
- All tests passing consistently
- Coverage mapping updated in test-plan.md
- Tests committed to feature branch
