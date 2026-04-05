// =============================================================================
// imdbapi-client — Jenkins declarative pipeline
//
// Pipeline modes (Jenkins Multibranch Pipeline):
//   PR build   — every pull request: Lint + Typecheck + Test (no image build)
//   Main build — push to main: Lint + Typecheck + Test (no image build)
//
// NOTE: This image is NOT pushed to ACR. imdbapi is an internal Python library
// imported by the chain; only the backend app image is published to ACR.
//
// Required Jenkins plugins: Docker Pipeline, JUnit, Coverage, Credentials Binding
// =============================================================================

pipeline {
    agent any

    options {
        buildDiscarder(logRotator(numToKeepStr: '20'))
        timeout(time: 45, unit: 'MINUTES')
        disableConcurrentBuilds(abortPrevious: true)
    }

    environment {
        SERVICE_NAME = 'imdbapi-client'
        COMPOSE_PROJECT_NAME = "imdbapi-ci-${env.BUILD_NUMBER}"
    }

    stages {

        // ------------------------------------------------------------------ //
        stage('Initialize') {
            steps {
                sh 'make init'
            }
        }

        // ------------------------------------------------------------------ //
        stage('Lint + Typecheck') {
            parallel {
                stage('Lint') {
                    steps { sh 'make lint' }
                }
                stage('Typecheck') {
                    steps { sh 'make typecheck' }
                }
            }
        }

        // ------------------------------------------------------------------ //
        stage('Test') {
            steps {
                sh 'make test-coverage'
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/junit.xml'
                    recordCoverage(
                        tools: [
                            [parser: 'COBERTURA', pattern: 'reports/coverage.xml']
                        ],
                        id: 'coverage',
                        name: 'IMDb Client Coverage',
                        sourceCodeRetention: 'EVERY_BUILD',
                        sourceDirectories: [[path: 'src']],
                        failOnError: false,
                        qualityGates: [
                            [threshold: 10.0, metric: 'LINE', baseline: 'PROJECT'],
                            [threshold: 10.0, metric: 'BRANCH', baseline: 'PROJECT']
                        ]
                    )
                }
            }
        }

    }

    post {
        always {
            sh 'make clean || true'
            sh 'make ci-down || true'
            cleanWs()
        }
        failure {
            echo "Pipeline failed on ${env.BRANCH_NAME ?: 'unknown ref'} — check logs above."
        }
        success {
            echo "Pipeline completed successfully."
        }
    }
}
