# Database and API performance

## Query paths

- Donor discovery is filtered to available profiles, deterministically ordered
  by `name, id`, paginated, and does not join `accounts_user` because its
  serializer never reads it.
- Blood-request listings use `select_related('requester', 'requester__profile')`
  because the response reads `requester.profile.name`. This prevents an N+1
  relationship query pattern.
- Public content remains Redis-cached. It is intentionally not over-indexed.

## Index decisions

`profiles_profile` has `profile_donor_group_idx` on
`(is_available_for_donation, blood_group)`, matching the common available-donor
plus-blood-group filter. The existing blood-request indexes already match the
status, group, requester, and timestamp query paths, so no speculative general
listing index was added.

Use `infrastructure.database.performance.explain_query()` for safe,
non-mutating plan inspection. Production `EXPLAIN ANALYZE` should only run in a
controlled environment, never blindly against live traffic.

## Regression coverage

`tests/performance/` verifies that donor and blood-request query counts stay
constant as result counts grow, caps requested page size at 100, checks stable
page separation, and confirms representative querysets remain explainable.
