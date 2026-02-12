# Review Checklist

A structured checklist for reviewing phase implementations. Work through each section systematically.

---

## 1. Plan Alignment

Check that the implementation matches what the phase file specified.

- [ ] All steps listed in the phase file are completed
- [ ] Files created/modified match the planned file list
- [ ] No unplanned files were modified without documented reason
- [ ] Deviations from the plan are documented in progress.md
- [ ] Entry criteria were met before work began
- [ ] Exit criteria are satisfied

**Good:** Phase planned 3 steps, all 3 are done, files match, one deviation documented with rationale.
**Bad:** Phase planned 5 steps, only 4 done, extra file modified with no explanation.

---

## 2. Spec Compliance

Check that the implementation meets the feature specification.

- [ ] All acceptance criteria from the spec are met
- [ ] Edge cases described in the spec are handled
- [ ] Error scenarios described in the spec are addressed
- [ ] API contracts match the spec (request/response shapes)
- [ ] Business logic matches spec requirements exactly
- [ ] No spec requirements were silently dropped

**Good:** Spec says "return 404 when not found" — handler returns 404 with proper error body.
**Bad:** Spec says "return 404 when not found" — handler returns 200 with empty body.

---

## 3. Code Quality

Review the implementation for maintainability and correctness.

### Readability
- [ ] Functions and variables have descriptive names
- [ ] Complex logic has explanatory comments
- [ ] Functions are not excessively long (generally under 50 lines)
- [ ] Nesting depth is reasonable (generally 3 levels or fewer)

**Good:** `calculateDiscountedPrice(basePrice, discountPercent)`
**Bad:** `calc(p, d)` or `doStuff(x)`

### Error Handling
- [ ] All async operations have error handling
- [ ] Error messages are descriptive and actionable
- [ ] Errors propagate correctly (not silently swallowed)
- [ ] Fallback behavior is appropriate and documented

**Good:** `throw new ValidationError('Email must contain @ symbol', { field: 'email' })`
**Bad:** `catch(e) { /* ignore */ }` or `catch(e) { return null }`

### No Hardcoded Values
- [ ] Magic numbers are replaced with named constants
- [ ] Configuration values come from config/env, not inline
- [ ] URLs, ports, paths are configurable
- [ ] Feature flags are used where appropriate

**Good:** `const MAX_RETRY_ATTEMPTS = 3; ... if (retries < MAX_RETRY_ATTEMPTS)`
**Bad:** `if (retries < 3)` or `fetch('http://localhost:3000/api')`

### Typing
- [ ] No `any` types (use `unknown` if type is truly unknown)
- [ ] Interfaces/types defined for all data structures
- [ ] Function parameters and return types are explicit
- [ ] Generic types are used where appropriate
- [ ] Union types are handled exhaustively (switch with default)

**Good:** `function getUser(id: string): Promise<User | null>`
**Bad:** `function getUser(id: any): any`

### Performance
- [ ] No unnecessary re-renders (React) or recomputations
- [ ] Database queries are efficient (no N+1 queries)
- [ ] Large lists use pagination or virtualization
- [ ] Expensive operations are memoized where appropriate

---

## 4. Test Quality

Review tests for thoroughness and reliability.

### Coverage
- [ ] Happy path is tested
- [ ] Edge cases are tested (empty input, boundary values, null/undefined)
- [ ] Error scenarios are tested (invalid input, network failures, timeouts)
- [ ] Integration points are tested

### Test Structure
- [ ] Test descriptions clearly state what is being tested
- [ ] Each test tests one thing (single assertion focus)
- [ ] Tests are isolated (no shared mutable state between tests)
- [ ] Setup and teardown are clean

**Good:** `it('returns 404 when user does not exist')`
**Bad:** `it('works')` or `it('test 1')`

### Assertion Quality
- [ ] Assertions are specific (not just "truthy" or "no error")
- [ ] Expected values are explicit, not computed in the test
- [ ] Error messages in assertions are helpful
- [ ] Snapshot tests are used sparingly and reviewed carefully

**Good:** `expect(result.status).toBe(404); expect(result.body.error).toBe('User not found')`
**Bad:** `expect(result).toBeTruthy()` or `expect(fn).not.toThrow()`

### No Flaky Patterns
- [ ] No reliance on timing (setTimeout in tests)
- [ ] No reliance on external services without mocking
- [ ] No reliance on execution order between test files
- [ ] Async operations properly awaited

---

## 5. Documentation

Review that documentation is accurate and sufficient.

- [ ] Complex logic has inline comments explaining "why"
- [ ] Public APIs have JSDoc/docstring documentation
- [ ] README or feature docs updated if behavior changed
- [ ] No outdated comments that contradict the code
- [ ] Migration steps documented if applicable
- [ ] Breaking changes documented if applicable
