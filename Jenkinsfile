pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        APP_NAME       = 'rural-telemedicine'
        CI_CONTAINER   = 'jenkins-ci'
        SONAR_HOST_URL = 'http://sonarqube:9000'
        NET            = 'devsecops'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'mkdir -p reports'
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                docker run --rm --volumes-from ${CI_CONTAINER} -w "$WORKSPACE" python:3.12-slim \
                  sh -c "pip install --no-cache-dir -q -r requirements.txt pytest && python -m pytest -q"
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                    sh '''
                    docker run --rm --network ${NET} --volumes-from ${CI_CONTAINER} -w "$WORKSPACE" \
                      -e SONAR_HOST_URL -e SONAR_TOKEN \
                      sonarsource/sonar-scanner-cli sonar-scanner \
                      -Dsonar.projectBaseDir="$WORKSPACE" -Dsonar.qualitygate.wait=true
                    '''
                }
            }
        }

        stage('Trivy Filesystem Scan') {
            steps {
                sh '''
                docker run --rm --volumes-from ${CI_CONTAINER} -v trivy-cache:/root/.cache \
                  aquasec/trivy:latest fs --scanners vuln,secret,misconfig --exit-code 0 \
                  --format table --output "$WORKSPACE/reports/trivy-fs.txt" "$WORKSPACE"
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build --pull -t ${APP_NAME}:${BUILD_NUMBER} -t ${APP_NAME}:latest .'
            }
        }

        stage('Trivy Image Scan') {
            steps {
                sh '''
                docker run --rm --volumes-from ${CI_CONTAINER} -v trivy-cache:/root/.cache \
                  aquasec/trivy:latest image --exit-code 0 --format table \
                  --output "$WORKSPACE/reports/trivy-image.txt" ${APP_NAME}:${BUILD_NUMBER}
                docker run --rm --volumes-from ${CI_CONTAINER} -v trivy-cache:/root/.cache \
                  aquasec/trivy:latest image --severity HIGH,CRITICAL --exit-code 0 ${APP_NAME}:${BUILD_NUMBER}
                '''
            }
        }

        stage('Deploy') {
            steps {
                withCredentials([string(credentialsId: 'doctor-password', variable: 'DOCTOR_PASSWORD')]) {
                    sh '''
                    docker rm -f telemed || true
                    docker run -d --name telemed --network ${NET} --restart unless-stopped \
                      -e DOCTOR_PASSWORD -p 8501:8501 -v telemed-data:/data ${APP_NAME}:${BUILD_NUMBER}
                    '''
                }
            }
        }

        stage('Smoke Test') {
            steps {
                sh '''
                for i in $(seq 1 20); do
                  s=$(docker inspect -f "{{.State.Health.Status}}" telemed)
                  echo "health: $s"
                  [ "$s" = "healthy" ] && exit 0
                  sleep 5
                done
                echo "App did not become healthy"
                docker logs telemed
                exit 1
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
        }
        success { echo 'Pipeline finished successfully.' }
        failure { echo 'Pipeline failed. Check the stage logs.' }
    }
}