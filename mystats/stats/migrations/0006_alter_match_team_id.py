# Generated by Django 4.2.9 on 2024-04-06 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("stats", "0005_delete_matchresult_match_team_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="match", name="team_id", field=models.IntegerField(default=0),
        ),
    ]
