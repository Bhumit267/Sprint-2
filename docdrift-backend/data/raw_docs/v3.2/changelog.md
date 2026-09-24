# Changelog - Version 3.2

## Release 3.2.0 (2025-01-20)

### New Features
- Added `resolveNormalized` query parameter to `fetchAddress` to enable address cleansing and postal format verification.
- Introduced `batchFetchAddresses` (`POST /api/v3.2/users/batch-addresses`) for bulk retrieval of up to 50 addresses per request.

### Performance Improvements
- Improved database indexing for geographic coordinate queries.
