import periodic_scraper as ps


def main(data, context):
    reasonable_mp_update_frequency = 5
    ps.insert_and_update_data(day_frequency_for_party_and_mp_data=reasonable_mp_update_frequency)

