import argparse

import yaml


def read_settings():
    parser = argparse.ArgumentParser(description="Recommendation System CMD.")
    parser.add_argument(
        "--config_file", help="path to config file", type=str, required=True
    )
    args = parser.parse_args()

    with open(args.config_file) as file:
        backend_settings = yaml.load(file, Loader=yaml.FullLoader)

    with open(backend_settings['CREDENTIALS']) as file:
        credentials = yaml.load(file, Loader=yaml.FullLoader)

    return {
        'BACKEND': backend_settings,
        'CREDENTIALS': credentials,
        'METADATA': backend_settings['METADATA'],
        'SBERT': backend_settings['SBERT'],
        'EMBEDDINGS_STORAGE_PATH': backend_settings['EMBEDDINGS_STORAGE_PATH'],
        'SIMILARITIES_STORAGE_PATH': backend_settings['SIMILARITIES_STORAGE_PATH']
    }


APP_SETTINGS = read_settings()
