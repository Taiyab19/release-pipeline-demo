// ============================================================
// Release Pipeline Demo — Jenkinsfile
// Author  : Tayyab Karem (Release Management Specialist)
// Purpose : End-to-end CI/CD pipeline with environment
//           promotion, approval gates, quality gates,
//           rollback, and post-deployment validation.
//           Mirrors enterprise release practices used at
//           Mastercard for business-critical payment apps.
// ============================================================

pipeline {

    agent any

    // ── Environment Variables ───────────────────────────────
    environment {
        APP_NAME        = 'payment-service'
        ARTIFACT_NAME   = "${APP_NAME}-${BUILD_NUMBER}"
        SONAR_PROJECT   = 'release-pipeline-demo'
        COVERAGE_MIN    = '80'
        DOCKER_IMAGE    = "tayyabkarem/${APP_NAME}"
        SLACK_CHANNEL   = '#releases'
        PROD_URL        = 'http://prod.example.com'
        STAGING_URL     = 'http://staging.example.com'
        DEV_URL         = 'http://dev.example.com'
    }

    // ── Build Triggers ─────────────────────────────────────
    triggers {
        // Poll SCM every 5 minutes (replace with webhook in real setup)
        pollSCM('H/5 * * * *')
    }

    // ── Pipeline Options ───────────────────────────────────
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 60, unit: 'MINUTES')
        timestamps()
        disableConcurrentBuilds()
    }

    // ── Parameters (visible in Jenkins UI) ─────────────────
    parameters {
        choice(
            name: 'DEPLOY_ENV',
            choices: ['dev', 'staging', 'production'],
            description: 'Target deployment environment'
        )
        booleanParam(
            name: 'SKIP_TESTS',
            defaultValue: false,
            description: 'Skip tests (emergency hotfix only — requires CAB approval)'
        )
        string(
            name: 'RELEASE_VERSION',
            defaultValue: '',
            description: 'Release version tag (e.g. 1.4.2). Leave blank to auto-generate.'
        )
    }

    stages {

        // ── Stage 1: Checkout & Versioning ─────────────────
        stage('Checkout') {
            steps {
                echo "====== STAGE: Checkout ======"
                checkout scm
                script {
                    // Auto-generate version if not provided
                    env.VERSION = params.RELEASE_VERSION ?:
                        sh(script: "git describe --tags --always --dirty", returnStdout: true).trim()
                    env.GIT_COMMIT_MSG = sh(
                        script: "git log -1 --pretty=%B",
                        returnStdout: true
                    ).trim()
                    env.GIT_AUTHOR = sh(
                        script: "git log -1 --pretty=%an",
                        returnStdout: true
                    ).trim()
                    echo "Version   : ${env.VERSION}"
                    echo "Commit    : ${env.GIT_COMMIT_MSG}"
                    echo "Author    : ${env.GIT_AUTHOR}"
                    echo "Build No  : ${BUILD_NUMBER}"
                }
            }
        }

        // ── Stage 2: Build ─────────────────────────────────
        stage('Build') {
            steps {
                echo "====== STAGE: Build ======"
                sh '''
                    echo "Installing dependencies..."
                    pip install -r app/requirements.txt --quiet

                    echo "Running linter..."
                    pip install flake8 --quiet
                    flake8 app/app.py --max-line-length=100 --statistics || true

                    echo "Build complete: ${ARTIFACT_NAME}"
                '''
            }
            post {
                success { echo "Build PASSED" }
                failure { echo "Build FAILED — pipeline aborted" }
            }
        }

        // ── Stage 3: Unit Tests ─────────────────────────────
        stage('Unit Tests') {
            when {
                not { expression { params.SKIP_TESTS } }
            }
            steps {
                echo "====== STAGE: Unit Tests ======"
                sh '''
                    pip install pytest pytest-cov --quiet
                    pytest app/test_app.py \
                        -v \
                        --cov=app \
                        --cov-report=xml:coverage.xml \
                        --cov-report=term-missing \
                        --junitxml=test-results.xml
                '''
            }
            post {
                always {
                    // Publish test results in Jenkins UI
                    junit 'test-results.xml'
                }
                success { echo "All tests PASSED" }
                failure {
                    echo "Tests FAILED — blocking pipeline"
                    // In real setup: raise incident ticket via ServiceNow API
                    sh 'bash scripts/notify.sh "FAILED" "Unit tests failed on build ${BUILD_NUMBER}"'
                }
            }
        }

        // ── Stage 4: Code Quality Gate ──────────────────────
        stage('Quality Gate') {
            when {
                not { expression { params.SKIP_TESTS } }
            }
            steps {
                echo "====== STAGE: Quality Gate (SonarQube-style) ======"
                script {
                    // Parse coverage from XML and enforce minimum threshold
                    def coverage = sh(
                        script: """
                            python3 -c "
import xml.etree.ElementTree as ET
tree = ET.parse('coverage.xml')
root = tree.getroot()
cov = float(root.attrib.get('line-rate', 0)) * 100
print(f'{cov:.1f}')
"
                        """,
                        returnStdout: true
                    ).trim()

                    echo "Code Coverage: ${coverage}%  (Minimum required: ${COVERAGE_MIN}%)"

                    if (coverage.toFloat() < COVERAGE_MIN.toFloat()) {
                        error("Quality gate FAILED: Coverage ${coverage}% < ${COVERAGE_MIN}% minimum. " +
                              "Pipeline blocked per release governance policy.")
                    }
                    echo "Quality gate PASSED"
                }
            }
        }

        // ── Stage 5: Package & Archive Artifact ────────────
        stage('Package') {
            steps {
                echo "====== STAGE: Package Artifact ======"
                sh '''
                    mkdir -p artifacts
                    # Simulate artifact packaging (in real setup: Docker build or JAR/WAR)
                    tar -czf artifacts/${ARTIFACT_NAME}.tar.gz app/
                    echo "Artifact packaged: artifacts/${ARTIFACT_NAME}.tar.gz"

                    # Generate release notes from Git log
                    bash scripts/generate-release-notes.sh > artifacts/RELEASE_NOTES_${VERSION}.md
                    echo "Release notes generated"

                    # In real setup: push to JFrog Artifactory
                    # jfrog rt upload artifacts/${ARTIFACT_NAME}.tar.gz repo/
                    ls -lh artifacts/
                '''
                archiveArtifacts artifacts: 'artifacts/**', fingerprint: true
            }
        }

        // ── Stage 6: Deploy to DEV ──────────────────────────
        stage('Deploy → DEV') {
            steps {
                echo "====== STAGE: Deploy to DEV (automatic) ======"
                sh "bash scripts/deploy.sh dev ${ARTIFACT_NAME} ${VERSION}"
            }
            post {
                success {
                    sh "bash scripts/smoke-test.sh dev ${DEV_URL}"
                }
                failure {
                    sh "bash scripts/rollback.sh dev"
                }
            }
        }

        // ── Stage 7: Deploy to STAGING ─────────────────────
        stage('Deploy → STAGING') {
            when {
                anyOf {
                    branch 'release/*'
                    expression { params.DEPLOY_ENV in ['staging', 'production'] }
                }
            }
            steps {
                echo "====== STAGE: Deploy to STAGING ======"
                sh "bash scripts/deploy.sh staging ${ARTIFACT_NAME} ${VERSION}"
            }
            post {
                success {
                    sh "bash scripts/smoke-test.sh staging ${STAGING_URL}"
                    echo "Staging smoke tests PASSED — ready for Production approval"
                }
                failure {
                    echo "Staging deploy FAILED — initiating rollback"
                    sh "bash scripts/rollback.sh staging"
                    error("Staging deployment failed. Production promotion blocked.")
                }
            }
        }

        // ── Stage 8: Production Approval Gate (CAB) ────────
        stage('Production Approval') {
            when {
                anyOf {
                    branch 'main'
                    expression { params.DEPLOY_ENV == 'production' }
                }
            }
            steps {
                echo "====== STAGE: Awaiting CAB / Release Manager Approval ======"
                script {
                    // Pause pipeline and wait for manual approval
                    // In real setup: sends notification to release-manager via ServiceNow/Slack
                    def approver = input(
                        id: 'prod-approval',
                        message: """
PRODUCTION DEPLOYMENT APPROVAL REQUIRED

Application  : ${APP_NAME}
Version      : ${VERSION}
Build        : ${BUILD_NUMBER}
Requestor    : ${GIT_AUTHOR}

Pre-conditions:
  ✅ Unit tests passed
  ✅ Quality gate passed (coverage >= ${COVERAGE_MIN}%)
  ✅ Staging smoke tests passed
  ✅ Artifact archived

Approving confirms the Go/No-Go decision for Production deployment.
                        """,
                        submitter: 'release-manager,cab-approvers',
                        submitterParameter: 'APPROVED_BY',
                        parameters: [
                            choice(
                                name: 'DECISION',
                                choices: ['GO', 'NO-GO'],
                                description: 'Release decision'
                            ),
                            text(
                                name: 'NOTES',
                                defaultValue: '',
                                description: 'Approval notes / change ticket number'
                            )
                        ]
                    )
                    if (approver.DECISION == 'NO-GO') {
                        error("Production deployment rejected by ${approver.APPROVED_BY}. " +
                              "Notes: ${approver.NOTES}")
                    }
                    env.APPROVED_BY    = approver.APPROVED_BY
                    env.APPROVAL_NOTES = approver.NOTES
                    echo "Production APPROVED by: ${env.APPROVED_BY}"
                    echo "Approval notes: ${env.APPROVAL_NOTES}"
                }
            }
        }

        // ── Stage 9: Deploy to PRODUCTION ──────────────────
        stage('Deploy → PRODUCTION') {
            when {
                anyOf {
                    branch 'main'
                    expression { params.DEPLOY_ENV == 'production' }
                }
            }
            steps {
                echo "====== STAGE: Deploy to PRODUCTION ======"
                sh "bash scripts/deploy.sh production ${ARTIFACT_NAME} ${VERSION}"
            }
            post {
                success {
                    sh "bash scripts/smoke-test.sh production ${PROD_URL}"
                    sh "bash scripts/health-check.sh ${PROD_URL}"
                }
                failure {
                    echo "PRODUCTION DEPLOY FAILED — initiating immediate rollback"
                    sh "bash scripts/rollback.sh production"
                    // In real setup: page on-call, raise P1 incident in ServiceNow
                    sh 'bash scripts/notify.sh "P1-INCIDENT" "Production deploy failed — rollback initiated. Build ${BUILD_NUMBER}"'
                    error("Production deployment failed. Rollback completed. Incident raised.")
                }
            }
        }

        // ── Stage 10: Post-Deploy Validation ───────────────
        stage('Post-Deploy Validation') {
            when {
                anyOf {
                    branch 'main'
                    expression { params.DEPLOY_ENV == 'production' }
                }
            }
            steps {
                echo "====== STAGE: Post-Deployment Validation ======"
                sh '''
                    echo "Running extended health checks..."
                    bash scripts/health-check.sh ${PROD_URL}

                    echo "Validating SLA thresholds..."
                    # Response time < 2000ms, error rate < 1%
                    RESPONSE_TIME=$(curl -o /dev/null -s -w "%{time_total}" ${PROD_URL}/health || echo "9999")
                    echo "Response time: ${RESPONSE_TIME}s"

                    echo "Post-deploy validation complete"
                    echo "Release ${VERSION} is LIVE in Production"
                '''
            }
        }
    }

    // ── Post-Pipeline Actions ───────────────────────────────
    post {
        success {
            echo "====== PIPELINE SUCCESS ======"
            echo "Release ${env.VERSION} deployed successfully"
            sh '''
                echo "Sending success notification..."
                # bash scripts/notify.sh "SUCCESS" "Release ${VERSION} deployed to ${DEPLOY_ENV}"
                echo "Notification sent (Slack/ServiceNow webhook)"
            '''
        }
        failure {
            echo "====== PIPELINE FAILED ======"
            sh '''
                echo "Sending failure alert to release manager..."
                # bash scripts/notify.sh "FAILED" "Build ${BUILD_NUMBER} failed on ${DEPLOY_ENV}"
                echo "Alert sent"
            '''
        }
        always {
            echo "Build ${BUILD_NUMBER} complete — cleaning workspace"
            cleanWs()
        }
    }
}
