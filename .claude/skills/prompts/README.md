# Two-Agent Review Workflow

A coordinated workflow using two Claude Code sessions sharing a task list: one implements, one reviews.

## Quick Start

### 1. Create Initial Tasks

First, create your task list with the tasks to implement. Start a Claude session with the shared list ID:

```bash
CLAUDE_CODE_TASK_LIST_ID=shared-workflow claude
```

Create your initial tasks:
```
Create the following tasks:
1. "Add user authentication" - Implement JWT-based auth for API routes
2. "Add user profile page" - Create profile page with edit functionality
3. "Add settings page" - User preferences and account settings
```

Exit this bootstrap session.

### 2. Start the Implementer Session (Terminal 1)

```bash
CLAUDE_CODE_TASK_LIST_ID=shared-workflow claude
```

Then paste the contents of `implementer-session.md` as your initial prompt, or reference it:

```
Follow the instructions in prompts/implementer-session.md - you are the Implementation Agent.
Start polling for tasks now.
```

### 3. Start the Reviewer Session (Terminal 2)

```bash
CLAUDE_CODE_TASK_LIST_ID=shared-workflow claude
```

Then paste the contents of `reviewer-session.md` as your initial prompt, or reference it:

```
Follow the instructions in prompts/reviewer-session.md - you are the Review Agent.
Start polling for tasks now.
```

## Workflow Diagram

```
┌─────────────────┐                    ┌─────────────────┐
│   Implementer   │                    │    Reviewer     │
│    Session      │                    │    Session      │
└────────┬────────┘                    └────────┬────────┘
         │                                      │
         ▼                                      │
    ┌─────────┐                                 │
    │ pending │                                 │
    └────┬────┘                                 │
         │ claim                                │
         ▼                                      │
  ┌──────────────┐                              │
  │ implementing │                              │
  └──────┬───────┘                              │
         │ done                                 │
         ▼                                      │
┌─────────────────┐                             │
│ ready_for_review│ ◄───────────────────────────┤ poll
└────────┬────────┘                             │
         │                                      │
         └──────────────────────────────────────┼─────┐
                                                │     │
                                                ▼     │
                                         ┌───────────┐│
                                         │ reviewing ││
                                         └─────┬─────┘│
                                               │      │
                              ┌────────────────┴──────┴───┐
                              │                           │
                              ▼                           ▼
                     ┌──────────────┐            ┌───────────┐
         ┌───────────│ needs_rework │            │ completed │
         │           └──────────────┘            └───────────┘
         │                  │
         │                  │ feedback
         ▼                  ▼
  ┌──────────────┐    ┌──────────────┐
  │ implementing │◄───│   (task)     │
  └──────────────┘    └──────────────┘
```

## Metadata Schema

Tasks use `metadata.reviewStatus` with these values:

| Status | Owner | Description |
|--------|-------|-------------|
| `implementing` | Implementer | Task is being worked on |
| `ready_for_review` | - | Implementation done, waiting for review |
| `reviewing` | Reviewer | Review in progress |
| `needs_rework` | - | Review complete, changes needed |
| `approved` | - | Final state (task status = completed) |

Additional metadata fields:

```typescript
{
  reviewStatus: string;
  // Implementer fields
  implementer?: string;      // Session ID
  startedAt?: string;        // ISO timestamp
  implementedAt?: string;    // When submitted for review
  summary?: string;          // What was implemented
  // Reviewer fields
  reviewer?: string;         // Session ID
  reviewStartedAt?: string;
  reviewedAt?: string;
  reviewedFiles?: string[];  // Files that were reviewed
  feedback?: string;         // Detailed feedback if needs_rework
  approvalNotes?: string;    // Notes if approved
}
```

## Tips

### For Implementers
- Always check for `needs_rework` tasks first - they have priority
- Read feedback carefully before starting rework
- Include a clear summary of what you changed

### For Reviewers
- Be specific and actionable in feedback
- Document which files you reviewed
- Run tests when possible before approving

### General
- Both sessions should never exit - they poll continuously
- Use `Ctrl+T` to see task status at a glance
- If a session crashes, restart it with the same `CLAUDE_CODE_TASK_LIST_ID`

## Troubleshooting

**Tasks not syncing between sessions:**
- Ensure both sessions use identical `CLAUDE_CODE_TASK_LIST_ID`
- Task changes should be visible immediately via `TaskList`

**Race conditions:**
- The `reviewing`/`implementing` status acts as a lock
- If both agents see a task simultaneously, one will fail to claim it
- The failed agent should just move to the next task

**Session exited unexpectedly:**
- Restart with same `CLAUDE_CODE_TASK_LIST_ID` to resume
- Check `TaskList` to see current state
- Continue the workflow loop
