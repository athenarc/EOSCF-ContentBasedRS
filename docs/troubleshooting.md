# Licence

<! --- SPDX-License-Identifier: CC-BY-4.0  -- >

## Troubleshooting

- Common operational issues and solutions.
- Guidelines for diagnosing problems.

### Discover connection problems to databases/APIs

Any connection issues with databases can be discovered by doing a `GET` request to the `/v1/health` endpoint. The response will contain the status of all databases. If the status is `DOWN`, it means that the connection to the database is not working. The response will also contain the error message.

**Example response**

```json
{
    "status": "UP",  # Up if everything below is working
    "catalog_api": {
        "status": "DOWN",
        "error": health_check_error,
        "database_type": "API"
    },
    "memory_store": {
        "status": "UP",
        "database_type": "Redis"
    }

}
```

### Autocompletion suggestions are failing

In order for the recommender to work some internal structures need to be created/initialized. While this is done automatically if something goes wrong during the initial creation of the structures you can manually request to create them again by doing a `GET` request to the `/v1/update` endpoint.
