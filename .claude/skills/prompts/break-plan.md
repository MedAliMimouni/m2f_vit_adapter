# Prompt: Create "break-plan" Skill

Create a Claude Code skill called "break-plan" that takes an implementation plan and breaks it into individual phase files for easier execution.

## Core Principle: Zero Assumptions

Never assume when uncertain or when multiple valid options exist. Always ask the user. It's better to ask one extra question than to build a plan on a wrong assumption.

## Goal

Transform a monolithic plan into discrete, actionable phase files that can be executed independently.

## Reference Files to Create

Before creating the skill, create the following reference files:

1. **Phase Template**
   - Research best practices for phase/milestone documents
   - Create a reference file with a phase template
   - Include sections for: objective, entry criteria, steps, files to modify, verification steps, exit criteria, status
   - Add examples of well-written phases
   - Template should be clear and actionable

## Input

The skill accepts:
- A path to a feature folder: `features/<feature-name>/` (with plan.md)

## Process

1. **Read and Analyze the Plan**
   - Read the implementation plan thoroughly
   - Identify all phases and their steps
   - Understand dependencies between phases

2. **Clarify Phase Boundaries (Interview Style)**
   - Ask ONE question at a time using the AskUserQuestion tool
   - Verify phase boundaries make sense
   - Check if any phases should be split or merged
   - Confirm dependencies between phases
   - There is NO LIMIT on the number of questions - ask as many as needed

3. **Create Phase Files (Draft)**
   - Create phases folder: `features/<feature-name>/phases/`
   - Create overview file `features/<feature-name>/phases/README.md`:
     - Feature summary
     - Link to plan.md and spec.md
     - Mermaid dependency diagram showing phase relationships
     - Overall status tracker
   - Create individual phase files:
     - `features/<feature-name>/phases/phase-1-<name>.md`
     - `features/<feature-name>/phases/phase-2-<name>.md`
     - etc.
   - Each phase file includes:
     - **Objective**: What this phase accomplishes
     - **Status**: `not-started` | `in-progress` | `done`
     - **Entry criteria**: What must be true before starting this phase
     - **Steps**: Ordered steps to complete
     - **Files to create/modify**: With purpose of each change
     - **Verification steps**: How to verify the phase is complete
     - **Exit criteria**: What must be true for phase to be considered done
   - Mark all as **DRAFT** status

4. **Get User Approval**
   - Present the phase structure to the user for review
   - Ask for feedback
   - If user has changes, update and present again
   - Keep iterating until user explicitly approves
   - When approved, update status from DRAFT to **APPROVED**
   - Skill completes only when user approves

## Output

A folder `features/<feature-name>/phases/` containing:
- `README.md` - Overview with mermaid dependency diagram and status tracker
- `phase-N-<name>.md` - Individual phase files with entry/exit criteria and verification steps

All with APPROVED status, reviewed and approved by the user.
