import logging
from multiprocessing import Process

import cronitor
from app.health.monitoring import cronitor_monitoring
from app.recommenders.update.updater_selector import get_updater
from app.routes.update import update
from app.settings import APP_SETTINGS
from apscheduler.schedulers.blocking import BlockingScheduler


def init_scheduler():
    scheduler = BlockingScheduler()
    scheduler.add_job(
        scheduled_update, 'cron',
        hour=f'*/{APP_SETTINGS["BACKEND"]["SCHEDULING"]["EVERY_N_HOURS"]}',
    )

    scheduler.add_job(
        scheduled_heartbeat, 'cron',
        minute="*/5"
    )

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass


@cronitor.job('update-rs')
def scheduled_update():
    logging.info("Running scheduled update...")
    update()


def scheduled_heartbeat():
    logging.info("Sending heartbeat...")
    cronitor_monitoring.send_heartbeat_message()


def start_scheduler_process():
    updater = get_updater()
    updater.initialize()

    p = Process(target=init_scheduler)
    logging.info("Starting process...")
    p.start()
