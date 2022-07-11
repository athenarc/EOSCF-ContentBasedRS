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
INTERNAL_MONGO_HOST=mongo # The host of the internal mongo deployed by compose
INTERNAL_MONGO_PORT=27017 # The port of the internal mongo deployed by compose
INTERNAL_MONGO_DATABASE=recommender # The name of the database we are using for internal storage
INTERNAL_MONGO_USERNAME="admin" # The username of a user of the internal mongo deployed by compose
INTERNAL_MONGO_PASSWORD="admin" # The password of a user of the internal mongo deployed by compose
# Currently we need the uri too, in a future version we will create it from the above variables
INTERNAL_MONGO_URI="mongodb://admin:admin@mongo:27017"

# RS Mongo
RS_MONGO_URI="mongodb://admin:admin@rs_mongo:27017"
RS_MONGO_DB=recommender # The name of the database used in the RS mongo

# The private sdn key for sentry which we use for error logging
SENTRY_SDN=https://12345...
```
