---
name: challenge-plan
description: Critically review an implementation plan as a devil's advocate to identify technical issues, risks, and gaps. Automatically use when user requests to "challenge plan", "review plan", "find plan gaps", "critique implementation plan", or "devil's advocate plan review".
---

# Challenge Plan

Strengthen an implementation plan by finding technical weaknesses before implementation begins. Be thorough but constructive — identify problems AND suggest how to address them.

## Core Principle: Zero Assumptions

Never assume when uncertain or when multiple valid options exist. Always ask the user. It's better to ask one extra question than to build a plan on a wrong assumption.

## How to Use This Skill

**Input:** A path to a feature folder: `features/<feature-name>/` (with `plan.md` and optionally `spec.md`)
**Output:** An improved implementation plan with identified gaps addressed, reviewed and approved by the user.

### Step 1: Read and Analyze the Plan

- Read `features/<feature-name>/plan.md` thoroughly
- If `spec.md` exists, read it to understand requirements
- Understand the proposed approach and phases
- If `plan.md` doesn't exist, inform the user and stop

### Step 2: Verify Spec Coverage

- If `spec.md` exists, check that the plan covers all acceptance criteria
- Identify any requirements from the spec not addressed in the plan
- Flag any plan steps that go beyond spec scope

### Step 3: Explore the Codebase

- Verify files mentioned in the plan exist and are as expected
- Verify prerequisites are actually in place
- Understand existing patterns and architecture
- Find similar implementations to compare approaches
- Identify potential conflicts with existing code
- Look for simpler or better alternative approaches

### Step 4: Visual Exploration (Only When Needed)

- Only offer if understanding current UI/UX would help identify implementation issues
- If yes, ask for URL and login credentials if not already known
- Use agent-browser CLI to understand current behavior
- Save screenshots to `features/<feature-name>/screenshots/` if helpful
- Skip entirely for backend-only features

### Step 5: Challenge the Plan (One Issue at a Time)

Present ONE issue at a time using the `AskUserQuestion` tool. For each issue explain:

- **What** the problem or gap is
- **Why** it matters technically
- **Reference** to similar implementations if applicable
- **Remediation** options with pros/cons

Wait for the user's response before moving to the next issue.

**Challenge categories:**

- **Spec coverage gaps** — requirements not addressed by the plan
- **Alternative approaches** — simpler or better ways to achieve the same result
- **Technical feasibility** — approaches that won't work as described
- **Missing steps** — steps needed but not included
- **Cross-phase dependencies** — steps that depend on other phases incorrectly ordered
- **Missing prerequisites** — things that must be in place before the plan can start
- **Architecture concerns** — violations of existing patterns or principles
- **Performance risks** — approaches that could cause performance issues
- **Security vulnerabilities** — potential security holes
- **Testing gaps** — insufficient or missing test coverage
- **Migration risks** — data migration issues or rollback concerns
- **Breaking changes** — unaddressed backward compatibility issues
- **Dependency risks** — problematic external dependencies
- **Scope creep** — steps that go beyond the spec requirements
- **Technical debt** — plan introduces debt or misses opportunity to address existing debt
- **Missing error handling** — failure modes not addressed

### Step 6: Update the Plan

- After each issue is discussed, update `plan.md` if the user agrees
- Keep track of all changes made

### Step 7: Summary

- When all issues have been addressed, provide a summary of changes
- Update the plan with any final revisions

## Important Guidelines

**DO:**
- Challenge one issue at a time and wait for user response
- Reference actual code and files from the codebase in your challenges
- Suggest concrete remediation options with pros/cons
- Verify that files and patterns referenced in the plan actually exist
- Ask for external documentation links when challenging library/framework usage

**DON'T:**
- Dump all issues at once — go one by one
- Skip codebase exploration — always verify claims in the plan
- Assume phase boundaries or technical decisions — ask if unclear
- Proceed without a `plan.md` file
- Skip the user approval loop — keep iterating until the user approves
