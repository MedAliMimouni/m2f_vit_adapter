# Prompt: Create "plan-feature" Skill

Create a Claude Code skill called "plan-feature" that helps users create a detailed implementation plan for a feature.

## Core Principle: Zero Assumptions

Never assume when uncertain or when multiple valid options exist. Always ask the user. It's better to ask one extra question than to build a plan on a wrong assumption.

## Reference Files to Create

Before creating the skill, create the following reference files:

1. **Implementation Plan Template**
   - Research best practices for implementation plan documents
   - Create a reference file with a plan template
   - Structure the plan in phases (not a flat list of steps)
   - Include sections for: overview, phases with ordered steps, files to modify/create, testing strategy, risks, breaking changes, migrations, reference to spec
   - Add examples of well-written plans
   - Template should be clear and actionable

2. **Agent-Browser API Reference**
   - Fetch documentation from: https://github.com/vercel-labs/agent-browser
   - Create a reference file with the full API documentation
   - For visual exploration when needed

## Input

The skill can accept:
- A path to an existing feature folder: `features/<feature-name>/` (with spec.md created by define-feature skill)
- A feature description (if no spec exists)

If given a feature description without a spec, recommend running define-feature first, but proceed if user prefers.

## Process

1. **Read the Spec / Understand Requirements**
   - If spec file provided, read and understand the functional requirements
   - If feature description provided, clarify requirements as needed

2. **Explore the Codebase for Implementation Patterns**
   - Identify similar features and how they were implemented
   - Understand the architecture and layers involved
   - Find relevant files that will need modification
   - Note existing patterns, utilities, and conventions to follow

3. **Visual Exploration (Only When Really Needed)**
   - Only offer if the feature involves significant UI changes
   - If yes, ask for:
     - URL to the app (if not already known)
     - Login credentials if authentication is required (if not already known)
   - Use agent-browser CLI to understand current UI state
   - Save screenshots to `features/<feature-name>/screenshots/` folder if helpful
   - Skip for backend-only or minor UI changes

4. **Gather External Documentation (When Needed)**
   - If the implementation involves unfamiliar tools, libraries, or frameworks
   - Ask the user for documentation links when it would help create a better plan
   - Only ask when applicable and genuinely needed - don't ask for every library
   - Use documentation to inform implementation approach and best practices

5. **Discuss Implementation Options (Interview Style)**
   - Focus on HOW to build it
   - Ask about architectural choices, patterns, trade-offs
   - Present technical options with pros/cons
   - Reference similar patterns found in the codebase
   - Ask ONE question at a time using the AskUserQuestion tool
   - Mark a recommended option when there's a clear best choice
   - If multiple valid approaches exist, ask - don't pick
   - There is NO LIMIT on the number of questions - ask as many as needed

6. **Identify Risks and Concerns**
   - Identify potential risks, blockers, or areas of uncertainty
   - Note any breaking changes and how to handle them
   - If data migrations are needed, plan the migration strategy
   - Discuss these with the user during the interview

7. **Save Implementation Plan (Draft)**
   - Save to `features/<feature-name>/plan.md`
   - Mark the plan as **DRAFT** status
   - Structure the plan in **phases**, each with ordered steps:
     - Phase 1: Setup / Foundation
     - Phase 2: Core Implementation
     - Phase 3: Integration
     - Phase 4: Testing
     - (adjust phases based on feature complexity)
   - Include:
     - Link to the spec file (if exists)
     - Files to create and modify with purpose of each change
     - Phases with ordered implementation steps
     - Testing requirements (unit tests, integration tests, e2e tests)
     - Risks and mitigation strategies
     - Breaking changes and handling approach
     - Migration steps (if applicable)

8. **Get User Approval**
   - Present the plan to the user for review
   - Ask for feedback
   - If user has changes, update the plan and present again
   - Keep iterating until user explicitly approves
   - When approved, update the plan status from DRAFT to **APPROVED**
   - Skill completes only when user approves the plan

## Output

An implementation plan document saved to `features/<feature-name>/plan.md` with APPROVED status, structured in phases, reviewed and approved by the user.
