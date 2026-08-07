pipeline {
    agent any

    environment {
        SONAR_SERVER = 'SonarQube'
        APP_NAME     = 'entropy-engine' // Docker image names must be strictly lowercase
        PORT         = '8000'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Trivy FS Scan') {
            steps {
                echo 'Scanning source code dependencies with Trivy...'
                sh '''
                    trivy fs \
                      --severity HIGH,CRITICAL \
                      --format table \
                      --output trivy-fs-report.txt . || true
                '''
            }
        }

        stage('SonarQube Code Analysis') {
            steps {
                withSonarQubeEnv("${SONAR_SERVER}") {
                    script {
                        def scannerHome = tool 'SonarQubeScanner'
                        sh """
                            ${scannerHome}/bin/sonar-scanner \\
                            -Dsonar.projectKey=Entropy-Engine \\
                            -Dsonar.projectName=Entropy-Engine \\
                            -Dsonar.sources=. \\
                            -Dsonar.exclusions=**/venv/**,**/.venv/**,**/__pycache__/**,**/*.pyc \\
                            -Dsonar.javascript.exclusions=**/*
                        """
                    }
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${APP_NAME}:latest ."
            }
        }

        stage('Grype Container Scan') {
            steps {
                echo 'Scanning container image with Grype...'
                // Generates standard text report + JSON output for archiving
                sh """
                    grype ${APP_NAME}:latest \
                      --fail-on critical \
                      -o table > grype-report.txt || true

                    grype ${APP_NAME}:latest \
                      -o json > grype-report.json || true
                """
            }
        }

        stage('Trivy Image Scan') {
            steps {
                echo 'Scanning container image with Trivy...'
                sh """
                    trivy image \
                      --severity HIGH,CRITICAL \
                      --format table \
                      --output trivy-image-report.txt \
                      ${APP_NAME}:latest || true
                """
            }
        }

        stage('Deploy App') {
            steps {
                sh """
                    docker stop ${APP_NAME} || true
                    docker rm ${APP_NAME} || true
                    docker run -d --name ${APP_NAME} -p ${PORT}:${PORT} ${APP_NAME}:latest
                """
                // Healthcheck delay: ensure app container is listening before ZAP hits it
                sh """
                    echo "Waiting for ${APP_NAME} to accept connections on port ${PORT}..."
                    until \$(curl --output /dev/null --silent --head --fail http://172.17.0.1:${PORT}); do
                        sleep 2
                    done
                """
            }
        }

        stage('OWASP ZAP DAST Scan') {
            steps {
                script {
                    // Create workspace directory for ZAP report output
                    sh 'mkdir -p ${WORKSPACE}/zap-reports && chmod 777 ${WORKSPACE}/zap-reports'
                    
                    // Pull and run ZAP Docker image against the local running app
                    sh """
                        docker run --rm \\
                        -v \${WORKSPACE}/zap-reports:/zap/wrk/:rw \\
                        ghcr.io/zaproxy/zaproxy:stable \\
                        zap-baseline.py \\
                        -t http://172.17.0.1:${PORT} \\
                        -r zap-report.html \\
                        -I || true
                    """
                }
            }
        }
    }

    post {
        always {
            // 1. Publish OWASP ZAP Interactive GUI Report to Jenkins Sidebar
            publishHTML([
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'zap-reports',
                reportFiles: 'zap-report.html',
                reportName: 'OWASP ZAP Report',
                reportTitles: 'OWASP ZAP DAST Results'
            ])

            // 2. Save raw scan reports as build artifacts
            archiveArtifacts artifacts: '*.txt, *.json, zap-reports/*.html', allowEmptyArchive: true

            // 3. Clean up Jenkins workspace directory
            cleanWs()
        }
    }
}
