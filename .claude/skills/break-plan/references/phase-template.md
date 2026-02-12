# Phase File Template

Use this template when creating individual phase files.

## Template

```markdown
# Phase N: <Phase Name>

**Status:** `not-started` | `in-progress` | `done`

## Objective

[One paragraph describing what this phase accomplishes and why it matters]

## Entry Criteria

- [ ] [What must be true before starting this phase]
- [ ] [Previous phase completed, specific state exists, etc.]

## Steps

### Step N.1: <Step Name>

**Description:** [What to do]
**Files to create/modify:**
- `path/to/file.ts` - [Purpose of change]

### Step N.2: <Step Name>

**Description:** [What to do]
**Files to create/modify:**
- `path/to/file.ts` - [Purpose of change]

## Verification Steps

- [ ] [How to verify this phase is complete]
- [ ] [Specific checks, tests to run, behavior to confirm]

## Exit Criteria

- [ ] [What must be true for this phase to be considered done]
- [ ] [All tests passing, specific functionality working, etc.]
```

## Example: Well-Written Phase

```markdown
# Phase 2: Core API Implementation

**Status:** `not-started`

## Objective

Implement the REST API endpoints for user management, including CRUD operations and input validation. This phase builds on the database schema from Phase 1.

## Entry Criteria

- [ ] Phase 1 (Database Setup) is complete
- [ ] Database migrations have been run successfully
- [ ] User model exists and is tested

## Steps

### Step 2.1: Create User Router

**Description:** Set up the Express router with route definitions for all user endpoints.
**Files to create/modify:**
- `src/routes/user.routes.ts` - Create new router with GET/POST/PUT/DELETE routes
- `src/routes/index.ts` - Register user router

### Step 2.2: Implement Create User Endpoint

**Description:** Implement POST /users with input validation, duplicate checking, and password hashing.
**Files to create/modify:**
- `src/controllers/user.controller.ts` - Add createUser handler
- `src/validators/user.validator.ts` - Add create user validation schema

### Step 2.3: Implement Get/List User Endpoints

**Description:** Implement GET /users and GET /users/:id with pagination and filtering.
**Files to create/modify:**
- `src/controllers/user.controller.ts` - Add getUser and listUsers handlers

## Verification Steps

- [ ] POST /users creates a user and returns 201
- [ ] POST /users with invalid data returns 400 with validation errors
- [ ] POST /users with duplicate email returns 409
- [ ] GET /users returns paginated list
- [ ] GET /users/:id returns single user
- [ ] GET /users/:id with invalid ID returns 404
- [ ] All unit tests pass
- [ ] All integration tests pass

## Exit Criteria

- [ ] All CRUD endpoints are implemented and tested
- [ ] Input validation works for all endpoints
- [ ] Error responses follow consistent format
- [ ] Linting and type checking pass with 0 errors/warnings
```

## Guidelines

- **Objective** should be one clear paragraph explaining the "what" and "why"
- **Entry criteria** are hard gates - the phase should not start if these aren't met
- **Steps** should be ordered and specific enough to implement without guessing
- **Files to create/modify** should list every file with the purpose of each change
- **Verification steps** are concrete checks someone can run
- **Exit criteria** define the "done" state unambiguously
