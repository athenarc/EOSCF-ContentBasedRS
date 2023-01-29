import argparse

import yaml
from dotenv import dotenv_values
from sentence_transformers import SentenceTransformer


def load_sbert_model(sbert_settings):
    model = SentenceTransformer(sbert_settings["MODEL_NAME"], device=sbert_settings["DEVICE"])
    model._model_card_vars["name"] = sbert_settings["MODEL_NAME"]

    return model


def read_settings(config_path=None):
    if config_path is None:
        parser = argparse.ArgumentParser(description="Recommendation System CMD.")
        parser.add_argument(
            "--config_file", help="path to config file", type=str, required=True
        )
        args = parser.parse_args()
        config_file = args.config_file
    else:
        config_file = config_path

    with open(config_file) as file:
        backend_settings = yaml.load(file, Loader=yaml.FullLoader)

    # We need to know if we are running in prod or dev env
    if 'prod' in config_file:
        backend_settings['PROD'] = True
    else:
        backend_settings['PROD'] = False

    credentials = dotenv_values(".env")

    backend_settings["SIMILAR_SERVICES"]["SBERT"]["MODEL"] = \
        load_sbert_model(backend_settings["SIMILAR_SERVICES"]["SBERT"])

    return {
        'BACKEND': backend_settings,
        'CREDENTIALS': credentials,
    }


def update_backend_settings(config_path):
    with open(config_path) as file:
        backend_settings = yaml.load(file, Loader=yaml.FullLoader)

    APP_SETTINGS['BACKEND'] = backend_settings
    APP_SETTINGS['BACKEND']["SIMILAR_SERVICES"]["SBERT"]["MODEL"] = \
        load_sbert_model(backend_settings["SIMILAR_SERVICES"]["SBERT"])


APP_SETTINGS = read_settings()
