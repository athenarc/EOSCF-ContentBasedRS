import argparse

import yaml
from dotenv import dotenv_values


def read_settings():
    parser = argparse.ArgumentParser(description="Recommendation System CMD.")
    parser.add_argument(
        "--config_file", help="path to config file", type=str, required=True
    )
    args = parser.parse_args()

    with open(args.config_file) as file:
        backend_settings = yaml.load(file, Loader=yaml.FullLoader)

    # We need to know if we are running in prod or dev env
    if 'prod' in args.config_file:
        backend_settings['PROD'] = True
    else:
        backend_settings['PROD'] = False

    credentials = dotenv_values(".env")

    return {
        'BACKEND': backend_settings,
        'CREDENTIALS': credentials,
    }


APP_SETTINGS = read_settings()
