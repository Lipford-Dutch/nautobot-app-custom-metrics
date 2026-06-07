"""View and API tests for Nautobot Cellular SoT."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from nautobot.users.models import Token


class CellularDashboardViewTestCase(TestCase):
    """Tests for the cellular dashboard UI."""

    def setUp(self):
        """Create a privileged user."""
        self.user = get_user_model().objects.create_superuser(username="admin", password="test")

    def test_dashboard_requires_authentication(self):
        """Anonymous users cannot access the dashboard."""
        response = self.client.get(reverse("plugins:nautobot_cellular_sot:dashboard"))

        self.assertEqual(response.status_code, 403)

    def test_dashboard_renders_empty_state(self):
        """Authenticated users can see the dashboard and empty state."""
        self.client.force_login(self.user)

        response = self.client.get(reverse("plugins:nautobot_cellular_sot:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cellular SoT Dashboard")
        self.assertContains(response, "No cellular routers are configured.")

    def test_dashboard_blocks_user_without_permissions(self):
        """Authenticated users without cellular permissions cannot view the dashboard."""
        user = get_user_model().objects.create_user(username="viewer", password="test")
        self.client.force_login(user)

        response = self.client.get(reverse("plugins:nautobot_cellular_sot:dashboard"))

        self.assertEqual(response.status_code, 403)


class CellularSummaryAPITestCase(TestCase):
    """Tests for the cellular summary and observability APIs."""

    def setUp(self):
        """Create a privileged user."""
        self.user = get_user_model().objects.create_superuser(username="admin", password="test")

    def test_summary_api_requires_authentication(self):
        """Anonymous API requests are rejected."""
        response = self.client.get(reverse("plugins-api:nautobot_cellular_sot-api:cellular-summary"))

        self.assertEqual(response.status_code, 403)

    def test_summary_api_returns_empty_rollup(self):
        """The summary API returns a deterministic empty rollup."""
        self.client.force_login(self.user)

        response = self.client.get(reverse("plugins-api:nautobot_cellular_sot-api:cellular-summary"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["router_count"], 0)
        self.assertEqual(response.json()["sim_count"], 0)

    def test_prometheus_api_accepts_token_authentication(self):
        """The Prometheus endpoint supports token-authenticated service callers."""
        token = Token.objects.create(user=self.user, key="b" * 40)

        response = self.client.get(
            reverse("plugins-api:nautobot_cellular_sot-api:cellular-prometheus"),
            HTTP_AUTHORIZATION=f"Token {token.key}",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cellular_router_info", status_code=200)
