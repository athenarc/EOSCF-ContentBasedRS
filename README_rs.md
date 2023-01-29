# Recommendation System for EOSCF

The recommendation system component focuses on creating recommendations for a requested resource. So far, its data
source is only the mongo of the RS.

Use cases that are being implemented: https://wiki.eoscfuture.eu/display/EOSCF/RS+Content-based+Use+Cases

## V2 BREAKING

1. All the API urls have an added `v1` eg. `http://0.0.0.0:4559/similar_services/recommendation` -> `http://0.0.0.0:4559/v1/similar_services/recommendation`
2. The recommendation responses have changed to match [RecommendationSet](https://wiki.eoscfuture.eu/display/EOSCF/RS+facade#RSfacade-RecommendationSet)

```json
{
  "panel_id": "similar_services",
  "recommendations": [
    12, 23, ...
  ],
  "explanations": [
    "explanation1", "explanation2" ...
  ],
  "explanations_short": [
    "explanation_short1", "explanation_short2" ...
  ],
  "score": [
    0.7, 0.6, ...
  ],
  "engine_version": "v1"
}
```

## Building and Running

Prerequisites:

1. Read access to RS Mongo (from Cyfronet)
2. Read/write access to our Internal Mongo (from Athena)
3. Read/write access to our internal Redis storage

Build and run:

1. Make sure that you have added the `.env` file in the project root
2. Run `docker build -t rs-image . -f Dockerfile-rs`
3. Run `docker run -p <port>:4559 rs-image`

The image can be deployed using `docker-compose` if the `.env` variables are set correctly.

## Environment variables

The following variables should be set in the .env file

```shell
# These variable are of our internal mongo which is used for logging recommendations
# Should not be confused with the RS Mongo
CONTENT_BASED_RS_MONGO_HOST=content_based_recs_mongo # The hostname of the content_based_recs mongo
CONTENT_BASED_RS_MONGO_PORT=27017 # The port of the internal mongo
CONTENT_BASED_RS_MONGO_DATABASE=content_based_recs # The name of the database we are using for internal storage
CONTENT_BASED_RS_MONGO_USERNAME="admin" # The username of a user of the internal mongo deployed by compose
CONTENT_BASED_RS_MONGO_PASSWORD="admin" # The password of a user of the internal mongo deployed by compose

# RS Mongo (from Cyfronet)
RS_MONGO_HOST=localhost # The hostname of the external RS mongo
RS_MONGO_PORT=27017 # The port of the external RS mongo
RS_MONGO_DATABASE=rs_dump # The name of the RS database
RS_MONGO_USERNAME=dev # The username of a user of the external RS mongo
RS_MONGO_PASSWORD=dev # The password of a user of the external RS mongo

INTERNAL_REDIS_HOST=redis # The hostname of the internal redis deployed by compose
INTERNAL_REDIS_PORT=6379 # The port of the internal redis deployed by compose
INTERNAL_REDIS_PASSWORD=redis_pswd # The password of the internal redis deployed by compose

# The private sdn key for sentry which we use for error logging
SENTRY_SDN=https://12345...

# Cronitor is used to monitor the offline updating of our RS data structures
# stored in redis
CRONITOR_API_KEY=123aababdas...

# Monitoring access token is used to obtain reliability status of services in the portal before recommending them
MONITORING_API_ACCESS_TOKEN=daad2dasd...
```
