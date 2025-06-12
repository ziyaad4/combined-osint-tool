# ⚙️ OSINT DevOps Dashboard

A **Streamlit-based OSINT (Open Source Intelligence)** dashboard, integrated with **Docker** and **Jenkins CI/CD**, built for automation, modular intelligence gathering, and rapid deployment in DevSecOps pipelines.

---

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Docker Automated](https://img.shields.io/badge/Docker-Automated-blue?logo=docker)
![Jenkins Build](https://img.shields.io/badge/CI-Jenkins-success?logo=jenkins)

---

## 🚀 Features

- 🔍 Username search across platforms
- 🌐 DNS and WHOIS lookups
- 📍 IP geolocation with provider data
- 📁 Metadata extraction from files
- 🌑 Basic dark web queries
- 📊 Export results as JSON or CSV
- 📜 Integrated activity logging
- 📦 Dockerized for portability
- 🛠 Jenkins pipeline for automated builds and deployment

---

## 🧱 Tech Stack

| Layer         | Tech         |
|---------------|--------------|
| UI / Dashboard| Streamlit    |
| Language      | Python       |
| Container     | Docker       |
| CI/CD         | Jenkins      |
| Deployment    | EC2 / VPS    |

---

## 📁 Project Structure

```text
combined-osint-tool/
├── app.py                  # Streamlit application
├── Dockerfile              # Container config
├── Jenkinsfile             # CI/CD pipeline
├── requirements.txt        # Python dependencies
├── utils/                  # Modular OSINT tools
│   └── utils/
│       ├── whois_lookup.py
│       ├── dns_enum.py
│       └── ...
├── .streamlit/             # UI config
└── README.md
└── README.md
````

---

## 🐳 Docker Deployment

### 🔧 Build & Run Locally

```bash
docker build -t osint-tool .
docker run -d -p 8501:8501 --name osint osint-tool
````

🧪 Development Mode (without Docker)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
````
🧪 Jenkins CI/CD
This repo includes a Jenkinsfile to:
- Clone source from Git
- Build Docker image
- Push to Docker Hub
- Deploy to EC2/VPS
Example Jenkins Pipeline Stage
```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'docker build -t yourname/osint-tool .'
            }
        }
        stage('Push') {
            steps {
                withCredentials([usernamePassword(...)]) {
                    sh 'docker push yourname/osint-tool'
                }
            }
        }
        ...
    }
}
```
📸 Screenshots
![image](https://github.com/user-attachments/assets/19349d97-f44e-483a-8356-5f4792122eaa)

📦 Exported Results
All tools support data export:

- Export to CSV

- Export to JSON

Session logs and history are also available for review.

🔐 License
This project is licensed under the MIT License. See the LICENSE file for details.

👤 Author
Ziyaad Sayyad

Security Researcher | DevSecOps Enthusiast

GitHub: @ziyaad4




