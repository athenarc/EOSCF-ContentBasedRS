# Recommendation System for EOSCF

The recommendation system component focuses on creating recommendations for a requested resource. So far, its data
source is only the mongo of the RS.

Use cases that are being implemented: https://wiki.eoscfuture.eu/display/EOSCF/RS+Content-based+Use+Cases

## Running

Prerequisites:
* docker, docker-compose

1. Make sure that you have added the `.env` file in the project root
2. Run `docker-compose -f docker-compose-app.yml up`

## Environment variables

The following variables should be set in the .env file

```shell
# These variable are of our mongo which will be used for logging recommendations
# Should not be confused with the RS Mongo
INTERNAL_MONGO_HOST=internal_mongo # The hostname of the internal mongo deployed by compose
INTERNAL_MONGO_PORT=27017 # The port of the internal mongo deployed by compose
INTERNAL_MONGO_DATABASE=internal_recommender # The name of the database we are using for internal storage
INTERNAL_MONGO_USERNAME="admin" # The username of a user of the internal mongo deployed by compose
INTERNAL_MONGO_PASSWORD="admin" # The password of a user of the internal mongo deployed by compose

# RS Mongo (from Cyfronet)
RS_MONGO_HOST=localhost # The hostname of the external RS mongo
RS_MONGO_PORT=27017 # The port of the external RS mongo
RS_MONGO_DATABASE=rs_dump # The name of the RS database
RS_MONGO_USERNAME=admin # The username of a user of the external RS mongo
RS_MONGO_PASSWORD=admin # The password of a user of the external RS mongo

INTERNAL_REDIS_HOST=redis # The hostname of the internal redis deployed by compose
INTERNAL_REDIS_PORT=6379 # The port of the internal redis deployed by compose
INTERNAL_REDIS_PASSWORD=redis_pswd # The password of the internal redis deployed by compose

# The private sdn key for sentry which we use for error logging
SENTRY_SDN=https://12345...

# Cronitor is used to monitor the offline updating of our RS data structures
# stored in redis
CRONITOR_API_KEY=123aababdas...
```
