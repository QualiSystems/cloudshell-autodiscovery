import unittest

import mock

from autodiscovery.models import VendorDefinitionCollection


class TestVendorDefinitionCollection(unittest.TestCase):
    def setUp(self):
        self.expected_vendor = mock.MagicMock(check_vendor_name=mock.MagicMock(return_value=True))
        self.vendors = [mock.MagicMock(check_vendor_name=mock.MagicMock(return_value=False)),
                        mock.MagicMock(check_vendor_name=mock.MagicMock(return_value=False)),
                        self.expected_vendor,
                        mock.MagicMock(check_vendor_name=mock.MagicMock(return_value=False))]
        self.vendors_collection = VendorDefinitionCollection(vendors=self.vendors)

    def test_get_vendor(self):
        vendor_name = "test_vendor_name"
        # act
        result = self.vendors_collection.get_vendor(vendor_name=vendor_name)
        # verify
        self.assertEqual(result, self.expected_vendor)
