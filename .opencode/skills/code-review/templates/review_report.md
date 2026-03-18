# Code Review: {{FILE_OR_PR}}

**Reviewer:** AI Code Review
**Date:** {{DATE}}
**Scope:** {{SCOPE_DESCRIPTION}}

---

## Summary

{{2-3 sentence overall assessment. Mention overall quality, biggest concern, and one positive.}}

**Verdict:** {{APPROVE / REQUEST CHANGES / NEEDS DISCUSSION}}

---

## 🔴 Critical Issues (must fix before merge)

<!-- Bugs, security holes, data loss risks -->

### Issue 1: {{title}}
**File:** `{{path}}:{{line}}`
**Problem:** {{clear description of what's wrong}}
**Impact:** {{what breaks or what risk this creates}}
**Fix:**
```{{lang}}
// Before
{{bad code}}

// After
{{fixed code}}
```

---

## 🟡 Major Issues (should fix)

<!-- Logic flaws, missing error handling, performance problems -->

### Issue 1: {{title}}
**File:** `{{path}}:{{line}}`
**Problem:** {{description}}
**Suggestion:** {{how to improve it}}

---

## 🟢 Minor Suggestions (nice to have)

<!-- Naming, style, small refactor opportunities -->

- `{{file}}:{{line}}` — {{suggestion}}
- `{{file}}:{{line}}` — {{suggestion}}

---

## ✅ What's Done Well

- {{specific positive thing 1}}
- {{specific positive thing 2}}

---

## Next Steps

1. [ ] Fix critical issues listed above
2. [ ] Address major issues before next review
3. [ ] Consider minor suggestions in a follow-up
