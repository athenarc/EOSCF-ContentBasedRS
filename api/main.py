import logging

import sentry_sdk
import uvicorn

logging.basicConfig(level=logging.INFO, format='%(levelname)s | %(asctime)s | %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S')

from api.routes.add_routes import initialize_routes
from api.settings import APP_SETTINGS
from fastapi import FastAPI

sentry_sdk.init(
    dsn=APP_SETTINGS['CREDENTIALS']['SENTRY_SDN'],
    traces_sample_rate=1.0
)
if not APP_SETTINGS['BACKEND']['PROD']:
    sentry_sdk.init()  # Disable sentry if we are not in a dev environment

app = FastAPI()

initialize_routes(app)


@app.get("/health")
def health_check():
    return {"message": "App has initialised and is running"}


def start_app():
    uvicorn.run("api.main:app",
                host=APP_SETTINGS['BACKEND']['FASTAPI']['HOST'],
                port=APP_SETTINGS['BACKEND']['FASTAPI']['PORT'],
                reload=APP_SETTINGS['BACKEND']['FASTAPI']['RELOAD'],
                debug=APP_SETTINGS['BACKEND']['FASTAPI']['DEBUG'],
                workers=APP_SETTINGS['BACKEND']['FASTAPI']['WORKERS'],
                reload_dirs=["recommendation_system/api"])


if __name__ == '__main__':
    start_app()
