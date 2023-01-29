import logging

import api.scheduling.initialization
import sentry_sdk
import uvicorn
from api.databases.content_based_rec_db import ContentBasedRecsMongoDB
from api.settings import APP_SETTINGS

logging.basicConfig(level=logging.INFO if APP_SETTINGS['BACKEND']['PROD'] else logging.DEBUG,
                    format='%(levelname)s | %(asctime)s | %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S')

from api.routes.add_routes import initialize_routes
from fastapi import FastAPI

sentry_sdk.init(
    dsn=APP_SETTINGS['CREDENTIALS']['SENTRY_SDN'],
    traces_sample_rate=1.0
)
if not APP_SETTINGS['BACKEND']['PROD']:
    sentry_sdk.init()  # Disable sentry if we are not in a dev environment

app = FastAPI()
initialize_routes(app)


@app.on_event("startup")
async def startup_event():
    # Keep track of the RS version we are running (specified in config file)
    if APP_SETTINGS["BACKEND"]["MODE"] == "RS":
        db = ContentBasedRecsMongoDB()
        db.update_version()


def start_app():
    # The update scheduler starts before uvicorn creates many workers
    # The following call will also create necessary structures if they do not exist in redis
    api.scheduling.initialization.start_updating_process()

    uvicorn.run("api.main:app",
                host=APP_SETTINGS['BACKEND']['FASTAPI']['HOST'],
                port=APP_SETTINGS['BACKEND']['FASTAPI']['PORT'],
                reload=APP_SETTINGS['BACKEND']['FASTAPI']['RELOAD'],
                debug=APP_SETTINGS['BACKEND']['FASTAPI']['DEBUG'],
                workers=APP_SETTINGS['BACKEND']['FASTAPI']['WORKERS'],
                reload_dirs=["recommendation_system/api"],
                log_level="info" if APP_SETTINGS['BACKEND']['PROD'] else "debug")


if __name__ == '__main__':
    start_app()
