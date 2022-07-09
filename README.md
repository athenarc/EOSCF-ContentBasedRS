# Recommendation System for EOSCF

The recommendation system component focuses on creating recommendations for a requested resource. So far, its data
source is only the mongo of the RS.

Use cases that are being implemented: https://wiki.eoscfuture.eu/display/EOSCF/RS+Content-based+Use+Cases

## Running

Prerequisites:
* docker, docker-compose

1. Make sure that you have added the `.env` file in the project root
2. Run `docker-compose -f docker-compose-app.yml up`
