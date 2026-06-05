import unittest
from unittest import mock
from reports import direct_organic_pages_report

class TestDirectOrganicPagesReport(unittest.TestCase):

    def test_run_report_active_new_users_logic(self):
        """
        Test that the run_report function correctly handles Active Users and New Users
        and performs the intersection logic correctly.
        """
        mock_data_client = mock.Mock()
        
        # Mock response for 'After' period (Top 250)
        # Metrics: activeUsers, newUsers, engagementRate
        mock_response_after = mock.Mock()
        mock_row_after1 = mock.Mock()
        mock_row_after1.dimension_values = [mock.Mock(value="/home")]
        mock_row_after1.metric_values = [mock.Mock(value="150"), mock.Mock(value="120"), mock.Mock(value="0.6")]
        
        mock_row_after2 = mock.Mock()
        mock_row_after2.dimension_values = [mock.Mock(value="/new-page")]
        mock_row_after2.metric_values = [mock.Mock(value="40"), mock.Mock(value="30"), mock.Mock(value="0.3")]
        
        mock_response_after.rows = [mock_row_after1, mock_row_after2]
        
        # Mock response for 'Before' period (Top 500)
        mock_response_before = mock.Mock()
        mock_row_before1 = mock.Mock()
        mock_row_before1.dimension_values = [mock.Mock(value="/home")]
        mock_row_before1.metric_values = [mock.Mock(value="100"), mock.Mock(value="80"), mock.Mock(value="0.5")]
        
        # /old-page is in 'Before' but not in 'After', so it should be EXCLUDED
        mock_row_before2 = mock.Mock()
        mock_row_before2.dimension_values = [mock.Mock(value="/old-page")]
        mock_row_before2.metric_values = [mock.Mock(value="50"), mock.Mock(value="40"), mock.Mock(value="0.4")]
        
        mock_response_before.rows = [mock_row_before1, mock_row_before2]
        
        # Set side_effect to return after then before
        mock_data_client.run_report.side_effect = [mock_response_after, mock_response_before]

        property_id = "12345"
        start_date = "2023-01-08"
        end_date = "2023-01-14"

        report_data = direct_organic_pages_report.run_report(property_id, mock_data_client, start_date, end_date)

        self.assertIsNotNone(report_data)
        # Only 2 rows because only 'after' pages are included
        self.assertEqual(len(report_data["rows"]), 2)

        # /home row
        home_row = report_data["rows"][0]
        self.assertEqual(home_row[0], "/home")
        self.assertEqual(home_row[1], "100") # Active Before
        self.assertEqual(home_row[2], "150") # Active After
        self.assertEqual(home_row[3], "+50 (+50.0%)") # Growth Active
        self.assertEqual(home_row[4], "80")  # New Before
        self.assertEqual(home_row[5], "120") # New After
        self.assertEqual(home_row[6], "+40 (+50.0%)") # Growth New
        self.assertEqual(home_row[7], "60.00%") # Eng. Rate (After)

        # /new-page row (Was not in top 500 of 'Before')
        new_row = report_data["rows"][1]
        self.assertEqual(new_row[0], "/new-page")
        self.assertEqual(new_row[1], "0") # Active Before
        self.assertEqual(new_row[2], "40") # Active After
        self.assertEqual(new_row[3], "+40 (New)") # Growth Active
        self.assertEqual(new_row[4], "0")  # New Before
        self.assertEqual(new_row[5], "30")  # New After
        self.assertEqual(new_row[6], "+30 (New)") # Growth New
        self.assertEqual(new_row[7], "30.00%") # Eng. Rate (After)


    def test_run_report_smart_month_logic(self):
        """
        Test that the run_report function uses the full previous month when a full 
        month is provided as the 'After' period.
        """
        mock_data_client = mock.Mock()
        mock_response = mock.Mock()
        mock_response.rows = []
        mock_data_client.run_report.return_value = mock_response

        # May 2026 (31 days)
        start_date = "2026-05-01"
        end_date = "2026-05-31"

        report_data = direct_organic_pages_report.run_report("123", mock_data_client, start_date, end_date)

        # Check the explanation text for the correctly calculated 'Before' period
        # April 2026 (30 days)
        self.assertIn("**Before Period**: 2026-04-01 to 2026-04-30", report_data["explanation"])

    def test_run_report_standard_duration_fallback(self):
        """
        Test that the run_report function falls back to standard day-count matching
        when the 'After' period is not a full calendar month.
        """
        mock_data_client = mock.Mock()
        mock_response = mock.Mock()
        mock_response.rows = []
        mock_data_client.run_report.return_value = mock_response

        # Partial month: 7 days
        start_date = "2026-05-10"
        end_date = "2026-05-16"

        report_data = direct_organic_pages_report.run_report("123", mock_data_client, start_date, end_date)

        # Before period should also be 7 days: 2026-05-03 to 2026-05-09
        self.assertIn("**Before Period**: 2026-05-03 to 2026-05-09", report_data["explanation"])
