import unittest
import datetime

import parlpy.bills.bill_votes_fetcher as bvf



class TestVotes(unittest.TestCase):
    def test_votes_for_single_bill(self):
        mock_start_time = datetime.date(2019,12,9)
        mock_end_time = None

        bill_divisions_list = bvf.get_divisions_information('financial services', mock_start_time, mock_end_time)

        for d in bill_divisions_list:
            print(f"div name {d.division_name}")
            print(f"stage {d.division_stage}")
            print(f"ayes {d.ayes}")
            print(f"noes {d.noes}")