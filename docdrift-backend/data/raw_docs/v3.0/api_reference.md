# API Reference - Version 3.0

## Overview
CloudCore API v3.0 introduces camelCase schema standards, granular address categorization, and strict OAuth2 Bearer token authentication.

## Authentication
Requests require an OAuth 2.0 Bearer token in the `Authorization` header:
`Authorization: Bearer <access_token>`

## Endpoints

### fetchAddress
Retrieves user address information filtered by classification type. Replaces the legacy `getUserAddress` method.

- **HTTP Method**: `GET`
- **Path**: `/api/v3.0/users/{userId}/addresses`
- **Path Parameters**:
  - `userId` (string, required): The unique customer identifier.
- **Query Parameters**:
  - `addressType` (string, required): The target address category. Accepted values: `"billing"`, `"shipping"`.
  - `geo` (boolean, optional, default: `false`): When true, includes latitude and longitude coordinates in the response.
- **Response (200 OK)**:
  ```json
  {
    "userId": "usr_9812",
    "addressType": "billing",
    "street": "100 Innovation Way",
    "city": "Austin",
    "postalCode": "78701",
    "countryCode": "US",
    "geo": null
  }
  ```

### fetchProfile
Retrieves member account configuration and subscription details. Replaces `getUserProfile`.

- **HTTP Method**: `GET`
- **Path**: `/api/v3.0/users/{userId}/profile`
