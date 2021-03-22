import parlpy.mps.parties_fetcher as pf
import unittest

class TestParties(unittest.TestCase):
    def test_get_all_parties(self):
        parties_list = pf.get_all_parties()

        for p in parties_list:
            print(f"name {p.party_name}")
            print(f"id {p.party_id}")
            print(type(p.party_id))

            if p.party_name == "Labour":
                self.assertTrue(p.party_id == 15)