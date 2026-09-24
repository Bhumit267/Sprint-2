# Migration Guide - Upgrading from v2.x to v3.0

## Breaking Changes Summary
CloudCore v3.0 is a major release containing breaking API contract changes, field renaming, and security updates.

## Migrating from getUserAddress to fetchAddress
The `getUserAddress` endpoint has been deprecated and completely removed. Integrators must switch to `fetchAddress`.

1. **Path & Method Changes**:
   - v2.x: `GET /api/v2.1/users/{user_id}/address`
   - v3.0: `GET /api/v3.0/users/{userId}/addresses`
2. **Parameter Renaming**:
   - `user_id` has been renamed to `userId`.
   - `include_coordinates` has been renamed to `geo`.
3. **Mandatory Classification**:
   - You must now supply `addressType` query parameter (`billing` or `shipping`). Requests lacking this parameter will return HTTP `400 Bad Request`.
4. **Payload Field Renaming**:
   - `zip_code` has been replaced by `postalCode`.
   - `countryCode` is now always returned as an ISO-3166 alpha-2 string.

## Authentication Migration
The `X-API-Key` header is no longer accepted. All calls must authenticate with `Authorization: Bearer <access_token>`.
