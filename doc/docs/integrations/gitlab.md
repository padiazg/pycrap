# GitLab CI

Use py-crap in GitLab CI to enforce CRAP score thresholds.

## Example pipeline

```yaml
stages:
  - quality

crap-check:
  stage: quality
  image: python:3.12-slim
  before_script:
    - pip install py-crap
    - pip install -e .
  script:
    - py-crap scan --fail-above --threshold 30 --exclude '.*_test\.py'
  artifacts:
    paths:
      - py-crap-report.json
    when: always
```

## JSON artifact

Generate a JSON report as a CI artifact:

```yaml
crap-report:
  stage: quality
  image: python:3.12-slim
  before_script:
    - pip install py-crap
  script:
    - py-crap scan --format json --exclude '.*_test\.py' > py-crap-report.json
  artifacts:
    paths:
      - py-crap-report.json
```
