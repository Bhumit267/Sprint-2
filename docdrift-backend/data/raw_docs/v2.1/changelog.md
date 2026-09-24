# Changelog - Version 2.1

## Release 2.1.0 (2024-03-10)

### New Features
- Added the `include_coordinates` query parameter to the `getUserAddress` endpoint to allow downstream geocoding caching.
- Introduced response caching for `getUserProfile` to reduce latency.

### Bug Fixes
- Fixed an issue where postal codes containing alphanumeric characters were improperly truncated.
- Resolved intermittent timeouts during concurrent lookups on `/api/v2.1/users/{user_id}/address`.
