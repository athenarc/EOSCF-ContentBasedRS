from datetime import datetime, timedelta
import pandas as pd
import requests

from app.databases.registry.registry_selector import get_registry
from app.settings import APP_SETTINGS


class ArgoMonitoringApi:
    def __init__(self, n_days_ago=7):
        self.headers = {'Accept': 'application/json',
                        'x-api-key': APP_SETTINGS['CREDENTIALS']['MONITORING_API_ACCESS_TOKEN']}
        self.N_DAYS_AGO = n_days_ago
        self.unhealthy_statuses = ['CRITICAL', 'DOWNTIME']

    def get_status_report(self):
        """Get the latest status report from monitoring services

        Returns:
            status_report_df (datframe): response from api
        """
        status_report = f"https://api.devel.argo.grnet.gr/api/v3/status/Default?" \
                        f"?latest=true"

        response = requests.get(status_report, headers=self.headers)
        if response.status_code != 200:
            return None
        status_report_df = pd.json_normalize(response.json()['groups'])

        for i, statuses in enumerate(status_report_df['statuses']):
            status_report_df['statuses'][i] = statuses[-1]['value']

        for i, service in enumerate(status_report_df['endpoints']):
            catalog_id = service[0]['info']['ID']
            status_report_df['name'][i] = catalog_id

        status_report_df.rename(columns={"name": "catalog_id", "statuses": "status"}, inplace=True)
        status_report_df = status_report_df.drop(columns=['type', 'endpoints'])

        registry = get_registry()
        catalog_id_mappings = registry.get_catalog_id_mappings()
        for i, service in enumerate(status_report_df['catalog_id']):
            if service in catalog_id_mappings['catalog_id'].unique():
                status_report_df['catalog_id'][i] = \
                    catalog_id_mappings.loc[catalog_id_mappings['catalog_id'] == service, 'id'].iloc[0]
            else:
                status_report_df['catalog_id'][i] = pd.NA
        status_report_df.dropna(inplace=True)
        unhealthy_services = status_report_df.loc[status_report_df['status'].isin(self.unhealthy_statuses)]

        return list(unhealthy_services['catalog_id'])

    def get_ar_report(self):
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
        if response.status_code != 200:
            return None

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

        return ar_report_df
