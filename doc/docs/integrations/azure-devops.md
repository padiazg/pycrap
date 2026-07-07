# Azure DevOps

Use py-crap in Azure DevOps pipelines to enforce CRAP score thresholds.

## Example pipeline

```yaml
trigger:
  - main
  - master

pool:
  vmImage: ubuntu-latest

steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: '3.12'
  - script: |
      pip install py-crap
      pip install -e .
    displayName: 'Install dependencies'
  - script: |
      py-crap scan --fail-above --threshold 30 --exclude '.*_test\.py'
    displayName: 'CRAP score check'
  - script: |
      py-crap scan --format sarif --threshold 30 --exclude '.*_test\.py' --output py-crap.sarif
    displayName: 'Generate SARIF report'
    continueOnError: true
  - task: PublishBuildArtifacts@1
    inputs:
      PathtoPublish: py-crap.sarif
      ArtifactName: sarif
```
