---
name: plan-feature
description: Create a detailed, phased implementation plan for a feature based on a spec or description. Explores codebase patterns, discusses options interview-style, and produces an approved plan document. Automatically use when user requests to "plan a feature", "create implementation plan", "plan implementation", "design feature architecture", or "write a plan".
---

# Plan Feature

Create a detailed, phased implementation plan for a feature by exploring the codebase, discussing options, and documenting the path forward.

## Core Principle: Zero Assumptions

Never assume when uncertain or when multiple valid options exist. Always ask the user. It's better to ask one extra question than to build a plan on a wrong assumption.

## How to Use This Skill

**Input:** A path to `features/<feature-name>/` (with `spec.md` from define-feature) OR a feature description.
**Output:** An implementation plan at `features/<feature-name>/plan.md` with APPROVED status.

If no spec exists, recommend running define-feature first but proceed if the user prefers.

### Step 1: Read the Spec / Understand Requirements

- If `spec.md` exists in the feature folder, read it thoroughly
- If only a feature description is given, clarify requirements as needed
- Confirm understanding before moving on

### Step 2: Explore the Codebase for Patterns

- Identify similar features and how they were implemented
- Understand architecture and layers involved
- Find files that will need modification
- Note existing patterns, utilities, and conventions to follow

### Step 3: Visual Exploration (Only for Significant UI Changes)

- Only offer if the feature involves significant UI changes — skip for backend-only or minor UI work
- If needed, ask for app URL and login credentials (if not already known)
- Use agent-browser CLI to understand current UI state
- Save screenshots to `features/<feature-name>/screenshots/` if helpful

### Step 4: Gather External Documentation (When Needed)

- If unfamiliar tools, libraries, or frameworks are involved, ask the user for documentation links
- Only ask when genuinely needed — don't ask for every library
- Use documentation to inform the implementation approach

### Step 5: Discuss Implementation Options (Interview Style)

- Ask ONE question at a time using the `AskUserQuestion` tool
- Present technical options with pros/cons
- Reference similar patterns found in the codebase
- Mark a recommended option when there is a clear best choice
- If multiple valid approaches exist, ask — don't pick
- There is **no limit** on questions — ask as many as needed

### Step 6: Identify Risks and Concerns

- Identify potential risks, blockers, or areas of uncertainty
- Note breaking changes and how to handle them
- Plan migration strategy if data migrations are needed
- Discuss these with the user during the interview

### Step 7: Save Implementation Plan (Draft)

Save to `features/<feature-name>/plan.md` with **DRAFT** status.

For the plan template and structure, see [references/plan-template.md](references/plan-template.md).

Structure the plan in **phases**, each with ordered steps:
- Phase 1: Setup / Foundation
- Phase 2: Core Implementation
- Phase 3: Integration
- Phase 4: Testing
- (adjust phases based on feature complexity)

Include: link to spec, files to create/modify with purpose, testing requirements, risks and mitigation, breaking changes, and migration steps.

### Step 8: Get User Approval

- Present the plan to the user for review
- Ask for feedback using `AskUserQuestion`
- If user has changes, update and present again
- Keep iterating until user **explicitly approves**
- When approved, update status from DRAFT to **APPROVED**
- Skill completes only when user approves

## Important Guidelines

**DO:**
- Structure the plan in phases with ordered steps, not a flat list
- Include specific file paths for every create/modify action
- Reference codebase patterns discovered during exploration
- Ask about every non-obvious architectural choice
- Include testing strategy for each phase

**DON'T:**
- Skip codebase exploration — always understand existing patterns first
- Assume architectural choices when multiple valid options exist
- Skip the user approval loop — always get explicit approval
- Offer visual exploration for backend-only changes
- Create overly detailed plans for simple features or vague plans for complex ones
