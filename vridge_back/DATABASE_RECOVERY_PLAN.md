# VideoPlanet Database Recovery Plan
**Author**: Victoria, Database Reliability Engineer  
**Date**: 2025-08-12  
**Version**: 1.0

## Executive Summary

This document outlines the comprehensive database recovery and optimization plan for VideoPlanet, addressing the `users_user.deletion_reason` field NULL constraint violation and establishing robust database reliability practices.

## Problem Analysis

### Root Cause
1. **Migration 0018** created `deletion_reason` field as `TextField(blank=True)` without `null=True`
2. **PostgreSQL** enforced NOT NULL constraint, causing IntegrityError on user operations
3. **Migration 0019** attempted to fix by adding `null=True` but existing constraint persisted
4. **Environment inconsistency** between SQLite (dev) and PostgreSQL (prod)

### Impact Assessment
- **Severity**: HIGH - User registration/update operations failing
- **Affected Systems**: Railway production environment
- **Data Risk**: LOW - No data corruption, only constraint violations
- **Downtime Risk**: MINIMAL - Zero-downtime migration available

## Recovery Strategy

### Phase 1: Immediate Stabilization (0-15 minutes)

#### Pre-Migration Checklist
- [ ] Confirm database connectivity
- [ ] Verify current user count and deletion_reason distribution
- [ ] Create backup of affected tables
- [ ] Test migration in staging environment
- [ ] Prepare rollback procedure

#### Execution Steps
```bash
# 1. Navigate to project directory
cd /home/winnmedia/VideoPlanet/vridge_back

# 2. Run pre-migration analysis
python3 database_analysis_report.py

# 3. Execute Railway migration fix
python3 scripts/railway_migration_fix.py

# 4. Verify migration success
python3 manage.py shell -c "
from users.models import User
user = User.objects.create_user('test_migration', 'test@example.com', 'password')
print('Migration successful:', user.deletion_reason == '')
user.delete()
"
```

#### Success Criteria
- ✅ Migration 0020 applied successfully
- ✅ User creation operations work without errors
- ✅ Soft delete functionality operational
- ✅ No data loss occurred

### Phase 2: Performance Optimization (15-30 minutes)

#### Database Optimization
```bash
# Apply performance optimizations
python3 scripts/database_optimization.py

# Verify optimization results
python3 scripts/db_health_check.py
```

#### Index Strategy
- **Soft Delete Index**: `(is_deleted, deleted_at, deletion_reason)` for efficient cleanup queries
- **Email Verification Index**: `(email_verified, email_verified_at)` for verification workflows
- **Notification Index**: `(recipient_id, notification_type, is_read)` for user notifications

#### Query Optimization
- Implement `select_related()` for User-Profile queries
- Add `prefetch_related()` for User-Notification relationships
- Use database-level defaults to minimize application-level processing

### Phase 3: Monitoring Setup (30-45 minutes)

#### Health Monitoring
- **Real-time Metrics**: Connection count, cache hit ratio, query performance
- **Alert Thresholds**: Connection usage >80%, slow queries >1s, cache hit <95%
- **Automated Health Checks**: Every 5 minutes with escalation procedures

#### Backup Strategy (3-2-1 Rule)
- **3 Copies**: Primary + 2 backups
- **2 Media Types**: Database + file system
- **1 Offsite**: Cloud storage with encryption

## Rollback Procedures

### Emergency Rollback (if Phase 1 fails)
```bash
# Immediate rollback to previous migration
python3 manage.py migrate users 0019

# Verify rollback success
python3 manage.py showmigrations users

# Test user operations
python3 manage.py shell -c "
from users.models import User
# Test user creation and soft delete operations
"
```

### Data Recovery (if data corruption occurs)
```bash
# 1. Stop application servers
# 2. Restore from most recent backup
pg_restore --clean --no-acl --no-owner -h $DB_HOST -U $DB_USER -d $DB_NAME $BACKUP_FILE

# 3. Apply migrations up to known good state
python3 manage.py migrate users 0019

# 4. Verify data integrity
python3 scripts/data_integrity_check.py
```

## Post-Recovery Verification

### Functional Testing
- [ ] User registration flow
- [ ] User authentication (all methods)
- [ ] Account deletion and recovery
- [ ] Email verification process
- [ ] Notification system
- [ ] Project creation and management

### Performance Testing
- [ ] User creation latency < 200ms
- [ ] Login response time < 100ms
- [ ] Notification queries < 50ms
- [ ] Soft delete operations < 100ms
- [ ] Database connection usage < 50%

### Data Consistency Checks
```sql
-- Verify deletion_reason field consistency
SELECT 
    COUNT(*) as total_users,
    COUNT(deletion_reason) as non_null_deletion_reason,
    COUNT(CASE WHEN deletion_reason = '' THEN 1 END) as empty_deletion_reason,
    COUNT(CASE WHEN is_deleted = true THEN 1 END) as deleted_users
FROM users_user;

-- Check for orphaned records
SELECT COUNT(*) FROM users_userprofile 
WHERE user_id NOT IN (SELECT id FROM users_user);
```

## Preventive Measures

### Development Process Improvements
1. **Migration Review Checklist**:
   - Field definitions include appropriate null/default constraints
   - Database backend compatibility verified
   - Data migrations tested with representative data volumes

2. **Testing Requirements**:
   - Unit tests for all model operations
   - Integration tests with PostgreSQL
   - Migration tests with production data samples

3. **Code Review Standards**:
   - Database changes require DBA approval
   - Migration scripts reviewed for performance impact
   - Rollback procedures documented for each change

### Monitoring Enhancements
1. **Proactive Alerts**:
   - Database constraint violations
   - Migration failures
   - Performance degradation trends

2. **Automated Health Checks**:
   - Continuous integration database tests
   - Staging environment parity validation
   - Production readiness gates

## Contact Information

### Escalation Procedures
1. **Level 1**: Development Team - Immediate response
2. **Level 2**: Database Administrator - Within 30 minutes
3. **Level 3**: Infrastructure Team - Within 1 hour
4. **Level 4**: External Database Consultant - Within 2 hours

### Emergency Contacts
- **Primary DBA**: Victoria (Database Reliability Engineer)
- **Backup DBA**: [To be assigned]
- **Infrastructure Lead**: [To be assigned]
- **Product Owner**: [To be assigned]

## Documentation Updates

### Required Updates After Recovery
- [ ] Update MEMORY.md with recovery actions
- [ ] Document new indexes in database schema
- [ ] Update deployment procedures
- [ ] Revise monitoring runbooks
- [ ] Update disaster recovery procedures

### Knowledge Transfer
- [ ] Team training on new monitoring tools
- [ ] Database optimization best practices session
- [ ] Migration review process training
- [ ] Incident response drill scheduling

## Appendix

### Migration Files Created
- `0020_fix_deletion_reason_constraint.py` - Primary fix migration
- `scripts/railway_migration_fix.py` - Production deployment script
- `scripts/database_optimization.py` - Performance optimization
- `scripts/db_health_check.py` - Continuous monitoring

### Performance Baselines
- **User Model Operations**: Target <100ms average
- **Notification Queries**: Target <50ms average  
- **Database Connections**: Target <30% utilization
- **Cache Hit Ratio**: Target >95%

### Compliance Notes
- All changes maintain GDPR compliance for user data
- Audit trail preserved for all database modifications
- Data retention policies remain unchanged
- Security access controls maintained

---

**Document Status**: ACTIVE  
**Next Review Date**: 2025-09-12  
**Approval Required**: Database Team Lead, Infrastructure Manager