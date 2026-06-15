import unittest
from unittest import mock
from reports import channel_overview_report

class TestChannelOverviewReport(unittest.TestCase):

    def test_run_report_with_totals(self):
        """
        Test that the run_report function correctly calculates and appends totals
        for multiple metrics.
        """
        mock_data_client = mock.Mock()
        
        # Traffic response mock
        mock_traffic_response = mock.Mock()
        mock_row1 = mock.Mock()
        mock_row1.dimension_values = [mock.Mock(value="Channel A")]
        mock_row1.metric_values = [mock.Mock(value="100"), mock.Mock(value="50"), mock.Mock(value="0.5"), mock.Mock(value="80"), mock.Mock(value="70")]

        mock_row2 = mock.Mock()
        mock_row2.dimension_values = [mock.Mock(value="Channel B")]
        mock_row2.metric_values = [mock.Mock(value="200"), mock.Mock(value="150"), mock.Mock(value="0.75"), mock.Mock(value="180"), mock.Mock(value="170")]

        mock_traffic_response.rows = [mock_row1, mock_row2]

        # Lead response mock
        mock_lead_response = mock.Mock()
        mock_lrow1 = mock.Mock()
        mock_lrow1.dimension_values = [mock.Mock(value="Channel A")]
        mock_lrow1.metric_values = [mock.Mock(value="10")]
        mock_lead_response.rows = [mock_lrow1]

        mock_data_client.run_report.side_effect = [mock_traffic_response, mock_lead_response]

        property_id = "12345"
        start_date = "2023-01-01"
        end_date = "2023-01-07"

        report_data = channel_overview_report.run_report(property_id, mock_data_client, start_date, end_date)

        self.assertIsNotNone(report_data)
        self.assertEqual(report_data["title"], "Channel Overview Report")
        self.assertEqual(report_data["headers"], ["Channel", "Sessions", "Engaged Sessions", "Engagement Rate", "Active Users", "New Users", "Leads"])
        
        # Check rows (2 data rows + 1 total row)
        self.assertEqual(len(report_data["rows"]), 3)

        # Channel A
        self.assertEqual(report_data["rows"][0], ["Channel A", 100, 50, "50.00%", 80, 70, 10])
        # Channel B
        self.assertEqual(report_data["rows"][1], ["Channel B", 200, 150, "75.00%", 180, 170, 0])

        # Total
        total_row = report_data["rows"][2]
        self.assertEqual(total_row[0], "Total")
        self.assertEqual(total_row[1], 300) # 100+200
        self.assertEqual(total_row[2], 200) # 50+150
        self.assertEqual(total_row[3], "66.67%") # 200/300
        self.assertEqual(total_row[4], 260) # 80+180
        self.assertEqual(total_row[5], 240) # 70+170
        self.assertEqual(total_row[6], 10)

    def test_run_report_no_rows(self):
        """
        Test that the run_report function handles cases with no data rows gracefully.
        """
        mock_data_client = mock.Mock()
        mock_traffic_response = mock.Mock()
        mock_traffic_response.rows = []
        mock_lead_response = mock.Mock()
        mock_lead_response.rows = []
        mock_data_client.run_report.side_effect = [mock_traffic_response, mock_lead_response]

        property_id = "12345"
        start_date = "2023-01-01"
        end_date = "2023-01-07"

        report_data = channel_overview_report.run_report(property_id, mock_data_client, start_date, end_date)

        self.assertIsNotNone(report_data)
        self.assertEqual(report_data["title"], "Channel Overview Report")
        self.assertEqual(report_data["headers"], ["Channel", "Sessions", "Engaged Sessions", "Engagement Rate", "Active Users", "New Users", "Leads"])
        self.assertEqual(len(report_data["rows"]), 0) # No data rows, so no total row either

    def test_run_report_with_none_values(self):
        """
        Test that the run_report function handles cases where metric values might be zero.
        """
        mock_data_client = mock.Mock()
        mock_traffic_response = mock.Mock()
        
        mock_row1 = mock.Mock()
        mock_row1.dimension_values = [mock.Mock(value="Channel X")]
        mock_row1.metric_values = [mock.Mock(value="10"), mock.Mock(value="5"), mock.Mock(value="0.5"), mock.Mock(value="8"), mock.Mock(value="7")]

        mock_row2 = mock.Mock()
        mock_row2.dimension_values = [mock.Mock(value="Channel Y")]
        mock_row2.metric_values = [mock.Mock(value="0"), mock.Mock(value="0"), mock.Mock(value="0"), mock.Mock(value="0"), mock.Mock(value="0")] # Zero values

        mock_traffic_response.rows = [mock_row1, mock_row2]

        mock_lead_response = mock.Mock()
        mock_lead_response.rows = []
        mock_data_client.run_report.side_effect = [mock_traffic_response, mock_lead_response]

        property_id = "12345"
        start_date = "2023-01-01"
        end_date = "2023-01-07"

        report_data = channel_overview_report.run_report(property_id, mock_data_client, start_date, end_date)

        self.assertIsNotNone(report_data)
        self.assertEqual(len(report_data["rows"]), 3)

        total_row = report_data["rows"][2]
        self.assertEqual(total_row[0], "Total")
        self.assertEqual(total_row[1], 10)  # 10 + 0
        self.assertEqual(total_row[2], 5)   # 5 + 0

if __name__ == '__main__':
    unittest.main()
