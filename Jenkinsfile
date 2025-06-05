pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'ziyaadsayyad/osint-tool'
        DOCKER_CREDENTIALS_ID = 'dockerhub-creds'   // Set in Jenkins > Credentials
        DEPLOY_USER = 'ubuntu'
        DEPLOY_HOST = '3.109.212.76'
        DEPLOY_KEY = 'ec2-ssh-key'  // Private key stored in Jenkins Credentials
    }

    stages {
        stage('Clone Repo') {
            steps {
                git url: 'https://github.com/ziyaad4/combined-osint-tool.git', branch: 'main'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build(DOCKER_IMAGE)
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', DOCKER_CREDENTIALS_ID) {
                        docker.image(DOCKER_IMAGE).push('latest')
                    }
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                sshagent (credentials: [DEPLOY_KEY]) {
                    sh """
                    ssh -o StrictHostKeyChecking=no ${DEPLOY_USER}@${DEPLOY_HOST} << EOF
                    docker pull ${DOCKER_IMAGE}
                    docker stop osint-tool || true
                    docker rm osint-tool || true
                    docker run -d -p 8501:8501 --name osint-tool ${DOCKER_IMAGE}
                    EOF
                    """
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
