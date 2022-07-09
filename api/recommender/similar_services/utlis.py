import pandas as pd
from functools import reduce


def get_services(db):
    # get all the services
    services_info = [db.get_services(attributes=["name", "description", "scientific_domains", "target_users", "categories"])]

    # TODO replace with empty list
    services_df = reduce(lambda left, right: pd.merge(left, right, on=['service_id'],
                                               how='outer'), services_info).fillna("")

    services_df["service_id"] = services_df["service_id"].apply(str)

    return services_df
