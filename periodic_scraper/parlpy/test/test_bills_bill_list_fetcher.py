import datetime
import time

import pandas as pd
import numpy as np

from parlpy.bills.bill_list_fetcher import BillsOverview

import unittest


class TestOverview(unittest.TestCase):
    # create BillsOverview object ready for tests
    # also print result
    def setUp(self):
        self.test_fetcher = BillsOverview(debug=False)

        pd.set_option("display.max_columns", len(self.test_fetcher.bills_overview_data.columns))

        #print(self.test_fetcher.bills_overview_data)

    def atest_print_short(self):
        print(f"\n\nPrinting dataframe from bill_list_fetcher for 2004-2005 session {' ' * 5 + '=' * 200}")
        self.test_fetcher.update_all_bills_in_session(session_name="2004-05")

        print(self.test_fetcher.bills_overview_data)

        print("first session of first bill")
        print(self.test_fetcher.bills_overview_data["session"][0][0])

    # check that the second call to get_changed_bills_in_session puts more or equal items into bill_overview_data
    # than the first

    def atest_update_only_needed(self):
        self.test_fetcher.reset_datetime_last_scraped()

        self.test_fetcher.get_changed_bills_in_session()
        print("dataframe:")
        print(self.test_fetcher.bills_overview_data)
        print("---------------------------------------------------")
        df_row_count_1 = len(self.test_fetcher.bills_overview_data.index)

        self.test_fetcher.get_changed_bills_in_session()
        print("dataframe:")
        print(self.test_fetcher.bills_overview_data)
        print("---------------------------------------------------")
        df_row_count_2 = len(self.test_fetcher.bills_overview_data.index)

        self.assertTrue(df_row_count_1 >= df_row_count_2)

    # test types of dataframe
    def atest_dataframe_types(self):
        self.test_fetcher.update_all_bills_in_session()
        print(self.test_fetcher.bills_overview_data)
        print("---------------------------------------------------")

        self.assertIsInstance(self.test_fetcher.bills_overview_data, pd.DataFrame)

        print(self.test_fetcher.bills_overview_data.dtypes)

        # strings are stored as objects in dataframes
        self.assertTrue(self.test_fetcher.bills_overview_data.bill_title_stripped.dtype == object)
        self.assertTrue(self.test_fetcher.bills_overview_data.bill_detail_path.dtype == object)

        # check that last_updated is stored as datetime64[ns]
        self.assertTrue(self.test_fetcher.bills_overview_data.last_updated.dtype == np.dtype('datetime64[ns]'))

    def test_mock_datetime_last_scraped_prevents_all(self):
        self.test_fetcher.reset_datetime_last_scraped()

        mock_datetime_now = datetime.datetime.now()
        self.test_fetcher.mock_datetime_last_scraped(mock_datetime_now)

        self.test_fetcher.get_changed_bills_in_session(session_name="All")

        df_row_count = len(self.test_fetcher.bills_overview_data.index)
        self.assertTrue(df_row_count == 0)

    def test_mock_datetime_last_scraped_prevents_some(self):
        self.test_fetcher.reset_datetime_last_scraped()

        mock_datetime_year_ago = datetime.datetime.now() - datetime.timedelta(365)
        self.test_fetcher.mock_datetime_last_scraped(mock_datetime_year_ago)

        self.test_fetcher.get_changed_bills_in_session(session_name="All")

        df_row_count = len(self.test_fetcher.bills_overview_data.index)
        self.assertTrue(df_row_count != 0)


if __name__ == '__main__':
    unittest.main()