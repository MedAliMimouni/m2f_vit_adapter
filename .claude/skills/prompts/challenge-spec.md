# Prompt: Create "challenge-spec" Skill

Create a Claude Code skill called "challenge-spec" that acts as a devil's advocate to critically review a functional specification and identify gaps, issues, and potential problems.

## Core Principle: Zero Assumptions

Never assume when uncertain or when multiple valid options exist. Always ask the user. It's better to ask one extra question than to build a plan on a wrong assumption.

## Goal

Strengthen the spec by finding weaknesses before implementation begins. Be thorough but constructive - identify problems AND suggest how to address them.

## Reference Files to Create

Before creating the skill, create the following reference files:

1. **Agent-Browser API Reference**
   - Fetch documentation from: https://github.com/vercel-labs/agent-browser
   - Create a reference file with the full API documentation
   - For visual exploration when needed

## Input

The skill accepts:
- A path to a feature folder: `features/<feature-name>/` (with spec.md)

## Process

1. **Read and Analyze the Spec**
   - Read the functional specification thoroughly
   - Understand the feature's goals and scope

2. **Explore the Codebase**
   - Understand existing constraints and patterns
   - Find similar features and how they were specced
   - Identify related functionality that might affect this spec
   - Use this context to inform challenges

3. **Visual Exploration (Only When Needed)**
   - Only offer if understanding current UI/UX would help identify gaps
   - If yes, ask for:
     - URL to the app (if not already known)
     - Login credentials if authentication is required (if not already known)
   - Use agent-browser CLI to understand current behavior
   - Save screenshots to `features/<feature-name>/screenshots/` folder if helpful
   - Skip for backend-only features

4. **Gather External Documentation (When Needed)**
   - If understanding external dependencies would help challenge the spec
   - Ask the user for documentation links when relevant
   - Use documentation to identify potential integration issues or constraints

5. **Challenge the Spec (One Issue at a Time)**
   - Present ONE issue at a time using the AskUserQuestion tool
   - For each issue, explain:
     - What the problem or gap is
     - Why it matters
     - Reference to similar features if applicable (how they handled it)
     - Suggested remediation options with pros/cons
   - Wait for user response before moving to the next issue
   - Categories of challenges:
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

6. **Update the Spec**
   - After each issue is discussed, update the spec if user agrees
   - Keep track of all changes made

7. **Summary**
   - When all issues have been addressed, provide a summary of changes
   - Update the spec with any final revisions

## Output

An improved specification with identified gaps addressed, reviewed and approved by the user.
