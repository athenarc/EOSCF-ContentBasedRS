# Licence

<! --- SPDX-License-Identifier: CC-BY-4.0  -- >

## Introduction

The content-based-rs application uses both configuration files and environment variables to control its behaviour. We provide a detailed description of the configuration process below.

## Configuration Overview

The bare minimum configuration needed is creating the `.env` file in the root directory of the project. This file contains the environment variables needed to run the application.

One can then change the behavioral configuration file found in `app/config/backend-portal-recommender-prod.yaml` that has variables controlling fastapi settings and similar services model parameters.

- `.env`: Must be created, should never be committed to the repository.
- `app/config/backend-portal-recommender-prod.yaml`: Optional, the default values for the model configuration have been evaluated and work well.

## Configuration Files

The configuration file (`app/config/backend-portal-recommender-prod.yaml`) controls:

- The mode of the application (it should always be `"PORTAL-RECOMMENDER"`)
- `fastapi` configuration (workers, host, port, etc.)
- similar services model configuration

We provide a detailed example of the configuration file below:

```yaml
VERSION_NAME: "v3"  # Should be changed to differentiate between different versions of the model
                    # It is stored in the database and used for logging purposes along with each recommendation
MODE: "PORTAL-RECOMMENDER"  # Should always be "PORTAL-RECOMMENDER"

FASTAPI:  # Fastapi configuration
  WORKERS: 4
  DEBUG: False
  RELOAD: False
  HOST: '0.0.0.0'
  PORT: 4559

SCHEDULING:  # Decides the frequency of updating the internal structures of the model (embeddings, similarities)
  EVERY_N_HOURS: 6

SPACY_MODEL: "en_core_web_sm"  # Used for text processing. Using a bigger model did not affect performance

SIMILAR_SERVICES:

  METADATA: ["categories", "scientific_domains"]  # Which metadata fields of the services to use for the model
  TEXT_ATTRIBUTES: ["tagline", "description"]  # Which text attributes of the services to use for the model

  METADATA_WEIGHT: 0.25  # During similarity calculation the metadata and text attributes are weighted
                         # Text attributes are weighted by 1 - METADATA_WEIGHT
  VIEWED_WEIGHT: 0.5  # During recommendations how much weight to give to the services that the user is currently viewing vs. the history of ordered services

  DIVERSITY_WEIGHT: 0  # Emphasis given in diversity of recommendations. 0 means no diversity is considered. It leads to slight improvements but at a great performance cost.

  SENTENCE_FILTERING_METHOD: "KEYWORD"  # Possible values "NONE", "KEYWORD", "NER". Which technique to use to filter out non informative sentences.

  METHOD: "SBERT"  # Method used for calculating text embeddings. Currently only SBERT is supported.
  SBERT:  # SBERT configuration
    MODEL_NAME: 'paraphrase-MiniLM-L6-v2'
    DEVICE: "cpu"

PROJECT_ASSISTANT:  # Configuration for the project assistant. Currently not integrated with the frontend but is part of the API.
  SIMILARITY_THRESHOLD: 0.5  # The threshold of similarity between the user's query and the services

PROJECT_COMPLETION:  # Configuration for the project completion. Currently not integrated with the frontend but is part of the API.
  MIN_SUPPORT: 0.05
  MIN_CONFIDENCE: 0.5
```

## Environmental Variables

The environmental variables control integration with other services and databases. The `.env` file should be created in the root directory of the project and should contain the following variables:

```bash
# The internal mongo database (in initial deployment can be deployed through docker-compose)
CONTENT_BASED_RS_MONGO_HOST=localhost
CONTENT_BASED_RS_MONGO_PORT=27017
CONTENT_BASED_RS_MONGO_DATABASE=recommender
CONTENT_BASED_RS_MONGO_USERNAME=admin
CONTENT_BASED_RS_MONGO_PASSWORD=admin

# Mongo of the recommender the Cyfronet team
RS_MONGO_HOST=localhost
RS_MONGO_PORT=27017
RS_MONGO_DATABASE=database_name
RS_MONGO_USERNAME=admin
RS_MONGO_PASSWORD=admin

# Redis connection variables (deployed through docker-compose)
INTERNAL_REDIS_HOST=localhost
INTERNAL_REDIS_PORT=6379
INTERNAL_REDIS_PASSWORD=password

# Argo monitoring access token
MONITORING_API_ACCESS_TOKEN=asd1asd2

# Monitoring services
SENTRY_SDN=https://asd1asd2.ingest.sentry.io/asd1asd2
CRONITOR_API_KEY=asd1asd2
```

## Security Considerations

Each variable that affects the behavior of the model and is not considered secret should be added to the configuration file (`app/config/backend-portal-recommender-prod.yaml`).

The variables that are considered secret should be added to the `.env` file. The `.env` file should never be committed to the repository. It should be created manually on the server.
