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
                sh '''
                    # Create directory for Grype reports
                    mkdir -p ${WORKSPACE}/grype-reports

                    # Save JSON and raw text reports
                    grype ${APP_NAME}:latest -o table > grype-report.txt || true
                    grype ${APP_NAME}:latest -o json > ${WORKSPACE}/grype-reports/grype-report.json || true

                    # Generate HTML report for Jenkins GUI sidebar
                    echo "<html><head><title>Grype Report</title><style>body { font-family: monospace; background-color: #1e1e1e; color: #d4d4d4; padding: 20px; } pre { white-space: pre-wrap; }</style></head><body><h2>Grype Vulnerability Report</h2><pre>" > ${WORKSPACE}/grype-reports/grype-report.html
                    grype ${APP_NAME}:latest -o table >> ${WORKSPACE}/grype-reports/grype-report.html || true
                    echo "</pre></body></html>" >> ${WORKSPACE}/grype-reports/grype-report.html
                '''
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
                // Wait for application to be live so ZAP gets valid responses
                sh """
                    echo "Waiting for ${APP_NAME} to accept connections on port ${PORT}..."
                    until \$(curl --output /dev/null --silent --head --fail http://172.17.0.1:${PORT}); do
                        sleep 2
                    done
                    echo "App is ready!"
                """
            }
        }

        stage('OWASP ZAP DAST Scan') {
            steps {
                script {
                    sh 'mkdir -p ${WORKSPACE}/zap-reports && chmod 777 ${WORKSPACE}/zap-reports'
                    
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
            // 1. Publish OWASP ZAP Report to Jenkins Sidebar
            publishHTML([
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'zap-reports',
                reportFiles: 'zap-report.html',
                reportName: 'OWASP ZAP Report',
                reportTitles: 'OWASP ZAP DAST Results'
            ])

            // 2. Publish Grype Report to Jenkins Sidebar
            publishHTML([
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'grype-reports',
                reportFiles: 'grype-report.html',
                reportName: 'Grype Vulnerability Report',
                reportTitles: 'Grype Container Scan Results'
            ])

            // 3. Save raw reports as Jenkins build artifacts
            archiveArtifacts artifacts: '*.txt, grype-reports/*, zap-reports/*', allowEmptyArchive: true

            // 4. Clean up workspace
            cleanWs()
        }
    }
}
