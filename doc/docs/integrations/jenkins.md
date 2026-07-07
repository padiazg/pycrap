# Jenkins

Use py-crap in Jenkins pipelines to enforce CRAP score thresholds.

## Declarative pipeline

```groovy
pipeline {
    agent any

    tools {
        python 'python3.12'
    }

    stages {
        stage('Install') {
            steps {
                sh 'pip install py-crap'
                sh 'pip install -e .'
            }
        }
        stage('CRAP Check') {
            steps {
                sh 'py-crap scan --fail-above --threshold 30 --exclude ".*_test\\.py"'
            }
        }
        stage('SARIF Report') {
            steps {
                sh 'py-crap scan --format sarif --threshold 30 --exclude ".*_test\\.py" --output py-crap.sarif || true'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'py-crap.sarif', fingerprint: true
                }
            }
        }
    }
}
```
