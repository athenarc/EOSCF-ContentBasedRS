import logging

import sentry_sdk
import uvicorn
from app.databases.content_based_rec_db import ContentBasedRecsMongoDB
from app.scheduler import start_scheduler_process
from app.settings import APP_SETTINGS, settings_validation

logging.basicConfig(level=logging.INFO if APP_SETTINGS['BACKEND']['PROD'] else logging.DEBUG,
                    format='%(levelname)s | %(asctime)s | %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S')

from app.routes.add_routes import initialize_routes
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
    if APP_SETTINGS["BACKEND"]["MODE"] == "PORTAL-RECOMMENDER":
        db = ContentBasedRecsMongoDB()
        db.update_version()


def start_app():
    settings_validation()

    # The update scheduler starts before uvicorn creates many workers
    # The following call will also create necessary structures if they do not exist in redis
    start_scheduler_process()

    uvicorn.run("app.main:app",
                host=APP_SETTINGS['BACKEND']['FASTAPI']['HOST'],
                port=APP_SETTINGS['BACKEND']['FASTAPI']['PORT'],
                reload=APP_SETTINGS['BACKEND']['FASTAPI']['RELOAD'],
                debug=APP_SETTINGS['BACKEND']['FASTAPI']['DEBUG'],
                workers=APP_SETTINGS['BACKEND']['FASTAPI']['WORKERS'],
                reload_dirs=["recommendation_system/app"],
                log_level="info" if APP_SETTINGS['BACKEND']['PROD'] else "debug")


if __name__ == '__main__':
    start_app()
