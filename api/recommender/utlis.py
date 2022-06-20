import pandas as pd
from functools import reduce


# TODO: remove dfs?? or add service_id as index
def get_services(db):
    # get all the services
    services_info = [db.get_services(attributes=["name", "description"])]

    # TODO use of METADATA?
    extra_infos = ["services_scientific_domains", "services_target_users", "services_categories"]

    for extra_info in extra_infos:
        services_info.append(getattr(db, "get_" + extra_info)())

    # TODO replace with empty list
    services_df = reduce(lambda left, right: pd.merge(left, right, on=['service_id'],
                                               how='outer'), services_info).fillna("")

    services_df["service_id"] = services_df["service_id"].apply(str)

    return services_df
