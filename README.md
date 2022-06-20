# Recommendation System for EOSCF

The recommendation system component focuses on creating recommendations for a requested resource. So far, its data
source is the Marketplace (MP) and it implements the use case 1.5 (https://wiki.eoscfuture.eu/display/EOSCF/RS+Content-based+Use+Cases)

## Initial set up

Prerequisites:
* docker, docker-compose
* python >=3.9

**Step 1: Copy the dump file**
1. Copy the marketplace dump file (`.sql`) to `storage/dumps/marketplace/`

The final directory structure should look like:
* storage/dumps/
  * marketplace/
    * mp_dump_name.sql

**Step 2: Set up the credentials**
1. Change the default values for usernames and passwords in `credentials.yml`


## Running

1. Run `docker-compose -f docker-compose-app.yml up`
2. Populate db (only the first time):
   1. `docker exec --user postgres -i postgres sh -c "createdb mp_dump"`
   2. `docker exec --user postgres -i postgres sh -c "psql mp_dump < /dump/mp_db_name.sql"`
3. Go to `http://localhost:4557/docs`, you should be able to see the available requests
