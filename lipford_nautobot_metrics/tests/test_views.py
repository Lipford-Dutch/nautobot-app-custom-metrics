"""View and API tests for Lipford Nautobot Metrics."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from nautobot.users.models import Token

from lipford_nautobot_metrics.catalog import METRIC_CATALOG
from lipford_nautobot_metrics.models import MetricValue
from lipford_nautobot_metrics.services import seed_sample_metrics


class MetricsDashboardViewTestCase(TestCase):
    """Tests for the metrics dashboard UI."""

    def setUp(self):
        """Create a superuser and sample metric data."""
        self.user = get_user_model().objects.create_superuser(username="admin", password="test")
        seed_sample_metrics(sample_days=3)

    def test_dashboard_requires_authentication(self):
        """Anonymous users cannot access the dashboard."""
        response = self.client.get(reverse("plugins:lipford_nautobot_metrics:dashboard"))

        self.assertEqual(response.status_code, 403)

    def test_dashboard_renders_metric_summary(self):
        """Authenticated users with permissions can see summary values."""
        self.client.force_login(self.user)

        response = self.client.get(reverse("plugins:lipford_nautobot_metrics:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Metrics Dashboard")
        self.assertContains(response, "Time Saved per Automated Task")
        self.assertContains(response, "Reduction in Manual Error Rates")
        self.assertContains(response, "Increased Task Throughput")
        self.assertContains(response, "Automation Adoption Rate")
        self.assertContains(response, "Golden Config Overall Compliance Status")
        self.assertContains(response, "SSoT Data Synchronization Job Frequency")
        self.assertContains(response, "DLM Time to Provision New Device")
        self.assertContains(response, "Job Results")

    def test_dashboard_blocks_user_without_metric_permissions(self):
        """Authenticated users without metric permissions cannot view the dashboard."""
        user = get_user_model().objects.create_user(username="viewer", password="test")
        self.client.force_login(user)

        response = self.client.get(reverse("plugins:lipford_nautobot_metrics:dashboard"))

        self.assertEqual(response.status_code, 403)


class MetricSummaryAPITestCase(TestCase):
    """Tests for the metric summary API endpoint."""

    def setUp(self):
        """Create a superuser and sample metric data."""
        self.user = get_user_model().objects.create_superuser(username="admin", password="test")
        seed_sample_metrics(sample_days=2)

    def test_summary_api_requires_authentication(self):
        """Anonymous API requests are rejected."""
        response = self.client.get(reverse("plugins-api:lipford_nautobot_metrics-api:metric-summary"))

        self.assertEqual(response.status_code, 403)

    def test_summary_api_blocks_user_without_metric_permissions(self):
        """Authenticated API users without metric permissions are rejected."""
        user = get_user_model().objects.create_user(username="api-viewer", password="test")
        self.client.force_login(user)

        response = self.client.get(reverse("plugins-api:lipford_nautobot_metrics-api:metric-summary"))

        self.assertEqual(response.status_code, 403)

    def test_summary_api_returns_current_metric_rollup(self):
        """The summary API returns one rollup per enabled metric definition."""
        self.client.force_login(self.user)

        response = self.client.get(reverse("plugins-api:lipford_nautobot_metrics-api:metric-summary"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], len(METRIC_CATALOG))
        self.assertEqual(
            {item["key"] for item in response.json()["results"]},
            {definition["key"] for definition in METRIC_CATALOG},
        )

    def test_metric_value_api_rejects_invalid_percent_value(self):
        """The metric value API rejects invalid percent observations."""
        self.client.force_login(self.user)
        definition_id = response_definition_id("automation_adoption_rate")
        response = self.client.post(
            reverse("plugins-api:lipford_nautobot_metrics-api:metricvalue-list"),
            data={
                "metric_definition": definition_id,
                "value": "125.0000",
                "recorded_at": "2026-06-05T12:00:00Z",
                "source": "api-test",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_summary_api_accepts_token_authentication(self):
        """The summary API supports token-authenticated service callers."""
        token = Token.objects.create(user=self.user, key="a" * 40)

        response = self.client.get(
            reverse("plugins-api:lipford_nautobot_metrics-api:metric-summary"),
            HTTP_AUTHORIZATION=f"Token {token.key}",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], len(METRIC_CATALOG))

    def test_bulk_ingest_is_atomic_and_idempotent(self):
        """Bulk ingestion validates and updates a stable observation identity."""
        self.client.force_login(self.user)
        url = reverse("plugins-api:lipford_nautobot_metrics-api:metric-ingest")
        payload = {
            "values": [
                {
                    "metric_key": "automation_adoption_rate",
                    "value": "75.0000",
                    "recorded_at": "2026-06-15T12:00:00Z",
                    "source": "integration-test",
                }
            ]
        }

        first = self.client.post(url, data=payload, content_type="application/json")
        payload["values"][0]["value"] = "80.0000"
        second = self.client.post(url, data=payload, content_type="application/json")

        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.json(), {"created": 1, "updated": 0})
        self.assertEqual(second.status_code, 200)
        self.assertEqual(second.json(), {"created": 0, "updated": 1})

    def test_bulk_ingest_rejects_unknown_key_without_writes(self):
        """An invalid item rejects the entire ingestion batch."""
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("plugins-api:lipford_nautobot_metrics-api:metric-ingest"),
            data={
                "values": [
                    {
                        "metric_key": "automation_adoption_rate",
                        "value": "75.0000",
                        "recorded_at": "2026-06-15T12:00:00Z",
                        "source": "integration-test",
                    },
                    {
                        "metric_key": "not-a-metric",
                        "value": "1.0000",
                        "recorded_at": "2026-06-15T12:00:00Z",
                        "source": "integration-test",
                    },
                ]
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            MetricValue.objects.filter(source="integration-test").count(),
            0,
        )


def response_definition_id(key):
    """Return the primary key for a seeded metric definition."""
    from lipford_nautobot_metrics.models import MetricDefinition

    return str(MetricDefinition.objects.get(key=key).pk)
