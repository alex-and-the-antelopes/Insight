"""
Alex Dawkins (alexander.dawkins@gmail.com) 2021
Robert Chambers 2021
"""
import unittest

from parlpy.bills.bill_list_fetcher import BillsOverview
from parlpy.bills import summary_fetcher
import pandas as pd

class TestSummary(unittest.TestCase):
    def test_get_summary_of_single_bill_2005_06_session(self):
        overview = BillsOverview()
        overview.update_all_bills_in_session(session_name="2005-06")

        single_path = overview.bills_overview_data.iloc[0]['bill_detail_path']
        single_summary = summary_fetcher.get_summary(single_path)

        print(f"\n\nTest get_summary {' ' * 5 + '=' * 200}")
        print(single_summary)

        print(f"\n\nTest append_summary {' ' * 2 + '=' * 200}")
        print(summary_fetcher.append_summary(overview.bills_overview_data.iloc[0]))

        print("Test summary is string type")
        self.assertTrue(type(single_summary) == str)

if __name__ == "__main__":
    unittest.main()
