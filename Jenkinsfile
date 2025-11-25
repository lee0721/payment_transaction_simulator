pipeline {
  agent any
  options {
    timestamps()
    ansiColor('xterm')
  }

  environment {
    PYTHON = 'python3'
    NODE_VERSION = '20'
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Backend') {
      steps {
        sh '''
          ${PYTHON} -m venv .venv
          . .venv/bin/activate
          pip install --upgrade pip
          pip install -r requirements.txt pytest ruff
          ruff check .
          pytest
        '''
      }
    }

    stage('Frontend build') {
      steps {
        sh '''
          . ${NVM_DIR:-$HOME/.nvm}/nvm.sh >/dev/null 2>&1 || true
          command -v npm >/dev/null 2>&1 || { echo "Please ensure Node ${NODE_VERSION} is installed on the Jenkins agent."; exit 1; }
          cd frontend-app
          npm install
          npm run build
        '''
      }
    }

    stage('Docker compose config') {
      steps {
        sh 'docker compose config'
      }
    }

    stage('End-to-End tests') {
      steps {
        sh '''
          npm install
          docker compose up -d --build
          npx playwright install --with-deps
          for i in $(seq 1 30); do
            curl -fsS http://localhost:8000/health && break
            sleep 2
          done
          E2E_BASE_URL=http://localhost:4173 npm run test:e2e
        '''
      }
      post {
        always {
          sh 'docker compose down -v || true'
        }
      }
    }
  }
}
