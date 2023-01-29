from datetime import datetime, timedelta
import pandas as pd
import requests

from api.databases.redis_db import store_object
from api.settings import APP_SETTINGS


class ArgoMonitoringApi:
    def __init__(self, n_days_ago=7):
        self.headers = {'Accept': 'application/json',
                        'x-api-key': APP_SETTINGS['CREDENTIALS']['MONITORING_API_ACCESS_TOKEN']}
        self.N_DAYS_AGO = n_days_ago

    def get_status_report(self, store_in_redis=True):
        """Get the latest status report from monitoring services

        Args:
            store_in_redis (bool): Default TRUE

        Returns:
            status_report_df (datframe): response from api
        """
        status_report = f"https://api.devel.argo.grnet.gr/api/v3/status/Default?" \
                        f"?latest=true"

        response = requests.get(status_report, headers=self.headers)

        status_report_df = pd.json_normalize(response.json()['groups'])

        for i, statuses in enumerate(status_report_df['statuses']):
            tmp_statuses = []
            for status in statuses:
                tmp_statuses.append(status['value'])
            status_report_df['statuses'][i] = tmp_statuses

        if store_in_redis is True:
            store_object(status_report_df, "STATUS_REPORT")

        return status_report_df

    def get_ar_report(self, store_in_redis=True):
        """Get availability and reliability reports from monitoring services

        Notes:
            if user needs specific AR report then
            request_info (dict): {
                'start_day': '01',
                'start_month': '10',
                'start_year': '2022',
                'end_day': '03',
                'end_month': '10',
                'end_year': '2022',
                'granularity': 'daily'
            }
        Args:
            store_in_redis (bool): Default TRUE

        Returns:
            ar_report_df (dataframe): response from api
        """
        current_day = datetime.now()
        n_days_ago = current_day - timedelta(days=self.N_DAYS_AGO)

        start_date = n_days_ago.strftime("%Y-%m-%d")
        end_date = current_day.strftime("%Y-%m-%d")

        ar_report = f"https://api.devel.argo.grnet.gr/api/v3/results/Default?" \
                    f"start_time={start_date}" \
                    f"T00%3A04%3A05Z" \
                    f"&end_time={end_date}" \
                    f"T15%3A04%3A05Z" \
                    f"&granularity=daily"

        response = requests.get(ar_report, headers=self.headers)

        results_json = response.json()['results']
        results_dict = {
            'name': [],
            'type': [],
            'date': [],
            'availability': [],
            'reliability': [],
            'unknown': [],
            'uptime': [],
            'downtime': []
        }
        for project in results_json:
            for servicegroup in project['groups']:
                results_dict['name'].append(servicegroup['name'])
                results_dict['type'].append(servicegroup['type'])
                total_statuses = {
                    'date': [],
                    'availability': [],
                    'reliability': [],
                    'unknown': [],
                    'uptime': [],
                    'downtime': []
                }
                for statuses in servicegroup['results']:
                    for status, value in statuses.items():
                        total_statuses[status].append(value)
                for key, value in total_statuses.items():
                    results_dict[key].append(value)

        ar_report_df = pd.DataFrame.from_dict(results_dict)
        if store_in_redis is True:
            store_object(ar_report_df, "AR_REPORT")

        return ar_report_df
