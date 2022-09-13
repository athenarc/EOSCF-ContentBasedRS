import logging
from multiprocessing import Process

import cronitor
from api.recommender.project_completion.initialization import association_rules
from api.recommender.similar_services.similarities import (
    metadata_similarities, text_similarities)
from api.routes.update import update
from api.settings import APP_SETTINGS
from apscheduler.schedulers.blocking import BlockingScheduler

cronitor.api_key = APP_SETTINGS['CREDENTIALS']['CRONITOR_API_KEY']
cronitor.Monitor.put(
    key='update-rs',
    type='job',
    schedule=f'0 */{APP_SETTINGS["BACKEND"]["SCHEDULING"]["EVERY_N_HOURS"]} * * *'
)


def init_scheduler():
    scheduler = BlockingScheduler()
    scheduler.add_job(
        scheduled_update, 'cron',
        hour=f'*/{APP_SETTINGS["BACKEND"]["SCHEDULING"]["EVERY_N_HOURS"]}'
        # minute="*/5"
    )
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass


@cronitor.job('update-rs')
def scheduled_update():
    logging.info("Running scheduled update...")
    update()


def initialize_structures_if_not_exist():
    if not metadata_similarities.existence_metadata_similarities():
        logging.info("Metadata structure does not exist. Creating...")
        metadata_similarities.create_metadata_similarities()

    if not text_similarities.existence_text_similarities():
        logging.info("Text structure does not exist. Creating...")
        text_similarities.create_text_similarities()

    if not association_rules.existence_association_rules():
        logging.info("Association rules do not exist. Creating...")
        association_rules.create_association_rules()


def start_updating_process():
    initialize_structures_if_not_exist()

    p = Process(target=init_scheduler)
    logging.info("Starting process...")
    p.start()
