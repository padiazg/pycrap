# CircleCI

Use py-crap in CircleCI to enforce CRAP score thresholds.

## Example config

```yaml
version: 2.1

jobs:
  crap-check:
    docker:
      - image: cimg/python:3.12
    steps:
      - checkout
      - run:
          name: Install py-crap
          command: pip install py-crap
      - run:
          name: Install project
          command: pip install -e .
      - run:
          name: Check CRAP scores
          command: py-crap scan --fail-above --threshold 30 --exclude '.*_test\.py'

workflows:
  quality:
    jobs:
      - crap-check
```
