# Generated by Django 4.2 on 2023-04-07 00:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AaaFollowing",
            fields=[
                ("user_id", models.IntegerField(primary_key=True, serialize=False)),
                ("user_id_follows", models.IntegerField()),
            ],
            options={
                "db_table": "aaa_following",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="AaaGame",
            fields=[
                ("game_id", models.AutoField(primary_key=True, serialize=False)),
                ("start_date", models.DateTimeField(blank=True, null=True)),
                ("home_team_score", models.IntegerField(blank=True, null=True)),
                ("away_team_score", models.IntegerField(blank=True, null=True)),
                ("game_done", models.IntegerField()),
            ],
            options={
                "db_table": "aaa_game",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="AaaLeg",
            fields=[
                ("parlay_id", models.IntegerField(primary_key=True, serialize=False)),
                ("line_id", models.IntegerField()),
                ("under", models.IntegerField()),
            ],
            options={
                "db_table": "aaa_leg",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="AaaLine",
            fields=[
                ("line_id", models.AutoField(primary_key=True, serialize=False)),
                ("attribute", models.CharField(max_length=30)),
                ("under_odds", models.IntegerField()),
                ("over_odds", models.IntegerField()),
                ("sportsbook", models.CharField(max_length=30)),
                ("value", models.DecimalField(decimal_places=1, max_digits=3)),
            ],
            options={
                "db_table": "aaa_line",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="AaaParlay",
            fields=[
                ("parlay_id", models.AutoField(primary_key=True, serialize=False)),
                ("open", models.IntegerField(blank=True, null=True)),
                ("number_of_legs", models.IntegerField(blank=True, null=True)),
                (
                    "amount_wagered",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=8, null=True
                    ),
                ),
            ],
            options={
                "db_table": "aaa_parlay",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="AaaPlayer",
            fields=[
                ("player_id", models.AutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=30)),
            ],
            options={
                "db_table": "aaa_player",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="AaaStats",
            fields=[
                ("player_id", models.IntegerField(primary_key=True, serialize=False)),
                ("game_id", models.IntegerField()),
                ("attribute", models.CharField(max_length=30)),
                ("value", models.IntegerField()),
            ],
            options={
                "db_table": "aaa_stats",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="AaaTeam",
            fields=[
                (
                    "team_name",
                    models.CharField(max_length=30, primary_key=True, serialize=False),
                ),
                ("city", models.CharField(max_length=30)),
            ],
            options={
                "db_table": "aaa_team",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="AaaUser",
            fields=[
                ("user_id", models.AutoField(primary_key=True, serialize=False)),
                ("user_name", models.CharField(max_length=32)),
                ("hashed_password", models.CharField(max_length=128)),
                ("salt", models.CharField(max_length=64)),
                ("name", models.CharField(max_length=30)),
                ("email", models.CharField(max_length=30)),
                ("balance", models.DecimalField(decimal_places=2, max_digits=11)),
            ],
            options={
                "db_table": "aaa_user",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="AaaLikes",
            fields=[
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        primary_key=True,
                        serialize=False,
                        to="parlaypro.aaauser",
                    ),
                ),
            ],
            options={
                "db_table": "aaa_likes",
                "managed": False,
            },
        ),
    ]
