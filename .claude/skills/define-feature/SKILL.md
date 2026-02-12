---
name: define-feature
description: Define and document functional requirements for a new feature through an interview-style process. Produces a functional specification with user stories, acceptance criteria, and edge cases. Automatically use when user requests to "define a feature", "write a spec", "create requirements", "document feature requirements", or "new feature spec".
---

# Define Feature

Help users clearly define and document functional requirements for a new feature through guided discovery and an interview-style requirements clarification process, producing a formal functional specification.

## Core Principle: Zero Assumptions

Never assume when uncertain or when multiple valid options exist. Always ask the user. It's better to ask one extra question than to build a plan on a wrong assumption.

## How to Use This Skill

**Input:** A feature description or idea from the user
**Output:** A functional specification document saved to `features/<feature-name>/spec.md` with APPROVED status, reviewed and approved by the user.

### Step 1: Explore the Codebase

- Accept a feature description from the user
- Explore the codebase to understand existing functionality and domain
- Identify similar features, patterns, or conventions that inform requirement questions
- Gather enough context to ask informed, relevant questions

### Step 2: Offer Visual Exploration (Optional)

Ask the user if they want to explore the running app in a browser:

- If yes, ask for:
  - URL to the app
  - Login credentials if authentication is required
- Use agent-browser CLI for browser automation
- Save screenshots to `features/<feature-name>/screenshots/`
- Link screenshots in the spec document when helpful
- Skip this step if user declines or the feature is not UI-related

### Step 3: Clarify Requirements (Interview Style)

Focus on **WHAT** the user wants, not how to build it.

Ask ONE question at a time using the `AskUserQuestion` tool:

- Ask about functional requirements, expected behavior, edge cases, user expectations
- Present options with pros/cons for each decision point
- Mark a recommended option when there is a clear best choice
- Wait for the answer before asking the next question
- There is **no limit** on the number of questions -- ask as many as needed
- Goal is 100% understanding of the requirements
- Keep asking until every ambiguity is resolved

### Step 4: Gather Dependencies Context

- Identify dependencies on other features, APIs, or external systems
- Ask the user for documentation or additional context when it helps shape the spec
- Request links to API docs, design files, or related specs if relevant

### Step 5: Capture Non-Functional Hints (When Applicable)

Note any relevant non-functional expectations the user mentions:

- **Performance:** e.g., "should load quickly", "handles large datasets"
- **Security:** e.g., "sensitive data", "requires authentication"
- **Scalability:** e.g., "will have many concurrent users"

Keep these as hints and expectations, not implementation requirements.

### Step 6: Save Functional Specification (Draft)

Once requirements are clear, write a spec document using the template:

- Create feature folder: `features/<feature-name>/`
- Save to `features/<feature-name>/spec.md`
- Use a kebab-case feature name derived from the feature description
- Mark the spec as **DRAFT** status
- Document only functional requirements (the WHAT)
- Keep it purely functional -- no implementation details

For the spec template, see [references/spec-template.md](references/spec-template.md).

### Step 7: Get User Approval

- Present the spec to the user for review
- Ask for feedback using `AskUserQuestion`
- If user has changes, update the spec and present again
- Keep iterating until user **explicitly approves**
- When approved, update status from DRAFT to **APPROVED**
- Skill completes only when user approves the spec

## Output Format

```
features/<feature-name>/
  spec.md                        # Functional specification (APPROVED)
  screenshots/                   # Optional: browser screenshots
```

## Important Guidelines

**DO:**
- Use kebab-case for the feature folder name (`features/user-notifications/`)
- Ask one question at a time and wait for the answer
- Focus exclusively on functional requirements (the WHAT)
- Include concrete user stories with clear acceptance criteria
- Document edge cases and out-of-scope items explicitly
- Always get explicit user approval before marking APPROVED

**DON'T:**
- Include implementation details, architecture decisions, or technology choices in the spec
- Skip the user approval loop -- always get explicit approval
- Assume requirements when multiple valid options exist -- ask the user
- Batch multiple questions into a single prompt
- Proceed without understanding the codebase context first
- Mark the spec as APPROVED without the user explicitly approving it
