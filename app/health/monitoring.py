import json

import cronitor
from app.exceptions import ModeDoesNotExist
from app.health.health_checks import service_health_test
from app.settings import APP_SETTINGS


class CronitorMonitoring:
    def __init__(self, is_prod, api_key):
        self.is_prod = is_prod
        self.identifier = self.monitoring_identifier_selector()
        cronitor.api_key = api_key

        self.heartbeat_monitor = cronitor.Monitor(f'{self.identifier}-heartbeat')
        self.init_scheduled_monitors()

    @staticmethod
    def monitoring_identifier_selector():
        if APP_SETTINGS['BACKEND']['MODE'] == 'PORTAL-RECOMMENDER':
            return "rs"
        elif APP_SETTINGS['BACKEND']['MODE'] == 'PROVIDERS-RECOMMENDER':
            return "autocompletion"
        else:
            return "NOT-MONITORED"

    def init_scheduled_monitors(self):
        if self.is_prod:
            cronitor.Monitor.put(
                key=f'update-{self.identifier}',
                type='job',
                schedule=f'0 */{APP_SETTINGS["BACKEND"]["SCHEDULING"]["EVERY_N_HOURS"]} * * *'
            )

    def send_heartbeat_message(self):
        if self.is_prod:
            self.heartbeat_monitor.ping(message=json.dumps(
                {
                    "version": APP_SETTINGS['BACKEND']['VERSION_NAME'],
                    "mode": APP_SETTINGS['BACKEND']['MODE'],
                    "health": service_health_test()
                }
            ))


cronitor_monitoring = CronitorMonitoring(
    is_prod=APP_SETTINGS['BACKEND']['PROD'],
    api_key=APP_SETTINGS['CREDENTIALS']['CRONITOR_API_KEY']
)
