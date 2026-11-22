"""Reusable Jinja filters for metric displays."""

from decimal import Decimal

from django_jinja import library


@library.filter
def compact_metric_value(value):
    """Format decimal metric values without insignificant trailing zeroes."""
    if value is None:
        return "—"
    if isinstance(value, Decimal):
        return format(value.normalize(), "f")
    return str(value)
