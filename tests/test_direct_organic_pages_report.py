import unittest
from unittest import mock
from reports import direct_organic_pages_report

class TestDirectOrganicPagesReport(unittest.TestCase):

    def test_run_report_two_separate_requests(self):
        """
        Test that the run_report function correctly handles two separate requests
        for 'before' and 'after' periods and joins them correctly.
        """
        mock_data_client = mock.Mock()
        
        # Mock response for 'After' period
        mock_response_after = mock.Mock()
        mock_row_after1 = mock.Mock()
        mock_row_after1.dimension_values = [mock.Mock(value="/home")]
        mock_row_after1.metric_values = [mock.Mock(value="150"), mock.Mock(value="120"), mock.Mock(value="0.6")]
        
        mock_row_after2 = mock.Mock()
        mock_row_after2.dimension_values = [mock.Mock(value="/pricing")]
        mock_row_after2.metric_values = [mock.Mock(value="40"), mock.Mock(value="30"), mock.Mock(value="0.3")]
        
        mock_response_after.rows = [mock_row_after1, mock_row_after2]
        
        # Mock response for 'Before' period
        mock_response_before = mock.Mock()
        mock_row_before1 = mock.Mock()
        mock_row_before1.dimension_values = [mock.Mock(value="/home")]
        mock_row_before1.metric_values = [mock.Mock(value="100"), mock.Mock(value="80"), mock.Mock(value="0.5")]
        
        mock_row_before2 = mock.Mock()
        mock_row_before2.dimension_values = [mock.Mock(value="/pricing")]
        mock_row_before2.metric_values = [mock.Mock(value="50"), mock.Mock(value="40"), mock.Mock(value="0.4")]
        
        mock_response_before.rows = [mock_row_before1, mock_row_before2]
        
        # Set side_effect to return after then before
        mock_data_client.run_report.side_effect = [mock_response_after, mock_response_before]

        property_id = "12345"
        start_date = "2023-01-08"
        end_date = "2023-01-14"

        report_data = direct_organic_pages_report.run_report(property_id, mock_data_client, start_date, end_date)

        self.assertIsNotNone(report_data)
        self.assertEqual(len(report_data["rows"]), 2)

        # /home row (sorted by sessions after)
        home_row = report_data["rows"][0]
        self.assertEqual(home_row[0], "/home")
        self.assertEqual(home_row[1], "100") # Sessions Before
        self.assertEqual(home_row[2], "150") # Sessions After
        self.assertEqual(home_row[3], "+50 (+50.0%)") # Growth Sessions
        self.assertEqual(home_row[4], "80")  # Users Before
        self.assertEqual(home_row[5], "120") # Users After
        self.assertEqual(home_row[6], "+40 (+50.0%)") # Growth Users
        self.assertEqual(home_row[7], "60.00%") # Eng. Rate (After)

        # /pricing row
        pricing_row = report_data["rows"][1]
        self.assertEqual(pricing_row[0], "/pricing")
        self.assertEqual(pricing_row[1], "50") # Sessions Before
        self.assertEqual(pricing_row[2], "40") # Sessions After
        self.assertEqual(pricing_row[3], "-10 (-20.0%)") # Growth Sessions
        self.assertEqual(pricing_row[4], "40")  # Users Before
        self.assertEqual(pricing_row[5], "30")  # Users After
        self.assertEqual(pricing_row[6], "-10 (-25.0%)") # Growth Users
        self.assertEqual(pricing_row[7], "30.00%") # Eng. Rate (After)


if __name__ == '__main__':
    unittest.main()
