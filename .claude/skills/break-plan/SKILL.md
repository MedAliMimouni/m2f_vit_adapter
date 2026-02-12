---
name: break-plan
description: Break an implementation plan into individual phase files for easier execution. Creates discrete, actionable phase files with entry/exit criteria and dependency diagrams. Automatically use when user requests to "break plan into phases", "split plan", "create phase files", "break down the plan", or "generate phases from plan".
---

# Break Plan

Break a monolithic implementation plan into discrete, actionable phase files that can be executed independently.

## Core Principle: Zero Assumptions

Never assume when uncertain or when multiple valid options exist. Always ask the user. It's better to ask one extra question than to build a plan on a wrong assumption.

## How to Use This Skill

**Input:** A path to a feature folder: `features/<feature-name>/` (with `plan.md`)
**Output:** A `features/<feature-name>/phases/` folder containing a README.md overview and individual phase files, all with APPROVED status.

### Step 1: Read and Analyze the Plan

- Read `features/<feature-name>/plan.md` thoroughly
- Identify all phases and their steps
- Understand dependencies between phases
- If `plan.md` doesn't exist, inform the user and stop

### Step 2: Clarify Phase Boundaries (Interview Style)

Ask ONE question at a time using the `AskUserQuestion` tool:

- Verify phase boundaries make sense
- Check if any phases should be split or merged
- Confirm dependencies between phases
- Clarify any ambiguities in the plan

There is **no limit** on questions — ask as many as needed until boundaries are clear.

### Step 3: Create Phase Files (Draft)

Create the phases folder: `features/<feature-name>/phases/`

**Create the overview file** `phases/README.md`:
- Feature summary with links to plan.md and spec.md
- Phase summary table with status and dependencies
- Mermaid dependency diagram showing phase relationships

For the README template, see [references/phases-readme-template.md](references/phases-readme-template.md).

**Create individual phase files** `phases/phase-N-<name>.md`:

Each phase file must include:
- **Objective**: What this phase accomplishes
- **Status**: `not-started`
- **Entry criteria**: What must be true before starting
- **Steps**: Ordered steps with files to create/modify
- **Verification steps**: How to verify the phase is complete
- **Exit criteria**: What must be true for the phase to be done

For the phase template and examples, see [references/phase-template.md](references/phase-template.md).

Mark all files as **DRAFT** status.

### Step 4: Get User Approval

- Present the phase structure to the user for review
- Ask for feedback using `AskUserQuestion`
- If user has changes, update and present again
- Keep iterating until user **explicitly approves**
- When approved, update status from DRAFT to **APPROVED**
- Skill completes only when user approves

## Output Format

```
features/<feature-name>/phases/
  README.md                    # Overview with mermaid diagram and status tracker
  phase-1-<name>.md            # Individual phase with entry/exit criteria
  phase-2-<name>.md
  phase-3-<name>.md
  ...
```

## Important Guidelines

**DO:**
- Use kebab-case for phase file names (`phase-1-database-setup.md`)
- Make each phase independently executable (clear entry/exit criteria)
- Include specific file paths in each phase's steps
- Show parallel phases as separate branches in the mermaid diagram

**DON'T:**
- Create phases that are too small (a single step) or too large (dozens of steps)
- Skip the user approval loop — always get explicit approval
- Assume phase boundaries — ask if unclear
- Proceed without a plan.md file
