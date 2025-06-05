pipeline {
    agent any

    environment {
        IMAGE_NAME = "ziyaadsayyad/osint-tool"
        DOCKERHUB_CREDS = "dockerhub-creds"
        DEPLOY_USER = "ubuntu"
        DEPLOY_HOST = "3.109.212.76"
        DEPLOY_KEY = "ec2-ssh-key"
    }

    stages {
        stage('Clone Repo') {
            steps {
                git url: 'https://github.com/ziyaad4/combined-osint-tool.git', branch: 'main'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t $IMAGE_NAME .'
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: "$DOCKERHUB_CREDS", usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh """
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker push $IMAGE_NAME
                    """
                }
            }
        }

stage('Deploy to EC2') {
    steps {
        sshagent(['ec2-ssh-key']) {
            sh 'ssh -o StrictHostKeyChecking=no ubuntu@<3.109.212.76> "docker pull your-image && docker run ..."'
        }
    }
}

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
