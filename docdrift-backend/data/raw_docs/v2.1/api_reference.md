# API Reference - Version 2.1

## Overview
The CloudCore API v2.1 allows developers to manage user accounts, addresses, and team permissions using RESTful JSON endpoints.

## Authentication
Pass your API secret key in the HTTP request headers:
`X-API-Key: <your_api_key>`

## Endpoints

### getUserAddress
Retrieves the registered postal address for a specific user ID.

- **HTTP Method**: `GET`
- **Path**: `/api/v2.1/users/{user_id}/address`
- **Path Parameters**:
  - `user_id` (string, required): The unique customer identifier.
- **Query Parameters**:
  - `include_coordinates` (boolean, optional, default: `false`): If true, appends latitude and longitude coordinates.
- **Response (200 OK)**:
  ```json
  {
    "user_id": "usr_9812",
    "street": "100 Innovation Way",
    "city": "Austin",
    "zip_code": "78701",
    "coordinates": null
  }
  ```

### getUserProfile
Fetches core user account details including primary contact email and tier status.

- **HTTP Method**: `GET`
- **Path**: `/api/v2.1/users/{user_id}`
- **Parameters**: `user_id` (string, required).
