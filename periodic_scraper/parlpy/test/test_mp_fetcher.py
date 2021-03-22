import json
import pandas as pd

from parlpy.mps.mp_fetcher import MPOverview

import unittest


def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=2)
    print(text)


class TestMP(unittest.TestCase):
    def test_get_active_mps(self):
        current_mp_fetcher = MPOverview()
        current_mp_fetcher.get_active_MPs()

        pd.set_option('display.max_columns', 20)
        print(current_mp_fetcher.mp_overview_data)

        # since 1950 number of active MPs varies between 640-659
        reasonable_lower_bound = 600
        reasonable_upper_bound = 700
        number_of_active_mps = len(current_mp_fetcher.mp_overview_data.index)
        self.assertTrue(reasonable_lower_bound < number_of_active_mps < reasonable_upper_bound)

    def test_get_all_members(self):
        all_living_mps_fetcher = MPOverview()
        all_living_mps_fetcher.get_all_members(params={"House": "Commons"})

        pd.set_option('display.max_columns', 20)
        print(all_living_mps_fetcher.mp_overview_data)

if __name__ == "__main__":
    unittest.main()