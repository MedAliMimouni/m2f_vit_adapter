---
name: challenge-spec
description: Critically review a functional specification as a devil's advocate to find gaps, ambiguities, and potential problems before implementation begins. Automatically use when user requests to "challenge spec", "review spec", "find spec gaps", "critique specification", or "devil's advocate spec review".
---

# Challenge Spec

Strengthen a functional specification by finding weaknesses before implementation begins. Be thorough but constructive — identify problems AND suggest how to address them.

## Core Principle: Zero Assumptions

Never assume when uncertain or when multiple valid options exist. Always ask the user. It's better to ask one extra question than to build a plan on a wrong assumption.

## How to Use This Skill

**Input:** A path to a feature folder: `features/<feature-name>/` (with `spec.md`)
**Output:** An improved specification with identified gaps addressed, reviewed and approved by the user.

### Step 1: Read and Analyze the Spec

- Read `features/<feature-name>/spec.md` thoroughly
- Understand the feature's goals, scope, and requirements
- If `spec.md` doesn't exist, inform the user and stop

### Step 2: Explore the Codebase

- Understand existing constraints and patterns
- Find similar features and how they were specced
- Identify related functionality that might affect this spec
- Use this context to inform challenges

### Step 3: Visual Exploration (Only When Needed)

- Only offer if understanding current UI/UX would help identify gaps
- If yes, ask for the app URL and login credentials (if not already known) using `AskUserQuestion`
- Use agent-browser CLI to understand current behavior
- Save screenshots to `features/<feature-name>/screenshots/` if helpful
- Skip entirely for backend-only features

### Step 4: Challenge the Spec (One Issue at a Time)

Present ONE issue at a time using the `AskUserQuestion` tool. For each issue, explain:

- **What** the problem or gap is
- **Why** it matters
- **Reference** to similar features if applicable (how they handled it)
- **Suggested remediation** options with pros/cons

Wait for the user's response before moving to the next issue. There is **no limit** on issues — raise as many as needed until the spec is solid.

**Categories of challenges:**

- **Ambiguities**: Vague or unclear requirements
- **Missing scenarios**: Edge cases or user flows not covered
- **Contradictions**: Requirements that conflict with each other
- **Assumptions**: Unstated assumptions that could be wrong
- **Scope concerns**: Features that are too broad or too narrow
- **User experience gaps**: Confusing or frustrating user flows
- **Error handling**: Missing error states or recovery paths
- **Security concerns**: Potential vulnerabilities or data risks
- **Accessibility gaps**: Missing accessibility considerations
- **Dependencies**: Unclear or risky external dependencies
- **Inconsistency with existing features**: Deviations from established patterns

### Step 5: Update the Spec

- After each issue is discussed and the user agrees on a resolution, update `spec.md` immediately
- Keep track of all changes made throughout the session

### Step 6: Summary

- When all issues have been addressed, provide a summary of all changes made
- Apply any final revisions to the spec

## Important Guidelines

**DO:**
- Challenge one issue at a time — never dump a list of problems all at once
- Always explain why an issue matters, not just what it is
- Reference how similar features in the codebase handle the same concern
- Update the spec incrementally after each resolved issue
- Ask clarifying questions when the user's response is ambiguous

**DON'T:**
- Skip codebase exploration — existing patterns are critical context
- Assume the answer to an ambiguous requirement
- Combine multiple unrelated issues into a single question
- Proceed without a `spec.md` file
- Forget to provide a final summary of all changes
