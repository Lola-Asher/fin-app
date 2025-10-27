# Fin-App Credentials Management Guide

## Why Credentials Matter

### Security Benefits
- **Encrypted Storage**: Passwords stored securely in Jenkins
- **Environment Separation**: Different credentials for dev/staging/prod
- **Access Control**: Only authorized Jenkins jobs can use credentials
- **Audit Trail**: Track who uses which credentials when
- **Easy Rotation**: Update passwords without changing code

### Compliance Requirements
- No passwords in source code
- No passwords in Git history
- Encrypted credential storage
- Role-based access control

## Setting Up Credentials in Jenkins

### Step 1: Access Credentials Manager
1. Open Jenkins: http://localhost:8080
2. Click "Manage Jenkins"
3. Click "Manage Credentials"
4. Click "Global" domain
5. Click "Add Credentials"

### Step 2: Add Database Credentials

#### Database Username
```
Kind: Secret text
ID: fin-app-db-user
Secret: finapp_user
Description: Database username for fin-app
```

#### Database Password
```
Kind: Secret text
ID: fin-app-db-password
Secret: YourSecurePassword123!
Description: Database password for fin-app
```

#### Database Name
```
Kind: Secret text
ID: fin-app-db-name
Secret: finance_db
Description: Database name for fin-app
```

### Step 3: Verify Credentials
- Credentials should appear in the credentials list
- They should show as "Secret text" type
- Passwords should be hidden (not visible)

## Environment Configuration

### Development Environment
```yaml
# docker-compose.yml (for local development only)
environment:
  - POSTGRES_USER=dev_user
  - POSTGRES_PASSWORD=dev_password
  - POSTGRES_DB=finance_db_dev
```

### Staging Environment
```yaml
# docker-compose.staging.yml (uses Jenkins credentials)
environment:
  - POSTGRES_USER=${DB_USER}
  - POSTGRES_PASSWORD=${DB_PASSWORD}
  - POSTGRES_DB=${DB_NAME}_staging
```

### Production Environment
```yaml
# docker-compose.prod.yml (uses Jenkins credentials)
environment:
  - POSTGRES_USER=${DB_USER}
  - POSTGRES_PASSWORD=${DB_PASSWORD}
  - POSTGRES_DB=${DB_NAME}
```

## Best Practices

### Password Requirements
- **Minimum 12 characters**
- **Mix of uppercase, lowercase, numbers, symbols**
- **No dictionary words**
- **Unique per environment**

Example strong passwords:
- `Fn@pp_St4g1ng_2024!`
- `Pr0d_F1nApp_S3cur3#`

### Credential Rotation
1. **Monthly**: Change staging passwords
2. **Quarterly**: Change production passwords
3. **Immediately**: If credentials are compromised

### Access Control
- Only DevOps team should manage credentials
- Developers should not see production passwords
- Use separate credentials for each environment

## Troubleshooting

### Common Issues

#### 1. "Credential not found"
**Cause**: Wrong credential ID in Jenkinsfile
**Solution**: Check ID matches exactly
```groovy
// In Jenkinsfile
DB_USER = credentials('fin-app-db-user')  // Must match Jenkins ID
```

#### 2. "Authentication failed"
**Cause**: Wrong password in credential
**Solution**: Update credential in Jenkins

#### 3. "Environment variable not set"
**Cause**: Credential not properly injected
**Solution**: Check Jenkins credential binding

### Debug Commands
```bash
# Check if environment variables are set (in Jenkins pipeline)
echo "DB_USER: ${DB_USER}"
echo "DB_NAME: ${DB_NAME}"
# Note: Never echo DB_PASSWORD in logs!

# Test database connection
docker-compose exec db psql -U ${DB_USER} -d ${DB_NAME} -c "SELECT 1;"
```

### Verify Credentials Are Working
```bash
# In Jenkins pipeline console output, you should see:
# [Pipeline] withCredentials
# Masking supported pattern matches of $DB_PASSWORD
```

## Security Checklist

### Before Production
- [ ] All passwords are strong and unique
- [ ] No passwords in source code
- [ ] No passwords in Git history
- [ ] Credentials stored in Jenkins securely
- [ ] Access control configured
- [ ] Backup and recovery plan for credentials

### Regular Maintenance
- [ ] Monthly password rotation for staging
- [ ] Quarterly password rotation for production  
- [ ] Annual security audit
- [ ] Keep credential access logs
- [ ] Update documentation when credentials change

## Emergency Procedures

### If Credentials Are Compromised
1. **Immediately** change passwords in Jenkins
2. **Restart** all affected services
3. **Audit** access logs
4. **Review** who had access
5. **Update** incident response documentation

### If Jenkins Is Compromised
1. **Revoke** all database access
2. **Change** all passwords
3. **Rebuild** Jenkins with new credentials
4. **Audit** all deployments since compromise

This credential management ensures your fin-app is production-ready and secure!
