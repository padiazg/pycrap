# Known Issues

Known issues and workarounds for py-crap.

---

## Coverage Runner Fails Silently

**Symptom:** All functions report 0% coverage despite having tests.

**Cause:** The coverage runner (`coverage run -m pytest`) fails silently when tests don't exist, pytest is not installed, or the test suite has import errors. py-crap falls back gracefully without coverage data.

**Fix:** Ensure tests are runnable with `coverage run -m pytest` from the project root. Run with `--verbose` to see debug output.

---

## Large Projects Time Out

**Symptom:** py-crap hangs or takes very long on large monorepos.

**Cause:** The coverage runner has a default 10-minute timeout. Large test suites or slow integration tests can exceed this.

**Workaround:** Run `coverage run -m pytest` separately, then point py-crap at the existing `coverage.xml`.

---

## Exclude Patterns Not Matching

**Symptom:** Expected files are not being excluded.

**Cause:** The `--exclude` flag uses Python regex matched against the full absolute file path.

**Examples:**

```shell
# Exclude all test files (matches anywhere in path)
--exclude '.*_test\.py'

# Exclude protobuf generated files
--exclude '\.pb\..*\.py'

# Exclude a specific directory
--exclude '__pycache__/.*'

# Exclude vendored code
--exclude '\.venv/.*'
```

---

## Relative Paths in Coverage XML

**Symptom:** Functions from the same file appear duplicated or with wrong paths in the output.

**Cause:** coverage.py XML can include relative paths that don't match the absolute paths produced by the complexity analyzer. The merge layer uses a suffix-based fallback index to handle this, but edge cases can occur.

**Fix:** Run py-crap from the project root directory.
