# Fin-App Process Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Development Workflow](#development-workflow)
4. [Deployment Process](#deployment-process)
5. [Database Management](#database-management)
6. [Application Features](#application-features)
7. [Troubleshooting Guide](#troubleshooting-guide)
8. [Maintenance Procedures](#maintenance-procedures)

---

## 1. Project Overview

### What is Fin-App?
Fin-App is a personal finance tracking web application built with Flask (Python) and PostgreSQL. It allows users to:
- Track expenses with descriptions and amounts
- View all expenses in a chronological list
- Monitor application activity through detailed logs
- Access data through a clean, responsive web interface

### Technology Stack
- **Backend**: Python 3.9 with Flask framework
- **Database**: PostgreSQL 14
- **Frontend**: HTML, CSS (embedded), Jinja2 templating
- **Containerization**: Docker and Docker Compose
- **Logging**: Python logging module with file output

---

## 2. System Architecture

### Application Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │    │   Flask App     │    │   PostgreSQL    │
│   (Port 5001)   │◄──►│   (Port 5000)   │◄──►│   Database      │
│                 │    │                 │    │   (Port 5432)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### File Structure
```
fin-app/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
├── docker-compose.yml    # Multi-container orchestration
├── logs/                 # Application logs directory
│   └── app.log          # Main log file
└── templates/           # HTML templates
    ├── index.html       # Main expense tracker page
    └── activity.html    # Activity log viewer
```

### Data Flow
1. **User Request** → Web browser sends HTTP request
2. **Flask Routing** → App.py routes request to appropriate function
3. **Database Query** → PostgreSQL executes SQL queries
4. **Data Processing** → Flask processes data and logs activities
5. **Template Rendering** → Jinja2 renders HTML with data
6. **Response** → Browser displays the rendered page

---

## 3. Development Workflow

### Prerequisites
- Docker and Docker Compose installed
- Git for version control
- Code editor (VS Code recommended)

### Local Development Setup

#### Step 1: Clone and Navigate
```bash
cd /Users/lolaasher/FirstDevOps-Project/fin-app
git status  # Ensure you're in the right repo
```

#### Step 2: Build and Start Services
```bash
# Build and start all services
docker-compose up --build

# Or run in background (detached mode)
docker-compose up -d --build
```

#### Step 3: Access Application
- **Web Application**: http://localhost:5001
- **Database**: localhost:5432 (internal to containers)

#### Step 4: Development Process
1. **Make Code Changes** in your editor
2. **Test Changes** by refreshing browser
3. **Check Logs** with `docker-compose logs web`
4. **Commit Changes** with Git when satisfied

### Git Workflow
```bash
# Check current status
git status

# Add changes
git add .

# Commit with descriptive message
git commit -m "Add expense validation feature"

# Push to remote (if configured)
git push origin main
```

---

## 4. Deployment Process

### Container Management

#### Starting the Application
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f web
```

#### Stopping the Application
```bash
# Stop services (keeps data)
docker-compose stop

# Stop and remove containers (data persists in volumes)
docker-compose down

# Stop and remove everything including volumes (DANGER: deletes data)
docker-compose down -v
```

#### Updating the Application
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up --build -d
```

### Environment Configuration

#### Key Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `POSTGRES_USER`: Database username
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_DB`: Database name

#### Port Configuration
- **Host Port 5001** → **Container Port 5000** (Flask app)
- **Host Port 5432** → **Container Port 5432** (PostgreSQL)

---

## 5. Database Management

### Database Schema

#### Tables Structure

**expenses** table:
```sql
CREATE TABLE expenses (
    id SERIAL PRIMARY KEY,
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    created_at DATE DEFAULT CURRENT_TIMESTAMP
);
```

**activity_log** table:
```sql
CREATE TABLE activity_log (
    id SERIAL PRIMARY KEY,
    action_type TEXT NOT NULL,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Database Operations

#### Accessing Database Directly
```bash
# Connect to database container
docker-compose exec db psql -U user -d finance_db

# Common SQL commands
\dt              # List tables
\d expenses      # Describe expenses table
SELECT * FROM expenses LIMIT 5;  # View recent expenses
```

#### Database Backup
```bash
# Create backup
docker-compose exec db pg_dump -U user finance_db > backup_$(date +%Y%m%d).sql

# Restore backup
docker-compose exec -T db psql -U user finance_db < backup_20241027.sql
```

#### Database Reset
```bash
# DANGER: This will delete all data
docker-compose down -v
docker-compose up -d
```

---

## 6. Application Features

### Core Functionality

#### 1. Expense Tracking (`/` route)
**Purpose**: Main interface for adding and viewing expenses

**Process Flow**:
1. User fills out expense form (description + amount)
2. Flask validates form data
3. Data inserted into `expenses` table
4. Activity logged to `activity_log` table
5. Page redirects to show updated expense list
6. All expenses displayed in chronological order

**Key Code Section** (`app.py` lines 64-76):
```python
if request.method == 'POST':
    desc = request.form['description']
    amount = float(request.form['amount'])
    cur.execute('INSERT INTO expenses (description, amount) VALUES (%s, %s)', (desc, amount))
    conn.commit()
    log_activity(conn, "NEW_EXPENSE", f"Added '{desc}' for ${amount}")
```

#### 2. Activity Monitoring (`/activity` route)
**Purpose**: Comprehensive log of all application activities

**Process Flow**:
1. User navigates to `/activity`
2. Flask queries `activity_log` table
3. Results sorted by timestamp (newest first)
4. Data rendered in HTML table format

**Activity Types Logged**:
- `APP_START`: Application initialization
- `NEW_EXPENSE`: New expense entries
- Database connection events
- Error conditions

#### 3. Database Initialization (`init_db()` function)
**Purpose**: Ensures database schema exists

**Process Flow**:
1. Attempts database connection with retry logic
2. Creates tables if they don't exist
3. Logs successful initialization
4. Handles connection failures gracefully

---

## 7. Troubleshooting Guide

### Common Issues and Solutions

#### Issue 1: "Database connection failed"
**Symptoms**: App won't start, connection errors in logs

**Solutions**:
```bash
# Check if database container is running
docker-compose ps

# Restart database service
docker-compose restart db

# Check database logs
docker-compose logs db

# Verify environment variables
docker-compose config
```

#### Issue 2: "Port already in use"
**Symptoms**: `Error: Port 5001 is already allocated`

**Solutions**:
```bash
# Find process using port
lsof -i :5001

# Kill process (replace PID)
kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "5002:5000"  # Use port 5002 instead
```

#### Issue 3: "Volume mount issues"
**Symptoms**: Changes not reflected, permission errors

**Solutions**:
```bash
# Check volume status
docker volume ls

# Remove and recreate volumes
docker-compose down -v
docker-compose up -d
```

#### Issue 4: "Template not found"
**Symptoms**: `TemplateNotFound` error

**Solutions**:
```bash
# Verify templates directory exists
ls -la templates/

# Check file permissions
chmod 644 templates/*.html

# Restart container
docker-compose restart web
```

### Log Analysis

#### Application Logs Location
- **Container**: `/app/logs/app.log`
- **Host**: `./logs/app.log`

#### Key Log Patterns
```
# Successful startup
%(asctime)s - Chef is in the kitchen! The app is starting.
%(asctime)s - Successfully connected to the database.

# Database issues
%(asctime)s - Database isn't ready. Waiting and trying again...
%(asctime)s - Could not connect to the database. Is it running?

# User activities
%(asctime)s - User added a new expense: Coffee
```

#### Viewing Logs
```bash
# Real-time logs
docker-compose logs -f web

# Last 50 lines
docker-compose logs --tail=50 web

# Application log file
tail -f logs/app.log
```

---

## 8. Maintenance Procedures

### Regular Maintenance Tasks

#### Daily
- [ ] Check application accessibility (http://localhost:5001)
- [ ] Monitor log file size (`logs/app.log`)
- [ ] Verify database connectivity

#### Weekly
- [ ] Review application logs for errors
- [ ] Check disk space usage
- [ ] Backup database
- [ ] Update dependencies if needed

#### Monthly
- [ ] Review and archive old logs
- [ ] Performance analysis
- [ ] Security updates
- [ ] Documentation updates

### Performance Monitoring

#### Key Metrics to Monitor
1. **Response Time**: Page load speeds
2. **Database Connections**: Connection pool status
3. **Memory Usage**: Container resource consumption
4. **Log File Size**: Disk space management

#### Monitoring Commands
```bash
# Container resource usage
docker stats

# Database connections
docker-compose exec db psql -U user -d finance_db -c "SELECT count(*) FROM pg_stat_activity;"

# Log file size
ls -lh logs/app.log

# Disk usage
df -h
```

### Security Considerations

#### Best Practices Implemented
1. **Environment Variables**: Sensitive data not hardcoded
2. **SQL Injection Protection**: Parameterized queries used
3. **Container Isolation**: Services run in separate containers
4. **Port Management**: Only necessary ports exposed

#### Security Checklist
- [ ] Regular password updates
- [ ] Log access monitoring
- [ ] Container image updates
- [ ] Network security review

### Scaling Considerations

#### Current Limitations
- Single container deployment
- File-based logging
- No load balancing
- Manual backup process

#### Future Improvements
- Multiple application instances
- Centralized logging (ELK stack)
- Load balancer integration
- Automated backup systems
- Health check endpoints

---

## Quick Reference Commands

### Essential Docker Commands
```bash
# Start application
docker-compose up -d

# Stop application
docker-compose down

# View logs
docker-compose logs -f web

# Restart single service
docker-compose restart web

# Rebuild application
docker-compose up --build -d

# Database backup
docker-compose exec db pg_dump -U user finance_db > backup.sql

# Check service status
docker-compose ps

# Clean up (DANGER: deletes data)
docker-compose down -v
```

### Essential Git Commands
```bash
# Check status
git status

# Stage changes
git add .

# Commit changes
git commit -m "Description"

# Push changes
git push origin main

# View history
git log --oneline
```

---

This documentation provides a comprehensive guide for developing, deploying, and maintaining the Fin-App application. Keep this document updated as the application evolves and new features are added.
