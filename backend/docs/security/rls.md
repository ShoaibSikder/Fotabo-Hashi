# PostgreSQL row-level security

Fotabo Hashi applies PostgreSQL RLS to every current application-owned table
with sensitive or managed data. Django/DRF permissions remain the primary
business-authorization layer; RLS is the second database boundary.

| Resource | Anonymous | User | Admin |
| --- | --- | --- | --- |
| User account | No access | Own row | All rows |
| Profile | No access | Own row | All rows |
| Blood requests | No access | Read all; mutate own | All rows |
| Organization information | Public read | Public read | Full access |
| Notices, founding members, slider items | Published only | Published only | Full access |
| Audit logs | No access | No read access | Read access |

The leaderboard has no RLS policy because no persisted ranking data source has
been defined. A donation-history model must not be invented merely to support a
leaderboard policy.

## Connection context

The JWT authenticator sets these PostgreSQL settings before protected queries:

- `app.user_id`
- `app.is_authenticated`
- `app.is_admin`

The connection-cleanup middleware resets them after every request. This is
essential because Django uses persistent database connections. During login,
`app.login_email` is set only long enough for the credential verifier to read
the submitted account row; it is cleared with the rest of the context.

The application database role must not be a PostgreSQL superuser, because a
superuser bypasses RLS. RLS policy changes are version-controlled in migrations,
not manually applied in pgAdmin.

Verify policy enforcement with PostgreSQL's relation catalog (the force flag is
stored in `pg_class`, not `pg_tables`):

```sql
SELECT c.relname, c.relrowsecurity, c.relforcerowsecurity
FROM pg_class AS c
JOIN pg_namespace AS n ON n.oid = c.relnamespace
WHERE n.nspname = 'public'
  AND c.relname IN (
    'accounts_user', 'profiles_profile', 'blood_requests_bloodrequest',
    'content_organizationinformation', 'content_notice',
    'content_foundingmember', 'content_slideritem', 'audit_auditlog'
  );
```

## Maintenance

The authoritative protected-table registry is
`infrastructure.database.rls.policies.RLS_TABLES`. Evaluate every new
application-owned model for an RLS policy and add direct database tests under
`tests/security/rls/` before release.
