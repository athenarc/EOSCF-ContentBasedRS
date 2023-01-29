import logging
from api.databases.redis_db import (check_key_existence, delete_object, get_object)
from api.exceptions import MissingStructure
from api.databases.argo_monitoring_api import ArgoMonitoringApi


def create_status_report():
    mon = ArgoMonitoringApi()
    status_report = mon.get_status_report()
    return status_report


def create_ar_report():
    mon = ArgoMonitoringApi()
    ar_report = mon.get_ar_report()
    return ar_report


def update_status_report():
    if existence_status_report():
        delete_status_report()
    create_status_report()


def update_ar_report():
    if existence_ar_report():
        delete_ar_report()
    create_ar_report()


def existence_status_report():
    return check_key_existence("STATUS_REPORT")


def existence_ar_report():
    return check_key_existence("AR_REPORT")


def get_ar_report():
    if not existence_ar_report():
        raise MissingStructure("AR report does not exist!")
    return get_object("AR_REPORT")


def get_status_report():
    if not existence_status_report():
        raise MissingStructure("Status report does not exist!")
    return get_object("STATUS_REPORT")


def delete_ar_report():
    delete_object("AR_REPORT")


def delete_status_report():
    delete_object("STATUS_REPORT")


def initialise_status_report():
    if not existence_status_report():
        logging.info("Status report does not exist. Creating...")
        create_status_report()


def initialise_ar_report():
    if not existence_ar_report():
        logging.info("Status report does not exist. Creating...")
        create_ar_report()
