# PostgreSQL RLS

Request authentication sets `app.user_id`, `app.is_authenticated`, and
`app.is_admin` on the active PostgreSQL connection. `ClearRLSContextMiddleware`
resets them after every request, which is required when persistent connections
are enabled.

The submitted email is temporarily stored as `app.login_email` only while the
login serializer verifies credentials; it permits access to that one account
row and is cleared immediately after the request.

Every application-owned table protected by this system is listed in
`policies.py`. New application tables must be evaluated for RLS before release.
