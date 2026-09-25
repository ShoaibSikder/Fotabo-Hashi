# Supabase Storage media architecture

Fotabo Hashi uses Supabase Storage for media only. Django remains responsible
for authentication, authorization, validation, business rules, audit logging,
and the application PostgreSQL database. Supabase Auth and Supabase Database
are not part of this application.

## Configuration

Use `STORAGE_BACKEND=local` for offline/local development. Set
`STORAGE_BACKEND=supabase` only after providing the exact endpoint, region,
bucket, and server-only S3-compatible credentials from the Supabase project.
The bucket is `fotabo-hashi-media`, with `profiles/`, `founding-members/`, and
`slider/` prefixes.

The credential-bearing S3 access keys bypass Supabase Storage RLS. They must
remain server-side in deployment secrets and must never appear in React,
responses, logs, Git, screenshots, or public documentation. The Django API
authorizes every upload before it reaches storage.

## Visibility and lifecycle

Founding-member and slider assets may be publicly readable when the Supabase
bucket policy permits it. Public read never permits public write. Profile image
visibility follows the existing donor API policy; if this becomes more private,
use Supabase private objects and signed URLs rather than exposing credentials.

Object names are generated UUID paths; the original upload filename is never
stored or trusted. PostgreSQL stores only the object path, while the storage
layer generates provider URLs.

On replacement, upload and validate the new object, save the new database path,
then leave the old object as a reviewed cleanup candidate. Do not automate
destructive orphan deletion until media recovery rules exist: Supabase storage
objects are a separate recovery concern from the PostgreSQL backup.

The current 5 MB maximum is a security limit, not a quality target. Compress
images before upload to conserve the Supabase free-plan quota. Tests use local
or mocked storage and never contact a real Supabase project.
