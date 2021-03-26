import unittest
from insight.parliament import Bill


class MyTestCase(unittest.TestCase):
    """
    Tests for User. Covered functions:
    > to_dict todo fix to_dict tests and add comments
    """
    def test_to_dict(self):
        """
        Test the to_dict() in Bill
        """
        bill = Bill(
            "Example bill",
            "This description is a sample text. It can be as many lines as we want.",
            "1/1/2021",
            "1/2/2021",
            "active",
            short_desc="Sample Bill",
            photo="no_photo.jpg",
            link="https://www.youtube.com/watch?v=hXIArhNhD0g"
        )
        bill_dict = bill.to_dict()
        # Check for the actual value:
        result_dict = {
            'link': 'https://www.youtube.com/watch?v=hXIArhNhD0g',
            'status': 'active',
            'expiration': '1/2/2021',
            'date_added': '1/1/2021',
            'desc': 'This description is a sample text. It can be as many lines as we want.',
            'title': 'Example bill',
            'short_desc': 'Sample Bill',
            'img_url': '/res/no_photo.jpg'
        }
        self.assertEqual(result_dict, bill_dict)
        # Check for wrong values:
        false_dict = result_dict.copy()
        false_dict['link'] = 'https://www.youtube.com/watch?v=hXIArhNhD1G'
        self.assertNotEqual(false_dict, bill_dict)  # Wrong link
        false_dict = result_dict.copy()
        false_dict['status'] = 'invalid status'
        self.assertNotEqual(false_dict, bill_dict)  # Wrong status
        false_dict = result_dict.copy()
        false_dict['expiration'] = '1/1/2021'
        self.assertNotEqual(false_dict, bill_dict)  # Wrong expiration
        false_dict = result_dict.copy()
        false_dict['date_added'] = '1/2/2021'
        self.assertNotEqual(false_dict, bill_dict)  # Wrong date_added
        false_dict = result_dict.copy()
        false_dict['desc'] = 'THis description is a sample text. It can be as many lines as we want.'
        self.assertNotEqual(false_dict, bill_dict)  # Wrong desc
        false_dict = result_dict.copy()
        false_dict['title'] = 'Wrong title'
        self.assertNotEqual(false_dict, bill_dict)  # Wrong title
        false_dict = result_dict.copy()
        false_dict['short_desc'] = 'Sample BiLL'
        self.assertNotEqual(false_dict, bill_dict)  # Wrong short_desc
        false_dict = result_dict.copy()
        false_dict['img_url'] = '/res/no_photo.mp4'
        self.assertNotEqual(false_dict, bill_dict)  # Wrong img_url
        # Check Wrong Types:
        # Partially wrong types:
        false_dict = result_dict.copy()
        false_dict['link'] = None
        self.assertNotEqual(false_dict, bill_dict)  # None link
        false_dict = result_dict.copy()
        false_dict['status'] = None
        self.assertNotEqual(false_dict, bill_dict)  # None status
        false_dict = result_dict.copy()
        false_dict['expiration'] = None
        self.assertNotEqual(false_dict, bill_dict)  # None expiration
        false_dict = result_dict.copy()
        false_dict['date_added'] = None
        self.assertNotEqual(false_dict, bill_dict)  # None date_added
        false_dict = result_dict.copy()
        false_dict['desc'] = None
        self.assertNotEqual(false_dict, bill_dict)  # None desc
        false_dict = result_dict.copy()
        false_dict['title'] = None
        self.assertNotEqual(false_dict, bill_dict)  # None title
        false_dict = result_dict.copy()
        false_dict['short_desc'] = None
        self.assertNotEqual(false_dict, bill_dict)  # None short_desc
        false_dict = result_dict.copy()
        false_dict['img_url'] = None
        self.assertNotEqual(false_dict, bill_dict)  # None img_url
        false_dict = result_dict.copy()
        false_dict['link'] = None
        false_dict['status'] = None
        false_dict['expiration'] = None
        false_dict['date_added'] = None
        false_dict['desc'] = None
        false_dict['title'] = None
        false_dict['short_desc'] = None
        false_dict['img_url'] = None
        self.assertNotEqual(false_dict, bill_dict)  # All None
        # Fully wrong types:
        self.assertNotEqual("bill", bill_dict)
        self.assertNotEqual(None, bill_dict)
        self.assertNotEqual(13.012, bill_dict)


if __name__ == '__main__':
    unittest.main()
