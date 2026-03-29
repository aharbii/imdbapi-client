// =============================================================================
// imdbapi-client — Jenkins declarative pipeline
//
// Triggers:
//   • PR validation  — every pull request to main
//   • Release        — every git tag matching v*
//
// Local / CI contract:
//   - lint, typecheck, test, coverage, and pre-commit live behind Makefile
//   - Makefile dispatches into docker compose and the repo-local dev image
//
// Required Jenkins credentials:
//   docker-registry-url  — Docker registry base URL (e.g. ghcr.io/aharbii)
//
// Agent requirements:
//   - Docker Engine
//   - docker compose plugin
//
// Required Jenkins plugins:
//   Docker Pipeline, JUnit, Cobertura, Credentials Binding
// =============================================================================

pipeline {
    agent any

    options {
        buildDiscarder(logRotator(numToKeepStr: '20'))
        timeout(time: 20, unit: 'MINUTES')
        disableConcurrentBuilds(abortPrevious: true)
    }

    environment {
        SERVICE_NAME = 'imdbapi-client'
        COMPOSE_PROJECT_NAME = "imdbapi-ci-${env.BUILD_NUMBER}"
    }

    stages {

        // ------------------------------------------------------------------ //
        stage('Lint + Typecheck') {
            steps {
                sh '''
                    set -e
                    make lint
                    make typecheck
                '''
            }
            post {
                always {
                    sh 'make ci-down || true'
                }
            }
        }

        // ------------------------------------------------------------------ //
        stage('Test') {
            steps {
                sh '''
                    set -e
                    make coverage
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'test-results.xml'
                    cobertura coberturaReportFile: 'coverage.xml',
                              onlyStable: false,
                              failNoReports: false
                    sh 'make ci-down || true'
                }
            }
        }

        // ------------------------------------------------------------------ //
        stage('Build & Push Image') {
            when {
                anyOf {
                    branch 'main'
                    buildingTag()
                }
            }
            environment {
                DOCKER_REGISTRY = credentials('docker-registry-url')
                IMAGE_TAG = "${DOCKER_REGISTRY}/${SERVICE_NAME}:${env.GIT_TAG_NAME ?: env.GIT_COMMIT.take(8)}"
            }
            steps {
                sh "docker build --target runtime -t ${IMAGE_TAG} ."
                sh "docker push ${IMAGE_TAG}"

                script {
                    if (env.BRANCH_NAME == 'main') {
                        sh "docker tag ${IMAGE_TAG} ${DOCKER_REGISTRY}/${SERVICE_NAME}:latest"
                        sh "docker push ${DOCKER_REGISTRY}/${SERVICE_NAME}:latest"
                    }
                }
            }
        }

    }

    post {
        always {
            sh 'make ci-down || true'
            cleanWs()
        }
        failure {
            echo "Pipeline failed on branch ${env.BRANCH_NAME} — check logs above."
        }
    }
}
