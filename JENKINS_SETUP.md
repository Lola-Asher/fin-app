# Jenkins CI/CD Setup for Fin-App

## Overview
This document explains how to set up Jenkins to automatically build, test, and deploy your fin-app.

## Prerequisites

### 1. Install Jenkins
```bash
# On macOS with Homebrew
brew install jenkins

# Or using Docker
docker run -d -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkins/jenkins:lts
```

### 2. Required Jenkins Plugins
Install these plugins in Jenkins (Manage Jenkins → Manage Plugins):
- **Pipeline** - For pipeline support
- **Git** - For Git integration
- **Docker Pipeline** - For Docker commands
- **Blue Ocean** (optional) - Better UI for pipelines

### 3. System Requirements
- Docker and Docker Compose installed on Jenkins server
- Git access to your repository
- Ports 5001 (production), 5002 (staging), 5433 (staging DB) available

## Setup Steps

### Step 1: Configure Jenkins
1. **Access Jenkins**: http://localhost:8080
2. **Initial Setup**: Follow setup wizard
3. **Install Plugins**: Install required plugins listed above

### Step 2: Create Pipeline Job
1. **New Item** → **Pipeline** → Name: "fin-app-pipeline"
2. **Pipeline Section**:
   - Definition: "Pipeline script from SCM"
   - SCM: Git
   - Repository URL: Your git repository URL
   - Branch: */main
   - Script Path: Jenkinsfile

### Step 3: Configure Webhooks (Optional)
For automatic builds when you push code:
1. **GitHub**: Settings → Webhooks → Add webhook
   - URL: http://your-jenkins-server:8080/github-webhook/
   - Content type: application/json
   - Events: Push events

## Pipeline Stages Explained

### 1. **Checkout**
- Pulls latest code from Git repository
- Ensures Jenkins has current codebase

### 2. **Build**
- Runs `docker-compose build`
- Creates Docker images for your application

### 3. **Test**
- Starts application containers
- Performs health checks
- Verifies database connectivity
- Cleans up after testing

### 4. **Security Scan**
- Scans Docker images for vulnerabilities
- Uses Trivy security scanner (optional)

### 5. **Deploy to Staging**
- Deploys to staging environment (port 5002)
- Separate from production
- Safe testing environment

### 6. **Integration Tests**
- Tests actual application functionality
- Simulates user interactions
- Verifies API endpoints

### 7. **Deploy to Production**
- Only runs on main branch
- Backs up production database
- Updates production environment
- Performs final health checks

## Environment Configuration

### Production Environment
- **Web App**: http://localhost:5001
- **Database**: Internal PostgreSQL on port 5432
- **Logs**: Persistent Docker volume

### Staging Environment
- **Web App**: http://localhost:5002
- **Database**: Internal PostgreSQL on port 5433
- **Logs**: Separate staging volumes

## Running the Pipeline

### Manual Trigger
1. Go to Jenkins dashboard
2. Click "fin-app-pipeline"
3. Click "Build Now"

### Automatic Trigger
- Push code to repository
- Webhook triggers pipeline automatically
- Pipeline runs on every commit

### Branch-Specific Behavior
- **Feature branches**: Build + Test + Deploy to Staging
- **Main branch**: Full pipeline including Production deployment

## Monitoring and Logs

### Jenkins Console
- View real-time build logs
- Monitor pipeline progress
- Debug failures

### Application Logs
```bash
# Production logs
docker-compose logs -f web

# Staging logs
docker-compose -f docker-compose.staging.yml logs -f web
```

### Database Monitoring
```bash
# Check production database
docker-compose exec db psql -U user -d finance_db

# Check staging database
docker-compose -f docker-compose.staging.yml exec db psql -U user -d finance_db_staging
```

## Troubleshooting

### Common Issues

#### 1. **Port Conflicts**
```bash
# Find processes using ports
lsof -i :5001
lsof -i :5002

# Kill conflicting processes
kill -9 <PID>
```

#### 2. **Docker Permission Issues**
```bash
# Add Jenkins user to docker group
sudo usermod -aG docker jenkins

# Restart Jenkins
sudo systemctl restart jenkins
```

#### 3. **Pipeline Fails at Testing**
- Check if Docker Compose is installed
- Verify network connectivity
- Check port availability

#### 4. **Database Connection Failures**
- Ensure PostgreSQL container is healthy
- Check environment variables
- Verify database credentials

### Debug Commands
```bash
# Check Jenkins service
sudo systemctl status jenkins

# View Jenkins logs
sudo journalctl -u jenkins -f

# Check Docker containers
docker ps -a

# Check Docker networks
docker network ls
```

## Security Best Practices

### 1. **Secrets Management**
- Store database passwords in Jenkins credentials
- Use environment variables for sensitive data
- Never commit secrets to Git

### 2. **Access Control**
- Limit Jenkins access to authorized users
- Use role-based permissions
- Enable CSRF protection

### 3. **Network Security**
- Run Jenkins behind firewall
- Use HTTPS for Jenkins web interface
- Restrict Docker daemon access

## Scaling Considerations

### Multiple Environments
```yaml
# docker-compose.development.yml
# docker-compose.testing.yml  
# docker-compose.production.yml
```

### Multiple Instances
- Use different ports for each environment
- Separate databases per environment
- Independent Docker volumes

### Load Balancing
```yaml
# Add nginx load balancer
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
  depends_on:
    - web1
    - web2
```

## Backup Strategy

### Database Backups
```bash
# Automated backups in pipeline
docker-compose exec -T db pg_dump -U user finance_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Code Backups
- Git repository serves as code backup
- Jenkins stores build artifacts
- Docker images in registry

## Next Steps

### Advanced Features to Add
1. **Slack/Email Notifications**
2. **Automated Testing Suite**
3. **Performance Monitoring**
4. **Blue-Green Deployments**
5. **Infrastructure as Code (Terraform)**
6. **Container Registry Integration**

### Monitoring Integration
1. **Prometheus + Grafana**
2. **ELK Stack for Logs**
3. **Health Check Endpoints**
4. **Alerting Rules**

## Quick Commands Reference

```bash
# Start Jenkins
brew services start jenkins

# Access Jenkins
open http://localhost:8080

# Manual deployment
git push origin main  # Triggers pipeline

# Check pipeline status
# Go to Jenkins → fin-app-pipeline → Console Output

# Emergency rollback
docker-compose down
git checkout previous-working-commit
docker-compose up -d --build
```

This setup provides a complete CI/CD pipeline that automatically builds, tests, and deploys your fin-app whenever you push code changes!
