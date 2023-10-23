# Licence

<! --- SPDX-License-Identifier: CC-BY-4.0  -- >

## Deployment

### Prerequisites

1. `docker`
2. `docker-compose`
3. `.env` file in the project root (check `configuration.md` for more info)

### Databases

1. Read only access to **RS Mongo** (deployed from Cyfronet)
2. Read/write access to our **Internal Mongo** (can be deployed with the `docker-compose` file)
3. Read/write access to our internal **Redis** storage (can be deployed with the `docker-compose` file)

### Build and run

1. Make sure that you have added the `.env` file in the project root
2. Run `docker build -t rs-image . -f Dockerfile-rs`
3. Run `docker run -p <port>:4559 rs-image`

We also provide the `docker-compose-rs.yml` file for convenience. It can be used to deploy the service with `docker-compose` if the `.env` variables are set correctly. However, extra network configuration is needed for the service to be able to access the RS Mongo (not deployed by the compose).
