pipeline {
    agent any

    environment {
        SONAR_SERVER = 'SonarQube'
        APP_NAME     = 'Entropy-Engine'
        PORT         = '8000'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('SonarQube Code Analysis') {
    steps {
        withSonarQubeEnv('SonarQube') {
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

        stage('Deploy App') {
            steps {
                sh """
                    docker stop ${APP_NAME} || true
                    docker rm ${APP_NAME} || true
                    docker run -d --name ${APP_NAME} -p ${PORT}:${PORT} ${APP_NAME}:latest
                """
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
