"""Cross-entry validation for metric data."""

from nautobot.apps.models import CustomValidator


class MetricValueContextValidator(CustomValidator):
    """Keep metric dimensions consistently object-shaped for API consumers."""

    model = "lipford_nautobot_metrics.metricvalue"

    def clean(self):
        """Reject valid JSON values that are not key/value mappings."""
        obj = self.context["object"]
        if not isinstance(obj.context, dict):
            self.validation_error({"context": "Metric context must be a JSON object of label/value pairs."})


custom_validators = [MetricValueContextValidator]
