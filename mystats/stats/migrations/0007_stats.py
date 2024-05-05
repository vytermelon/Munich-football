# Generated by Django 4.2.9 on 2024-04-10 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("stats", "0006_alter_match_team_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="Stats",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("stat_id", models.IntegerField(default=0)),
                ("player_s", models.TextField()),
                ("fraction", models.IntegerField(default=0)),
            ],
        ),
    ]