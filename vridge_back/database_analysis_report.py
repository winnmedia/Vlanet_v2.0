#!/usr/bin/env python3
"""
VideoPlanet Database Issue Analysis Script
Author: Victoria, Database Reliability Engineer

This script analyzes the deletion_reason field issue and provides recommendations.
"""

import os
import sys
import django

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.railway')
django.setup()

from django.db import connection
from django.core.management.color import make_style
from users.models import User

style = make_style()

def analyze_deletion_reason_issue():
    """Analyze the deletion_reason field issue"""
    
    print(style.SUCCESS("=== VideoPlanet Database Analysis Report ==="))
    print()
    
    # 1. Current Model Analysis
    print(style.SUCCESS("1. Current Model Field Definition:"))
    field = User._meta.get_field('deletion_reason')
    print(f"   - Field Type: {type(field).__name__}")
    print(f"   - Max Length: {field.max_length}")
    print(f"   - Null Allowed: {field.null}")
    print(f"   - Blank Allowed: {field.blank}")
    print(f"   - Default Value: '{field.default}'")
    print()
    
    # 2. Database Backend Analysis
    print(style.SUCCESS("2. Current Database Backend:"))
    db_backend = connection.vendor
    print(f"   - Database: {db_backend}")
    print(f"   - Database Name: {connection.settings_dict['NAME']}")
    print()
    
    # 3. Migration History Analysis
    print(style.SUCCESS("3. Migration Analysis:"))
    print("   - 0018_add_deletion_reason.py: TextField(blank=True) [ISSUE: null=True missing]")
    print("   - 0019_alter_user_deletion_reason_default.py: CharField(null=True, blank=True, default='')")
    print("   - Current Model: CharField(null=True, blank=True, default='')")
    print()
    
    # 4. Issue Identification
    print(style.ERROR("4. Identified Issues:"))
    print("   ❌ Migration 0018 created field without null=True")
    print("   ❌ PostgreSQL enforces NOT NULL constraint from migration 0018")
    print("   ❌ Migration 0019 attempts to add null=True but constraint may still exist")
    print("   ❌ Potential data inconsistency between environments")
    print()
    
    # 5. Risk Assessment
    print(style.WARNING("5. Risk Assessment:"))
    print("   - HIGH: User creation/update operations failing with IntegrityError")
    print("   - MEDIUM: Data inconsistency between SQLite (dev) and PostgreSQL (prod)")
    print("   - LOW: Existing user data may have empty string vs null inconsistency")
    print()
    
    # 6. Test current state if possible
    print(style.SUCCESS("6. Current State Test:"))
    try:
        # Test if we can create a user without deletion_reason
        test_data = {
            'username': 'test_user_deletion_reason',
            'email': 'test_deletion@example.com'
        }
        print(f"   - Testing user creation without deletion_reason...")
        
        # Clean up any existing test user first
        User.objects.filter(username=test_data['username']).delete()
        
        # Test creation
        user = User(**test_data)
        user.save()
        
        print(f"   ✅ User creation successful")
        print(f"   - deletion_reason value: '{user.deletion_reason}'")
        print(f"   - deletion_reason is None: {user.deletion_reason is None}")
        print(f"   - deletion_reason is empty string: {user.deletion_reason == ''}")
        
        # Clean up
        user.delete()
        
    except Exception as e:
        print(f"   ❌ User creation failed: {e}")
    
    print()
    
    return True

def generate_migration_strategy():
    """Generate safe migration strategy"""
    
    print(style.SUCCESS("=== Recommended Migration Strategy ==="))
    print()
    
    print(style.SUCCESS("PHASE 1: Immediate Fix (Zero-downtime)"))
    print("1. Create data migration to ensure all existing users have valid deletion_reason")
    print("2. Update existing NULL values to empty string ('')")
    print("3. Verify constraint compatibility")
    print()
    
    print(style.SUCCESS("PHASE 2: Schema Correction"))
    print("1. Create new migration to properly set field constraints")
    print("2. Ensure field allows NULL OR has default value")
    print("3. Add proper indexes for soft delete queries")
    print()
    
    print(style.SUCCESS("PHASE 3: Data Integrity Verification"))
    print("1. Run data consistency checks")
    print("2. Verify all soft delete operations work correctly")
    print("3. Test user creation/update operations")
    print()
    
    print(style.WARNING("ROLLBACK STRATEGY:"))
    print("- Keep backup of current schema state")
    print("- Create reverse migration for each phase")
    print("- Test rollback procedure in staging environment")
    print()

if __name__ == '__main__':
    try:
        analyze_deletion_reason_issue()
        generate_migration_strategy()
    except Exception as e:
        print(style.ERROR(f"Analysis failed: {e}"))
        sys.exit(1)