---
name: plan-tests
description: Generate BDD-style test scenarios from a functional specification. Focuses on WHAT to test, not HOW. Produces framework-agnostic behavioral scenarios. Automatically use when user requests to "plan tests", "create test scenarios", "write BDD scenarios", "generate test plan", or "define test cases".
---

# Plan Tests

Generate BDD-style test scenarios from a functional specification, focusing on behavioral coverage.

## Core Principle: Zero Assumptions

Never assume when uncertain or when multiple valid options exist. Always ask the user. It's better to ask one extra question than to build a plan on a wrong assumption.

## Focus

This skill defines WHAT to test, not HOW to test. Scenarios are functional and behavioral, independent of any testing framework or implementation details.

## How to Use This Skill

**Input:** A path to a feature folder: `features/<feature-name>/` (with `spec.md` created by define-feature skill)
**Output:** A `features/<feature-name>/test-plan.md` with APPROVED status, reviewed and approved by the user.

If `spec.md` doesn't exist, recommend running the **define-feature** skill first and stop.

### Step 1: Read and Understand the Spec

- Read `features/<feature-name>/spec.md` thoroughly
- Identify all user stories and acceptance criteria
- Note edge cases and error scenarios mentioned in the spec

### Step 2: Visual Exploration (Only When Needed)

- Only offer if the feature involves UI and understanding current behavior would help
- If yes, ask for URL and login credentials (if not already known)
- Save screenshots to `features/<feature-name>/screenshots/` if helpful
- Skip entirely for backend-only features or when the spec is clear enough

### Step 3: Clarify Test Scope (Interview Style)

Ask ONE question at a time using the `AskUserQuestion` tool:

- Clarify which user flows are highest priority
- Identify scenarios not covered in the spec that should be tested
- Ask about boundary conditions or edge cases to consider
- Present options with pros/cons, marking a recommended option when clear

There is **no limit** on questions -- ask as many as needed until scope is clear.

### Step 4: Generate Test Scenarios (Draft)

Write scenarios in BDD format (Given/When/Then), grouped by user story. Include:

- **Preconditions**: Required setup state before scenarios
- **Happy path scenarios**
- **Edge cases**
- **Error scenarios**
- **Boundary conditions**
- **Example data**: Concrete examples for each scenario
- **Coverage mapping**: Link each scenario to acceptance criteria it covers
- **Out of scope**: Explicitly note what is NOT being tested and why

For the BDD template and examples, see [references/bdd-scenarios-template.md](references/bdd-scenarios-template.md).

Save to `features/<feature-name>/test-plan.md` and mark as **DRAFT** status.

### Step 5: Get User Approval

- Present the scenarios to the user for review
- Ask for feedback using `AskUserQuestion`
- If user has changes, update and present again
- Keep iterating until user **explicitly approves**
- When approved, update status from DRAFT to **APPROVED**
- Skill completes only when user approves

## Output Format

```
features/<feature-name>/
  test-plan.md    # BDD scenarios document with APPROVED status
```

## Important Guidelines

**DO:**
- Keep scenarios implementation-agnostic and framework-independent
- Use concrete example data in every scenario
- Map every scenario back to an acceptance criterion from the spec
- Group scenarios logically by user story or feature area
- Include boundary conditions and negative/error scenarios

**DON'T:**
- Reference specific testing frameworks, libraries, or tools in scenarios
- Skip the user approval loop -- always get explicit approval
- Assume test scope -- ask if unclear
- Proceed without a spec.md file
- Write scenarios that describe implementation details (selectors, API endpoints, etc.)
