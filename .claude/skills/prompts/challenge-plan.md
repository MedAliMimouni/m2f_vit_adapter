# Prompt: Create "challenge-plan" Skill

Create a Claude Code skill called "challenge-plan" that acts as a devil's advocate to critically review an implementation plan and identify technical issues, risks, and gaps.

## Core Principle: Zero Assumptions

Never assume when uncertain or when multiple valid options exist. Always ask the user. It's better to ask one extra question than to build a plan on a wrong assumption.

## Goal

Strengthen the plan by finding technical weaknesses before implementation begins. Be thorough but constructive - identify problems AND suggest how to address them.

## Reference Files to Create

Before creating the skill, create the following reference files:

1. **Agent-Browser API Reference**
   - Fetch documentation from: https://github.com/vercel-labs/agent-browser
   - Create a reference file with the full API documentation
   - For visual exploration when needed

## Input

The skill accepts:
- A path to a feature folder: `features/<feature-name>/` (with plan.md and optionally spec.md)

## Process

1. **Read and Analyze the Plan**
   - Read the implementation plan thoroughly
   - If spec exists, read it to understand the requirements
   - Understand the proposed approach and phases

2. **Verify Spec Coverage**
   - If spec exists, check that plan covers all acceptance criteria
   - Identify any requirements from spec not addressed in plan
   - Flag any plan steps that go beyond spec scope

3. **Explore the Codebase**
   - Verify the files mentioned in the plan exist and are as expected
   - Verify prerequisites are actually in place
   - Understand existing patterns and architecture
   - Find similar implementations to compare approaches
   - Identify potential conflicts with existing code
   - Look for simpler or better alternative approaches

4. **Visual Exploration (Only When Needed)**
   - Only offer if understanding current UI/UX would help identify implementation issues
   - If yes, ask for:
     - URL to the app (if not already known)
     - Login credentials if authentication is required (if not already known)
   - Use agent-browser CLI to understand current behavior
   - Save screenshots to `features/<feature-name>/screenshots/` folder if helpful
   - Skip for backend-only features

5. **Gather External Documentation (When Needed)**
   - If challenging library/framework usage in the plan
   - Ask the user for documentation links when relevant
   - Use documentation to verify proposed approach is correct

6. **Challenge the Plan (One Issue at a Time)**
   - Present ONE issue at a time using the AskUserQuestion tool
   - For each issue, explain:
     - What the problem or gap is
     - Why it matters technically
     - Reference to similar implementations if applicable
     - Suggested remediation options with pros/cons
   - Wait for user response before moving to the next issue
   - Categories of challenges:
     - **Spec coverage gaps**: Requirements not addressed by the plan
     - **Alternative approaches**: Simpler or better ways to achieve the same result
     - **Technical feasibility**: Approaches that won't work as described
     - **Missing steps**: Steps needed but not included
     - **Cross-phase dependencies**: Steps that depend on other phases incorrectly ordered
     - **Missing prerequisites**: Things that must be in place before plan can start
     - **Architecture concerns**: Violations of existing patterns or principles
     - **Performance risks**: Approaches that could cause performance issues
     - **Security vulnerabilities**: Potential security holes
     - **Testing gaps**: Insufficient or missing test coverage
     - **Migration risks**: Data migration issues or rollback concerns
     - **Breaking changes**: Unaddressed backward compatibility issues
     - **Dependency risks**: Problematic external dependencies
     - **Scope creep**: Steps that go beyond the spec requirements
     - **Technical debt**: Plan introduces debt or misses opportunity to address existing debt
     - **Missing error handling**: Failure modes not addressed

7. **Update the Plan**
   - After each issue is discussed, update the plan if user agrees
   - Keep track of all changes made

8. **Summary**
   - When all issues have been addressed, provide a summary of changes
   - Update the plan with any final revisions

## Output

An improved implementation plan with identified gaps addressed, reviewed and approved by the user.
