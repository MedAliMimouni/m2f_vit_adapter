# Prompt: Create "plan-tests" Skill

Create a Claude Code skill called "plan-tests" that helps users generate BDD-style test scenarios from a functional specification.

## Core Principle: Zero Assumptions

Never assume when uncertain or when multiple valid options exist. Always ask the user. It's better to ask one extra question than to build a plan on a wrong assumption.

## Focus

This skill focuses on WHAT to test, not HOW to test. It defines scenarios from a functional/behavioral perspective, independent of any testing framework or implementation details.

## Reference Files to Create

Before creating the skill, create the following reference files:

1. **BDD Scenarios Template**
   - Research best practices for BDD scenario documents
   - Create a reference file with a scenarios template
   - Use Given/When/Then format
   - Include sections for: feature overview, preconditions, scenarios grouped by user story, example data, coverage mapping, out of scope
   - Add examples of well-written scenarios
   - Template should be clear and consistent

2. **Agent-Browser API Reference**
   - Fetch documentation from: https://github.com/vercel-labs/agent-browser
   - Create a reference file with the full API documentation
   - For visual exploration when needed

## Input

The skill accepts:
- A path to a feature folder: `features/<feature-name>/` (with spec.md created by define-feature skill)

If no spec is provided, recommend running define-feature first.

## Process

1. **Read and Understand the Spec**
   - Read the functional specification thoroughly
   - Identify all user stories and acceptance criteria
   - Note edge cases and error scenarios mentioned in the spec

2. **Visual Exploration (Only When Needed)**
   - Only offer if the feature involves UI and understanding current behavior would help
   - If yes, ask for:
     - URL to the app (if not already known)
     - Login credentials if authentication is required (if not already known)
   - Use agent-browser CLI to understand current behavior
   - Save screenshots to `features/<feature-name>/screenshots/` folder if helpful
   - Skip for backend-only features or when spec is clear enough

3. **Clarify Test Scope (Interview Style)**
   - Ask ONE question at a time using the AskUserQuestion tool
   - Clarify which user flows are highest priority
   - Identify any scenarios not covered in the spec that should be tested
   - Ask about boundary conditions or edge cases to consider
   - Present options with pros/cons for each
   - Mark a recommended option when there's a clear best choice
   - There is NO LIMIT on the number of questions - ask as many as needed

4. **Generate Test Scenarios (Draft)**
   - Write scenarios in BDD format (Given/When/Then)
   - Group scenarios by feature or user story
   - Include:
     - **Preconditions**: Required setup state before scenarios
     - **Happy path scenarios**
     - **Edge cases**
     - **Error scenarios**
     - **Boundary conditions**
     - **Example data**: Concrete examples for each scenario
     - **Coverage mapping**: Link each scenario to the acceptance criteria it covers
     - **Out of scope**: Explicitly note what is NOT being tested and why
   - Keep scenarios implementation-agnostic
   - Save to `features/<feature-name>/test-plan.md`
   - Mark as **DRAFT** status

5. **Get User Approval**
   - Present the scenarios to the user for review
   - Ask for feedback
   - If user has changes, update and present again
   - Keep iterating until user explicitly approves
   - When approved, update status from DRAFT to **APPROVED**
   - Skill completes only when user approves

## Output

A BDD test scenarios document saved to `features/<feature-name>/test-plan.md` with APPROVED status, reviewed and approved by the user.
