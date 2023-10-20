# Licence

<! --- SPDX-License-Identifier: CC-BY-4.0  -- >

## Monitoring and Logging

For monitoring we use two main tools:

- Sentry, which is used for error tracking
- Cronitor, which is used for monitoring the health of the services

Both tools can be set up using the following environment variables:

- `SENTRY_SDN=https://asd1asd2.ingest.sentry.io/asd1asd2`
- `CRONITOR_API_KEY=asd1asd2`

In the internal mongo of the architecture the generated recommendations are also logged under the `recommendation` collection. The schema of the collection is the following:

```json
{
    "date": "2021-06-01T12:00:00.000Z",
    "version": "v2",
    "service_id": 12,
    "recommendation": [15, 16, 29, 102],
    "user_id": 7594, (None if anonymous)
    "history_service_ids": [2, 65]
}
```
