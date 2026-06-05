"""View and API tests for Lipford Nautobot Metrics."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from nautobot.users.models import Token

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
        self.assertContains(response, "Automation Adoption Rate")

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
        self.assertEqual(response.json()["count"], 2)
        self.assertEqual(
            {item["key"] for item in response.json()["results"]},
            {"automation_adoption_rate", "time_saved_per_automated_task"},
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
        self.assertEqual(response.json()["count"], 2)


def response_definition_id(key):
    """Return the primary key for a seeded metric definition."""
    from lipford_nautobot_metrics.models import MetricDefinition

    return str(MetricDefinition.objects.get(key=key).pk)
