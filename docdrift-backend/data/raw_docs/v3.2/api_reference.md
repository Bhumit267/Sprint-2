# API Reference - Version 3.2

## Overview
CloudCore API v3.2 enhances address verification and adds batch operation capabilities.

## Authentication
Requires an OAuth 2.0 Bearer token in the `Authorization` header:
`Authorization: Bearer <access_token>`

## Endpoints

### fetchAddress
Retrieves user address information filtered by classification type with optional automated postal normalization.

- **HTTP Method**: `GET`
- **Path**: `/api/v3.2/users/{userId}/addresses`
- **Parameters**:
  - `userId` (string, required): Customer identifier.
  - `addressType` (string, required): `"billing"` or `"shipping"`.
  - `geo` (boolean, optional, default: `false`): Include coordinate details.
  - `resolveNormalized` (boolean, optional, default: `false`): If true, runs postal normalization against national postal databases and adds validation flags.

### batchFetchAddresses
Retrieves addresses for multiple users in a single optimized request.

- **HTTP Method**: `POST`
- **Path**: `/api/v3.2/users/batch-addresses`
- **Request Body**:
  ```json
  {
    "userIds": ["usr_1", "usr_2"],
    "addressType": "shipping"
  }
  ```
