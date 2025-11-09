pipeline {
    agent any
    
    environment {
        // Define environment variables
        DOCKER_IMAGE = 'fin-app'
        DOCKER_TAG = "${BUILD_NUMBER}"
        COMPOSE_PROJECT_NAME = "fin-app-${BUILD_NUMBER}"
        // Add Docker to PATH
        PATH = "/usr/local/bin:/opt/homebrew/bin:${env.PATH}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code from Git...'
                checkout scm
            }
        }
        
        stage('Build') {
            steps {
                echo 'Building Docker images...'
                script {
                    // Build the application
                    sh 'docker compose build'
                }
            }
        }
        
        stage('Test') {
            steps {
                echo 'Running tests...'
                script {
                    // Start services for testing
                    sh 'docker compose up -d'
                    
                    // Wait for services to be ready
                    sh 'sleep 30'
                    
                    // Basic health check
                    sh '''
                        # Check if web service is responding
                        curl -f http://localhost:5001 || exit 1
                        
                        # Check if database is accessible
                        docker compose exec -T db psql -U user -d finance_db -c "SELECT 1;" || exit 1
                    '''
                }
            }
            post {
                always {
                    // Clean up test environment
                    sh 'docker compose down -v'
                }
            }
        }
        
        stage('Security Scan') {
            steps {
                echo 'Running security scans...'
                script {
                    // Scan Docker images for vulnerabilities
                    sh '''
                        # Install trivy if not present
                        if ! command -v trivy &> /dev/null; then
                            echo "Trivy not found, skipping security scan"
                        else
                            trivy image fin-app-web:latest
                        fi
                    '''
                }
            }
        }
        
        stage('Deploy to Staging') {
            steps {
                echo 'Deploying to staging environment...'
                script {
                    // Deploy to staging (different port to avoid conflicts)
                    sh '''
                        # Stop any existing staging deployment
                        docker compose -f docker-compose.staging.yml down -v || true
                        
                        # Start staging deployment
                        docker compose -f docker-compose.staging.yml up -d
                        
                        # Wait for deployment
                        sleep 15
                        
                        # Verify staging deployment
                        curl -f http://localhost:5002 || exit 1
                    '''
                }
            }
        }
        
        stage('Integration Tests') {
            steps {
                echo 'Running integration tests...'
                script {
                    sh '''
                        # Test adding an expense
                        curl -X POST http://localhost:5002 \\
                             -d "description=Test Expense&amount=10.50" \\
                             -H "Content-Type: application/x-www-form-urlencoded"
                        
                        # Test activity log
                        curl -f http://localhost:5002/activity
                    '''
                }
            }
        }
        
        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                echo 'Deploying to production...'
                script {
                    // Production deployment
                    sh '''
                        # Backup current production database
                        docker compose -f docker-compose.prod.yml exec -T db pg_dump -U user finance_db > backup_$(date +%Y%m%d_%H%M%S).sql || true
                        
                        # Deploy to production
                        docker compose -f docker-compose.prod.yml down
                        docker compose -f docker-compose.prod.yml up -d --build
                        
                        # Wait for services
                        sleep 20
                        
                        # Health check
                        curl -f http://localhost:5001 || exit 1
                    '''
                }
            }
        }
    }
    
    post {
        always {
            echo 'Cleaning up...'
            script {
                // Clean up staging environment
                sh 'docker compose -f docker-compose.staging.yml down -v || true'
                
                // Clean up unused Docker images
                sh 'docker image prune -f || true'
            }
        }
        
        success {
            echo 'Pipeline completed successfully!'
            // Send success notification
            script {
                sh '''
                    echo "✅ Fin-App deployment successful!" 
                    echo "Build: ${BUILD_NUMBER}"
                    echo "Branch: ${BRANCH_NAME}"
                    echo "Commit: ${GIT_COMMIT}"
                '''
            }
        }
        
        failure {
            echo 'Pipeline failed!'
            // Send failure notification
            script {
                sh '''
                    echo "❌ Fin-App deployment failed!"
                    echo "Build: ${BUILD_NUMBER}"
                    echo "Branch: ${BRANCH_NAME}"
                    echo "Check Jenkins logs for details"
                '''
            }
        }
    }
}
