# Licence

<! --- SPDX-License-Identifier: CC-BY-4.0  -- >

## Scaling and Performance

In order to increase the throughput of the application as the load increases, it is necessary to increase the computing resources extra CPU (cores) can be allocated to the application.

To utilize the available resources, the number of workers should be configured correctly changing the configuration variable `FASTAPI:WORKERS` in `app/config/backend-portal-recommender-prod.yaml.`

For details, see [Configuration](configuration.md).
