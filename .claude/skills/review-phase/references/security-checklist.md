# Security Review Checklist

A security-focused checklist for reviewing phase implementations. Flag any violations as at least **Major** severity.

---

## 1. Input Validation

All user-supplied data must be validated before use.

- [ ] All API inputs are validated (type, format, length, range)
- [ ] File uploads are validated (type, size, content)
- [ ] URL parameters and query strings are validated
- [ ] Request headers used in logic are validated
- [ ] Validation happens on the server side, not just client side

**Good:**
```typescript
const schema = z.object({
  email: z.string().email().max(255),
  age: z.number().int().min(0).max(150),
});
const data = schema.parse(req.body);
```

**Bad:**
```typescript
const { email, age } = req.body;
// Used directly without validation
await createUser(email, age);
```

---

## 2. Authentication and Authorization

Every protected resource must verify identity and permissions.

- [ ] All protected endpoints require authentication
- [ ] Authorization checks verify the user has permission for the specific resource
- [ ] Token validation is performed on every request (not cached insecurely)
- [ ] Session management is secure (proper expiry, rotation)
- [ ] Password handling uses proper hashing (bcrypt/argon2, not MD5/SHA)
- [ ] Rate limiting is applied to authentication endpoints

**Good:**
```typescript
// Check both authentication AND authorization
const user = await authenticateRequest(req);
const resource = await getResource(params.id);
if (resource.ownerId !== user.id && !user.isAdmin) {
  throw new ForbiddenError('Not authorized to access this resource');
}
```

**Bad:**
```typescript
// Only checks if logged in, not if authorized for THIS resource
const user = await authenticateRequest(req);
const resource = await getResource(params.id);
return resource; // Any authenticated user can access any resource
```

---

## 3. Data Exposure

Sensitive data must never leak to unauthorized parties.

- [ ] API responses do not include unnecessary fields (password hashes, internal IDs, tokens)
- [ ] Logs do not contain sensitive data (passwords, tokens, PII)
- [ ] Error responses do not expose internal implementation details
- [ ] Database queries select only needed fields (no `SELECT *` with sensitive columns)
- [ ] Debug/development data is not present in production code
- [ ] Sensitive data is not stored in localStorage or cookies without encryption

**Good:**
```typescript
// Explicitly select safe fields
const user = await db.user.findUnique({
  where: { id },
  select: { id: true, name: true, email: true },
});
```

**Bad:**
```typescript
// Returns everything including passwordHash, resetToken, etc.
const user = await db.user.findUnique({ where: { id } });
return res.json(user);
```

---

## 4. Injection Vulnerabilities

All dynamic content must be properly escaped or parameterized.

- [ ] SQL queries use parameterized queries or ORM (never string concatenation)
- [ ] HTML output is escaped to prevent XSS
- [ ] Shell commands do not include user input (or are properly escaped)
- [ ] Regular expressions with user input are escaped
- [ ] JSON parsing handles malformed input gracefully
- [ ] Template rendering escapes variables by default

**Good:**
```typescript
// Parameterized query
const users = await db.query('SELECT * FROM users WHERE email = $1', [email]);
```

**Bad:**
```typescript
// SQL injection vulnerability
const users = await db.query(`SELECT * FROM users WHERE email = '${email}'`);
```

**Good (XSS prevention):**
```tsx
// React auto-escapes by default
<p>{userInput}</p>
```

**Bad (XSS vulnerability):**
```tsx
// Dangerous: renders raw HTML from user input
<div dangerouslySetInnerHTML={{ __html: userInput }} />
```

---

## 5. Sensitive Data Handling

Credentials, tokens, and secrets must be handled securely.

- [ ] Secrets are loaded from environment variables, never hardcoded
- [ ] API keys are not committed to version control
- [ ] `.env` files are in `.gitignore`
- [ ] Tokens have appropriate expiration times
- [ ] Sensitive data in memory is cleared when no longer needed
- [ ] HTTPS is enforced for all external communications
- [ ] Encryption keys are properly managed (not hardcoded)

**Good:**
```typescript
const apiKey = process.env.STRIPE_SECRET_KEY;
if (!apiKey) throw new Error('STRIPE_SECRET_KEY is required');
```

**Bad:**
```typescript
const apiKey = 'sk_live_abc123...'; // Hardcoded secret
```

---

## 6. Error Messages

Error responses must be helpful without exposing internals.

- [ ] Error messages do not include stack traces in production
- [ ] Database errors are caught and replaced with generic messages
- [ ] File paths are not exposed in error responses
- [ ] Internal service names and versions are not leaked
- [ ] Authentication failures give generic messages (not "user not found" vs "wrong password")
- [ ] Rate limit responses do not reveal exact limits or reset times to attackers

**Good:**
```typescript
catch (error) {
  logger.error('Database query failed', { error, query: 'getUserById' });
  throw new AppError('Unable to retrieve user', 500);
}
```

**Bad:**
```typescript
catch (error) {
  // Leaks database details, table names, query structure
  return res.status(500).json({
    error: error.message,
    stack: error.stack,
    query: error.query,
  });
}
```

**Good (auth):**
```typescript
throw new AuthError('Invalid email or password'); // Same message for both cases
```

**Bad (auth):**
```typescript
// Reveals which field is wrong — enables user enumeration
if (!user) throw new AuthError('No account with that email');
if (!validPassword) throw new AuthError('Incorrect password');
```
