import unittest
from insight.parliament import Bill


class MyTestCase(unittest.TestCase):
    """
    Tests for Bill. Covered functions:
    > prepare()
    """
    def test_prepare(self):
        """
        Test the prepare() function in Bill.
        """
        bill = Bill(59, "Example Bill Title", "An example of description.", "4/1/2021", "20/12/2021", "Amendments",
                    "Short description", "https://bills.parliament.uk/bills/2849")  # Example Bill object
        bill_dict = bill.to_dict()
        extra = {"likes": "5", "dislikes": "10"}
        correct_result = bill_dict.copy()
        correct_result["likes"], correct_result["dislikes"] = "5", "10"
        self.assertEqual(bill.prepare(extra), correct_result)  # Correct result
        # Correct type, wrong values
        temp_result = bill_dict.copy()
        temp_result["likes"], temp_result["dislikes"] = "5", "5"  # Wrong dislikes
        self.assertNotEqual(bill.prepare(extra), temp_result)
        temp_result = bill_dict.copy()
        temp_result["likes"], temp_result["dislikes"] = "15", "10"  # Wrong likes
        self.assertNotEqual(bill.prepare(extra), temp_result)
        temp_result = bill_dict.copy()
        temp_result["likes"], temp_result["dislikes"] = "15", "5"  # Wrong likes and dislikes
        self.assertNotEqual(bill.prepare(extra), temp_result)
