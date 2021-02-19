import unittest
from bill_tracker_core import Bill


class MyTestCase(unittest.TestCase):
    """
    Tests for Bills
    """
    def test_to_dict(self):
        bill = Bill(
            "Example bill",
            "This description is a sample text. It can be as many lines as we want.",
            "1/1/2021",
            "1/2/2021",
            "active",
            short_desc="Sample Bill"
        )
        print(bill.to_dict())
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
