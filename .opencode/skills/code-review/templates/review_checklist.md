# Code Review Checklist

Use this checklist for every review. Mark each item: ✅ Pass | ⚠️ Concern | ❌ Fail | N/A

## 1. Correctness
- [ ] Logic is correct for all described requirements
- [ ] Edge cases handled: null/undefined, empty collections, zero, negative numbers, max values
- [ ] Off-by-one errors in loops and array indexing
- [ ] Async/await used correctly — no unhandled promises or race conditions
- [ ] Error branches return correct values and don't silently swallow exceptions
- [ ] Type coercion and comparison operators are intentional (`===` vs `==`)
- [ ] Recursion has correct base cases and won't stack overflow on large input

## 2. Security (OWASP Top 10)
- [ ] No SQL injection — parameterized queries used, no string concatenation in queries
- [ ] No command injection — no `exec(user_input)` or shell interpolation
- [ ] No XSS — user input is escaped before rendering in HTML
- [ ] Auth/authz checks present on all sensitive routes
- [ ] No IDOR — access to resources gated by ownership check, not just ID
- [ ] No hardcoded secrets, tokens, passwords, or keys
- [ ] Input validated at all system boundaries (API endpoints, file uploads)
- [ ] Sensitive data not logged (passwords, PII, tokens)
- [ ] CSRF protection on state-changing HTTP endpoints
- [ ] Dependencies up to date — no known CVEs

## 3. Performance
- [ ] No N+1 queries — relationships eager-loaded where needed
- [ ] No expensive operations inside loops (DB calls, HTTP requests, file I/O)
- [ ] Proper indexes exist for all filtered/sorted columns
- [ ] Large data sets paginated — no unbounded queries
- [ ] Caching used where beneficial and invalidated correctly
- [ ] No memory leaks — listeners cleaned up, large objects released
- [ ] Async operations parallelized where independent (Promise.all vs sequential await)

## 4. Maintainability
- [ ] Functions do one thing and are under ~40 lines
- [ ] Variable and function names are self-explanatory
- [ ] No magic numbers/strings — constants are named and documented
- [ ] No dead code or commented-out blocks
- [ ] Complex logic has an explanatory comment (the "why", not the "what")
- [ ] DRY — no copy-pasted logic that should be a shared function
- [ ] Dependencies injected or easily mockable — no tight coupling

## 5. Test coverage
- [ ] Happy path is tested
- [ ] Error paths and exceptions are tested
- [ ] Edge cases (null, empty, boundary values) are tested
- [ ] External dependencies are mocked appropriately
- [ ] Tests are readable and test intent, not implementation
