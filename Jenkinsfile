// =============================================================================
// imdbapi-client — Jenkins declarative pipeline
//
// Triggers:
//   • PR validation  — every pull request to main
//   • Release        — every git tag matching v*
//
// Required Jenkins credentials:
//   docker-registry-url  — Docker registry base URL (e.g. ghcr.io/aharbii)
//
// Required Jenkins plugins:
//   Docker Pipeline, JUnit, Cobertura, Credentials Binding
// =============================================================================

pipeline {
    agent none

    options {
        buildDiscarder(logRotator(numToKeepStr: '20'))
        timeout(time: 20, unit: 'MINUTES')
        disableConcurrentBuilds(abortPrevious: true)
    }

    environment {
        SERVICE_NAME    = 'imdbapi-client'
        UV_IMAGE        = 'ghcr.io/astral-sh/uv:python3.13-bookworm-slim'
        DOCKER_IMAGE    = 'docker:24-dind'
    }

    stages {

        // ------------------------------------------------------------------ //
        stage('Lint') {
            agent {
                docker {
                    image "${UV_IMAGE}"
                }
            }
            steps {
                // imdbapi is standalone — has its own uv.lock
                sh 'uv sync --frozen --group lint'
                sh 'uv run ruff check src/ tests/'
                sh 'uv run ruff format --check src/ tests/'
                sh 'uv run mypy src/'
            }
        }

        // ------------------------------------------------------------------ //
        stage('Test') {
            agent {
                docker {
                    image "${UV_IMAGE}"
                }
            }
            steps {
                sh 'uv sync --frozen --group test'
                sh '''
                    uv run pytest tests/ \
                        --cov=src \
                        --cov-report=xml:coverage.xml \
                        --junitxml=test-results.xml \
                        -v --tb=short
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'test-results.xml'
                    cobertura coberturaReportFile: 'coverage.xml',
                              onlyStable: false,
                              failNoReports: false
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
            agent {
                docker {
                    image "${DOCKER_IMAGE}"
                    args '--privileged -v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            environment {
                DOCKER_REGISTRY = credentials('docker-registry-url')
                IMAGE_TAG = "${DOCKER_REGISTRY}/${SERVICE_NAME}:${env.GIT_TAG_NAME ?: env.GIT_COMMIT.take(8)}"
            }
            steps {
                sh "docker build -t ${IMAGE_TAG} ."
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
            cleanWs()
        }
        failure {
            echo "Pipeline failed on branch ${env.BRANCH_NAME} — check logs above."
        }
    }
}
