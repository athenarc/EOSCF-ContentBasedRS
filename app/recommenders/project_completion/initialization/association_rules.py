import logging

import pandas as pd
from app.databases.redis_db import (check_key_existence, delete_object,
                                    get_object, store_object)
from app.databases.registry.registry_selector import get_registry
from app.exceptions import NoneProjects
from app.settings import APP_SETTINGS
from mlxtend.frequent_patterns import association_rules, fpgrowth
from mlxtend.preprocessing import TransactionEncoder


def get_projects_services(db):
    # Get all project ids
    project_ids = db.get_projects()

    # Create a list with all the transactions(transaction => services in project)
    projects_services = []
    for project_id in project_ids:
        project_services = db.get_project_services(project_id)
        if len(project_services) > 1:
            projects_services.append(project_services)

    return projects_services


def create_association_rules():
    db = get_registry()
    projects_services = get_projects_services(db)

    if len(projects_services) == 0:
        raise NoneProjects

    # Encode the dataset
    te = TransactionEncoder()
    te_ary = te.fit(projects_services).transform(projects_services)
    projects_services_enc = pd.DataFrame(te_ary, columns=te.columns_)

    frequent_itemsets = fpgrowth(projects_services_enc,
                                 min_support=APP_SETTINGS['BACKEND']['PROJECT_COMPLETION']['MIN_SUPPORT'],
                                 use_colnames=True)

    rules = association_rules(frequent_itemsets, metric="confidence",
                              min_threshold=APP_SETTINGS['BACKEND']['PROJECT_COMPLETION']['MIN_CONFIDENCE'])

    # Convert frozensets to list
    rules["antecedents"] = rules["antecedents"].apply(list)
    rules["consequents"] = rules["consequents"].apply(list)

    # Store produced rules
    store_object(rules, "ASSOCIATION_RULES")


def get_association_rules():
    return get_object("ASSOCIATION_RULES")


def delete_association_rules():
    delete_object("ASSOCIATION_RULES")


def existence_association_rules():
    return check_key_existence("ASSOCIATION_RULES")


def initialize_association_rules():
    if not existence_association_rules():
        logging.debug("Association rules do not exist. Creating...")
        create_association_rules()
