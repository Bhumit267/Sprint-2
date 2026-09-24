# Changelog - Version 3.0

## Release 3.0.0 (2024-08-15)

### Breaking Changes
- Replaced `getUserAddress` with `fetchAddress`.
- Replaced `getUserProfile` with `fetchProfile`.
- Transitioned query and body parameter naming from `snake_case` to `camelCase`.
- Replaced `X-API-Key` authentication with OAuth 2.0 Bearer tokens.

### Deprecations
- Removed legacy XML response serialization; all responses are now strictly application/json.
