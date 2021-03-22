import periodic_scraper as ps
ps.insert_and_update_data()
import google.cloud.logging
import logging

def test_logging_func():
    logging_client = google.cloud.logging.Client()

    logging_client.get_default_handler()
    logging_client.setup_logging(log_level=logging.INFO)

    test_msg = "TEST MESSAGE"
    logging.warning(test_msg)


def main(data, context):
    ps.insert_and_update_data()

