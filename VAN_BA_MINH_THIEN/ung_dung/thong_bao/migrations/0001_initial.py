from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("kind", models.CharField(choices=[("job_match", "Việc làm phù hợp"), ("candidate_match", "Ứng viên phù hợp")], max_length=30)),
                ("title", models.CharField(max_length=180)),
                ("message", models.CharField(max_length=600)),
                ("target_url", models.CharField(max_length=700)),
                ("dedupe_key", models.CharField(max_length=64)),
                ("score", models.DecimalField(decimal_places=1, max_digits=5)),
                ("ai_generated", models.BooleanField(default=False)),
                ("is_read", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("recipient", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notifications", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "db_table": "notifications",
                "ordering": ("-created_at", "-pk"),
                "verbose_name": "Thông báo",
                "verbose_name_plural": "Thông báo",
            },
        ),
        migrations.AddConstraint(
            model_name="notification",
            constraint=models.UniqueConstraint(fields=("recipient", "dedupe_key"), name="uniq_notification_recipient_key"),
        ),
        migrations.AddIndex(
            model_name="notification",
            index=models.Index(fields=["recipient", "is_read", "created_at"], name="notif_user_read_created_idx"),
        ),
    ]
