import unittest
from bill_tracker_core import User


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_init(self):
        self.user = User()

# Check for hashed passwords etc
# make sure it runs normally
# think about corner cases/edge cases
# this will run on the pipeline


if __name__ == '__main__':
    unittest.main()
