import logging
from multiprocessing import Process

import cronitor
from api.recommender.project_completion.initialization import association_rules
from api.recommender.similar_services.preprocessor.embeddings.metadata_embeddings import initialize_metadata_embeddings
from api.recommender.similar_services.preprocessor.embeddings.text_embeddings import initialize_text_embeddings
from api.recommender.similar_services.preprocessor.reports.monitoring_reports import initialise_ar_report, \
    initialise_status_report
from api.recommender.similar_services.preprocessor.similarities.metadata_similarities import \
    initialize_metadata_similarities
from api.recommender.similar_services.preprocessor.similarities.text_similarities import initialize_text_similarities
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
    if APP_SETTINGS["BACKEND"]["MODE"] == "AUTO-COMPLETION":
        initialize_text_embeddings()
    elif APP_SETTINGS["BACKEND"]["MODE"] == "RS":
        # Create metadata structures if they do not exist
        initialize_metadata_embeddings()
        initialize_metadata_similarities()

        # Create report structures if they do not exist
        initialise_status_report()
        initialise_ar_report()

        # Create text structures if they do not exist
        initialize_text_embeddings()
        initialize_text_similarities()

        if not association_rules.existence_association_rules():
            logging.info("Association rules do not exist. Creating...")
            association_rules.create_association_rules()
    else:
        pass  # TODO raise exception


def start_updating_process():
    initialize_structures_if_not_exist()

    p = Process(target=init_scheduler)
    logging.info("Starting process...")
    p.start()
