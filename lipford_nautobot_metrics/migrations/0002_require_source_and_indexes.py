from django.db import migrations, models


def backfill_blank_sources(apps, schema_editor):
    metric_value = apps.get_model("lipford_nautobot_metrics", "MetricValue")
    metric_value.objects.filter(source="").update(source="legacy")


class Migration(migrations.Migration):
    dependencies = [
        ("lipford_nautobot_metrics", "0001_initial_metrics"),
    ]

    operations = [
        migrations.RunPython(backfill_blank_sources, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="metricvalue",
            name="source",
            field=models.CharField(
                help_text="Collector, job, integration, or manual source that produced this observation.",
                max_length=255,
            ),
        ),
        migrations.AddIndex(
            model_name="metricvalue",
            index=models.Index(fields=["metric_definition", "recorded_at"], name="lip_metrics_def_time_idx"),
        ),
        migrations.AddIndex(
            model_name="metricvalue",
            index=models.Index(fields=["source", "recorded_at"], name="lip_metrics_src_time_idx"),
        ),
    ]
