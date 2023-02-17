import logging
from multiprocessing import Process

import cronitor
from app.recommender.update.updater_selector import get_updater
from app.routes.update import update
from app.settings import APP_SETTINGS
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


def start_scheduler_process():
    updater = get_updater()
    updater.initialize()

    p = Process(target=init_scheduler)
    logging.info("Starting process...")
    p.start()
