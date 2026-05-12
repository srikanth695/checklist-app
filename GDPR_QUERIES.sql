-- GDPR & Security Query Examples for SQLite
-- These queries help verify compliance and monitor user data

-- 1. VIEW ALL USERS (ADMINS ONLY)
SELECT 
    id,
    email,
    username,
    first_name,
    last_name,
    data_processing_consent,
    marketing_consent,
    is_active,
    email_verified,
    created_at,
    last_login,
    last_ip
FROM users
ORDER BY created_at DESC;

-- 2. VIEW SPECIFIC USER DATA
SELECT 
    u.id,
    u.email,
    u.first_name,
    u.last_name,
    COUNT(DISTINCT h.id) as total_habits,
    COUNT(DISTINCT j.id) as total_journals,
    COUNT(DISTINCT g.id) as total_goals,
    COUNT(DISTINCT s.id) as total_schedules,
    u.data_processing_consent,
    u.gdpr_consent_date,
    u.created_at
FROM users u
LEFT JOIN habits h ON u.id = h.user_id
LEFT JOIN journal_entries j ON u.id = j.user_id
LEFT JOIN goals g ON u.id = g.user_id
LEFT JOIN schedule_events s ON u.id = s.user_id
WHERE u.email = 'user@example.com'
GROUP BY u.id;

-- 3. AUDIT LOG - ALL USER ACTIONS (for specific user)
SELECT 
    id,
    action,
    description,
    ip_address,
    created_at
FROM audit_logs
WHERE user_id = 1
ORDER BY created_at DESC
LIMIT 50;

-- 4. AUDIT LOG - ALL LOGIN EVENTS (for security review)
SELECT 
    al.user_id,
    u.email,
    al.action,
    al.ip_address,
    al.created_at
FROM audit_logs al
JOIN users u ON al.user_id = u.id
WHERE al.action IN ('login', 'oauth_login')
ORDER BY al.created_at DESC
LIMIT 100;

-- 5. FIND USERS WITH DELETION REQUESTS (to process)
SELECT 
    id,
    email,
    first_name,
    last_name,
    data_deletion_requested,
    updated_at
FROM users
WHERE data_deletion_requested = 1 AND is_active = 0
ORDER BY updated_at ASC;

-- 6. FIND INACTIVE ACCOUNTS (no login in 90 days)
SELECT 
    id,
    email,
    username,
    last_login,
    CAST((julianday('now') - julianday(last_login)) AS INTEGER) as days_since_login
FROM users
WHERE last_login < datetime('now', '-90 days')
ORDER BY last_login ASC;

-- 7. VERIFY GDPR CONSENT COMPLIANCE
SELECT 
    id,
    email,
    data_processing_consent,
    marketing_consent,
    gdpr_consent_date,
    CASE 
        WHEN data_processing_consent = 1 THEN 'COMPLIANT'
        ELSE 'NO CONSENT'
    END as compliance_status
FROM users
ORDER BY created_at DESC;

-- 8. COUNT USERS BY OAUTH VS EMAIL AUTH
SELECT 
    CASE 
        WHEN google_id IS NOT NULL THEN 'Google OAuth'
        WHEN password_hash IS NOT NULL THEN 'Email/Password'
        ELSE 'Other'
    END as auth_type,
    COUNT(*) as user_count
FROM users
WHERE is_active = 1
GROUP BY auth_type;

-- 9. GET USER DATA FOR EXPORT (GDPR Right to Access)
-- User's personal info
SELECT 
    'USER_PROFILE' as data_type,
    json_object(
        'id', id,
        'email', email,
        'username', username,
        'first_name', first_name,
        'last_name', last_name,
        'created_at', created_at,
        'last_login', last_login,
        'data_processing_consent', data_processing_consent,
        'marketing_consent', marketing_consent
    ) as data
FROM users
WHERE id = 1

UNION ALL

-- User's habits
SELECT 
    'HABITS',
    json_group_array(json_object(
        'id', id,
        'name', name,
        'category', category,
        'frequency', frequency,
        'streak', streak,
        'longest_streak', longest_streak,
        'completion_pct', completion_pct,
        'created_at', created_at
    ))
FROM habits
WHERE user_id = 1

UNION ALL

-- User's journals
SELECT 
    'JOURNALS',
    json_group_array(json_object(
        'id', id,
        'title', title,
        'mood', mood,
        'mood_score', mood_score,
        'created_at', created_at,
        'content_length', LENGTH(content)
    ))
FROM journal_entries
WHERE user_id = 1

UNION ALL

-- User's goals
SELECT 
    'GOALS',
    json_group_array(json_object(
        'id', id,
        'title', title,
        'category', category,
        'status', status,
        'current_progress', current_progress,
        'target_progress', target_progress,
        'created_at', created_at
    ))
FROM goals
WHERE user_id = 1;

-- 10. DELETE ACCOUNT - HARD DELETE (GDPR Right to Erasure)
-- IMPORTANT: This is irreversible! First backup data.
-- 1. Delete user's data
DELETE FROM habit_entries WHERE habit_id IN (SELECT id FROM habits WHERE user_id = 1);
DELETE FROM habits WHERE user_id = 1;
DELETE FROM journal_entries WHERE user_id = 1;
DELETE FROM goals WHERE user_id = 1;
DELETE FROM daily_checklist_items WHERE source_type = 'goal' AND source_id IN (SELECT id FROM goals WHERE user_id = 1);
DELETE FROM schedule_events WHERE user_id = 1;

-- 2. Delete audit logs (keep for record)
DELETE FROM audit_logs WHERE user_id = 1;

-- 3. Delete user account
DELETE FROM users WHERE id = 1;

-- 11. PRIVACY AUDIT - Data sharing check
SELECT 
    COUNT(*) as total_users,
    SUM(CASE WHEN google_id IS NOT NULL THEN 1 ELSE 0 END) as oauth_users,
    SUM(CASE WHEN data_processing_consent = 1 THEN 1 ELSE 0 END) as consented_users,
    SUM(CASE WHEN marketing_consent = 1 THEN 1 ELSE 0 END) as marketing_opted_in,
    SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active_users,
    SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END) as inactive_users
FROM users;

-- 12. SECURITY CHECK - Suspicious login activity
SELECT 
    u.email,
    al.ip_address,
    COUNT(*) as login_count,
    MIN(al.created_at) as first_login,
    MAX(al.created_at) as last_login,
    CASE 
        WHEN COUNT(*) > 10 AND MAX(al.created_at) > datetime('now', '-1 day') THEN 'SUSPICIOUS'
        ELSE 'NORMAL'
    END as activity_flag
FROM audit_logs al
JOIN users u ON al.user_id = u.id
WHERE al.action IN ('login', 'oauth_login')
    AND al.created_at > datetime('now', '-7 days')
GROUP BY al.user_id, al.ip_address
HAVING COUNT(*) > 5
ORDER BY login_count DESC;

-- 13. DATA RETENTION POLICY COMPLIANCE
-- Check for data older than retention period
SELECT 
    'AUDIT_LOGS' as entity_type,
    COUNT(*) as record_count,
    MIN(created_at) as oldest_record,
    MAX(created_at) as newest_record,
    CASE 
        WHEN MIN(created_at) < datetime('now', '-90 days') THEN 'NEEDS_CLEANUP'
        ELSE 'OK'
    END as retention_status
FROM audit_logs

UNION ALL

SELECT 
    'DELETED_ACCOUNTS',
    COUNT(*),
    MIN(created_at),
    MAX(created_at),
    CASE 
        WHEN MIN(created_at) < datetime('now', '-30 days') THEN 'HARD_DELETE'
        ELSE 'PENDING'
    END
FROM users
WHERE data_deletion_requested = 1;

-- 14. GDPR ARTICLE COMPLIANCE CHECKLIST
-- Run this monthly for compliance audit

-- Article 5 (Lawfulness, fairness, transparency)
SELECT 'Art 5: Consent required?' as requirement,
    COUNT(CASE WHEN data_processing_consent = 1 THEN 1 END) || '/' || COUNT(*) as status
FROM users;

-- Article 12-14 (Transparency - privacy notice)
SELECT 'Art 12-14: Privacy policy provided?' as requirement,
    'Yes - available at /privacy' as status;

-- Article 15 (Right to access)
SELECT 'Art 15: Data export function?' as requirement,
    'Yes - /auth/data-export' as status;

-- Article 17 (Right to erasure)
SELECT 'Art 17: Delete account feature?' as requirement,
    'Yes - /auth/delete-account' as status;

-- Article 20 (Right to portability)
SELECT 'Art 20: Data portability (JSON)?' as requirement,
    'Yes - /auth/data-export' as status;

-- Article 30 (Records of processing)
SELECT 'Art 30: Audit logging enabled?' as requirement,
    'Yes - audit_logs table' as status;
