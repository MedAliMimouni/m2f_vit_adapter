# Prompt: Create "define-feature" Skill

Create a Claude Code skill called "define-feature" that helps users clearly define and document functional requirements for a new feature.

## Core Principle: Zero Assumptions

Never assume when uncertain or when multiple valid options exist. Always ask the user. It's better to ask one extra question than to build a plan on a wrong assumption.

## Reference Files to Create

Before creating the skill, create the following reference files:

1. **Agent-Browser API Reference**
   - Fetch documentation from: https://github.com/vercel-labs/agent-browser
   - Create a reference file with the full API documentation
   - The skill should understand the agent-browser API well, especially:
     - Navigation and authentication
     - The `snapshot` command (AI-optimized page inspection)
     - Screenshot capture
     - Session/profile management for auth state

2. **Functional Spec Template**
   - Research best practices for functional specification documents
   - Create a reference file with a spec template
   - Should be purely functional (no implementation details)
   - Include sections for: overview, user stories, acceptance criteria, edge cases, out of scope, dependencies, non-functional hints, open questions
   - Add examples of well-written specs
   - Template should be clear and consistent

## Process

1. **Explore the Codebase First**
   - Accept a feature description from the user
   - Explore the codebase to understand existing functionality and domain
   - Identify similar features that can inform requirement questions
   - Gather enough context to ask informed questions

2. **Offer Visual Exploration (Optional)**
   - Ask the user if they want to explore the running app in the browser
   - If yes, ask for:
     - URL to the app
     - Login credentials if authentication is required
   - Use agent-browser CLI for browser automation
   - Save screenshots to `features/<feature-name>/screenshots/` folder
   - Link screenshots in the spec document when helpful
   - Skip this step if user declines or feature is not UI-related

3. **Clarify Requirements (Interview Style)**
   - Focus on WHAT the user wants, not how to build it
   - Ask about functional requirements, expected behavior, edge cases, user expectations
   - Ask ONE question at a time using the AskUserQuestion tool
   - Present options with pros/cons for each
   - Mark a recommended option when there's a clear best choice
   - Wait for the answer before asking the next question
   - There is NO LIMIT on the number of questions - ask as many as needed
   - Goal is 100% understanding of the requirements
   - Keep asking until every ambiguity is resolved

4. **Gather Dependencies Context**
   - Identify dependencies on other features, APIs, or external systems
   - Ask the user for documentation or additional context when it helps shape the spec
   - Request links to API docs, design files, or related specs if relevant

5. **Capture Non-Functional Hints (When Applicable)**
   - Note any performance expectations (e.g., "should load quickly", "handles large datasets")
   - Note security considerations (e.g., "sensitive data", "requires authentication")
   - Note scalability hints (e.g., "will have many concurrent users")
   - Keep these as hints/expectations, not implementation requirements

6. **Save Functional Specification (Draft)**
   - Once requirements are clear, write a spec document using the template
   - Create feature folder: `features/<feature-name>/`
   - Save to `features/<feature-name>/spec.md`
   - Use a kebab-case feature name derived from the feature description
   - Mark the spec as **DRAFT** status
   - Document only functional requirements (the WHAT)
   - Keep it purely functional - no implementation details

7. **Get User Approval**
   - Present the spec to the user for review
   - Ask for feedback
   - If user has changes, update the spec and present again
   - Keep iterating until user explicitly approves
   - When approved, update the spec status from DRAFT to **APPROVED**
   - Skill completes only when user approves the spec

## Output

A functional specification document saved to `features/<feature-name>/spec.md` with APPROVED status, reviewed and approved by the user.
