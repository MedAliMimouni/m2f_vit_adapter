# Implementation Plan Template

Use this template when creating `features/<feature-name>/plan.md`.

---

```markdown
# Implementation Plan: <Feature Name>

**Status:** DRAFT | APPROVED
**Spec:** [spec.md](./spec.md)
**Created:** <date>
**Approved:** <date or pending>

## Overview

Brief summary of what this plan covers and the high-level approach chosen.
Reference key decisions made during the planning discussion.

---

## Phases

### Phase 1: <Phase Name> (e.g., Setup / Foundation)

**Objective:** What this phase accomplishes.

| # | Step | Files | Action |
|---|------|-------|--------|
| 1 | Description of step | `path/to/file.ts` | create / modify |
| 2 | Description of step | `path/to/other.ts` | modify |

**Verification:** How to confirm this phase is complete.

---

### Phase 2: <Phase Name> (e.g., Core Implementation)

**Objective:** What this phase accomplishes.

| # | Step | Files | Action |
|---|------|-------|--------|
| 1 | Description of step | `path/to/file.ts` | create |
| 2 | Description of step | `path/to/file.ts` | modify |

**Verification:** How to confirm this phase is complete.

---

### Phase 3: <Phase Name> (e.g., Integration)

**Objective:** What this phase accomplishes.

| # | Step | Files | Action |
|---|------|-------|--------|
| 1 | Description of step | `path/to/file.ts` | modify |

**Verification:** How to confirm this phase is complete.

---

### Phase 4: <Phase Name> (e.g., Testing & Validation)

**Objective:** What this phase accomplishes.

| # | Step | Files | Action |
|---|------|-------|--------|
| 1 | Description of step | `path/to/file.test.ts` | create |
| 2 | Description of step | `path/to/file.e2e.ts` | create |

**Verification:** How to confirm this phase is complete.

---

## Testing Strategy

### Unit Tests
- List specific unit tests to write
- Reference files and functions under test

### Integration Tests
- List integration test scenarios
- Note services and modules involved

### E2E Tests (if applicable)
- List end-to-end test flows
- Note any test data setup required

---

## Risks and Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Description of risk | Low/Med/High | Low/Med/High | How to mitigate |

---

## Breaking Changes

- List any breaking changes introduced by this feature
- For each, describe the handling approach (versioning, deprecation, etc.)
- If none, state "No breaking changes expected."

---

## Migration Steps

- List any data or schema migrations required
- Include rollback strategy for each migration
- If none, state "No migrations required."
```

---

## Example: Phased Implementation Plan

Below is an example of a well-structured plan for reference.

```markdown
# Implementation Plan: Team Workspace Permissions

**Status:** APPROVED
**Spec:** [spec.md](./spec.md)
**Created:** 2025-04-10
**Approved:** 2025-04-11

## Overview

Implement role-based permissions for team workspaces. Users can be assigned
Owner, Editor, or Viewer roles. Permissions are enforced at the API layer
and reflected in the UI. Chosen approach: middleware-based authorization
using the existing RBAC utility rather than per-route checks, to stay
consistent with the auth patterns in the billing module.

---

## Phases

### Phase 1: Database & Models

**Objective:** Add the data layer for workspace roles and permissions.

| # | Step | Files | Action |
|---|------|-------|--------|
| 1 | Add `workspace_roles` enum type to schema | `prisma/schema.prisma` | modify |
| 2 | Add `WorkspaceMember` model with role field | `prisma/schema.prisma` | modify |
| 3 | Create migration for new table and enum | `prisma/migrations/` | create |
| 4 | Add seed data for default workspace roles | `prisma/seed.ts` | modify |

**Verification:** Run `prisma migrate dev` and confirm the table exists. Run seed and verify default roles are inserted.

---

### Phase 2: Authorization Middleware

**Objective:** Create reusable authorization middleware that checks workspace roles.

| # | Step | Files | Action |
|---|------|-------|--------|
| 1 | Define permission constants and role hierarchy | `src/lib/permissions.ts` | create |
| 2 | Create `requireWorkspaceRole` middleware | `src/middleware/workspace-auth.ts` | create |
| 3 | Add workspace role resolver to auth context | `src/lib/auth-context.ts` | modify |

**Verification:** Write a unit test confirming the middleware blocks Viewer from write operations and allows Owner for all operations.

---

### Phase 3: API Integration

**Objective:** Apply authorization to all workspace API routes.

| # | Step | Files | Action |
|---|------|-------|--------|
| 1 | Add middleware to workspace settings routes | `src/routes/workspace-settings.ts` | modify |
| 2 | Add middleware to workspace member routes | `src/routes/workspace-members.ts` | modify |
| 3 | Add middleware to workspace content routes | `src/routes/workspace-content.ts` | modify |
| 4 | Add role info to workspace list response | `src/routes/workspaces.ts` | modify |

**Verification:** Manually test each route with different roles via API client. Confirm 403 responses for unauthorized actions.

---

### Phase 4: UI Updates

**Objective:** Reflect permissions in the workspace UI — hide or disable actions the user cannot perform.

| # | Step | Files | Action |
|---|------|-------|--------|
| 1 | Add `useWorkspaceRole` hook | `src/hooks/useWorkspaceRole.ts` | create |
| 2 | Conditionally render settings tab | `src/components/WorkspaceSidebar.tsx` | modify |
| 3 | Disable edit controls for Viewers | `src/components/ContentEditor.tsx` | modify |
| 4 | Add role badge to member list | `src/components/MemberList.tsx` | modify |

**Verification:** Log in as each role and confirm correct UI state.

---

### Phase 5: Testing & Validation

**Objective:** Comprehensive test coverage for the permissions system.

| # | Step | Files | Action |
|---|------|-------|--------|
| 1 | Unit tests for permission constants and helpers | `src/lib/__tests__/permissions.test.ts` | create |
| 2 | Unit tests for authorization middleware | `src/middleware/__tests__/workspace-auth.test.ts` | create |
| 3 | Integration tests for API routes with roles | `tests/integration/workspace-permissions.test.ts` | create |
| 4 | E2E test for role-based UI visibility | `tests/e2e/workspace-permissions.spec.ts` | create |

**Verification:** All tests pass. Coverage report shows >90% for new files.

---

## Testing Strategy

### Unit Tests
- `permissions.ts`: Role hierarchy comparisons, permission checks
- `workspace-auth.ts`: Middleware allows/denies correctly per role

### Integration Tests
- Full request cycle: create workspace, assign roles, verify access per role
- Edge cases: removed member, role downgrade mid-session

### E2E Tests
- Owner invites Editor and Viewer, each sees correct UI
- Viewer cannot access settings page via direct URL navigation

---

## Risks and Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Existing workspaces lack role data | High | High | Migration assigns Owner to workspace creator |
| Performance hit from role lookup on every request | Low | Med | Cache role in auth context per request |
| UI flicker while role loads | Med | Low | Use loading skeleton in workspace layout |

---

## Breaking Changes

- `GET /api/workspaces` response now includes a `role` field on each workspace object. Clients that strictly validate response shapes may need updating.
- Workspace settings endpoints now return 403 for non-Owner roles (previously accessible to all members).

---

## Migration Steps

1. Run `prisma migrate deploy` to create `workspace_member` table and enum.
2. Run backfill script `scripts/backfill-workspace-owners.ts` to assign Owner role to all existing workspace creators.
3. Rollback: Drop `workspace_member` table and enum via down migration. No data loss since roles are new data.
```
