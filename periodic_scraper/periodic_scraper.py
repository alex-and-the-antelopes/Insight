# WARNING - importing parlpy after mysql.connector results in error with urllib, relating to SSL certs
# todo: fix this

from parlpy.bills.bill_list_fetcher import BillsOverview

import mysql.connector
from mysql.connector.constants import ClientFlag


sql_config = {
    "user": "root",
    "password": "",
    "host": "35.223.77.43",
    'client_flags': [ClientFlag.SSL],
    "ssl_ca": "/home/r/PycharmProjects/BillTracker/periodic_scraper/certs/server-ca.pem",
    "ssl_cert": "/home/r/PycharmProjects/BillTracker/periodic_scraper/certs/client-cert.pem",
    "ssl_key": "/home/r/PycharmProjects/BillTracker/periodic_scraper/certs/client-key.pem"
}


cnxn = mysql.connector.connect(**sql_config)
cnxn.close()

bills_this_session = BillsOverview()
bills_this_session.update_all_bills_in_session()

print(bills_this_session.bills_overview_data)
