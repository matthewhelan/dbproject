# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models



class AaaFollowing(models.Model):
    user_id = models.IntegerField(primary_key=True)  # The composite primary key (user_id, user_id_follows) found, that is not supported. The first column is selected.
    user_id_follows = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'aaa_following'
        unique_together = (('user_id', 'user_id_follows'),)


class AaaGame(models.Model):
    game_id = models.AutoField(primary_key=True)
    start_date = models.DateTimeField(blank=True, null=True)
    home_team = models.ForeignKey('AaaTeam', models.DO_NOTHING, db_column='home_team')
    away_team = models.ForeignKey('AaaTeam', models.DO_NOTHING, db_column='away_team', related_name='aaagame_away_team_set')
    home_team_score = models.IntegerField(blank=True, null=True)
    away_team_score = models.IntegerField(blank=True, null=True)
    game_done = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'aaa_game'


class AaaLeg(models.Model):
    parlay_id = models.IntegerField(primary_key=True)  # The composite primary key (parlay_id, line_id) found, that is not supported. The first column is selected.
    line_id = models.IntegerField()
    under = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'aaa_leg'
        unique_together = (('parlay_id', 'line_id'),)


class AaaLikes(models.Model):
    user = models.OneToOneField('AaaUser', models.DO_NOTHING, primary_key=True)  # The composite primary key (user_id, parlay_id) found, that is not supported. The first column is selected.
    parlay = models.OneToOneField('AaaParlay', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'aaa_likes'
        unique_together = (('user', 'parlay'), ('user', 'parlay'),)


class AaaLine(models.Model):
    line_id = models.AutoField(primary_key=True)  # The composite primary key (line_id, player_id, game_id, attribute) found, that is not supported. The first column is selected.
    player = models.OneToOneField('AaaPlayer', models.DO_NOTHING)
    game = models.ForeignKey(AaaGame, models.DO_NOTHING)
    attribute = models.CharField(max_length=30)
    under_odds = models.IntegerField()
    over_odds = models.IntegerField()
    sportsbook = models.CharField(max_length=30)
    value = models.DecimalField(max_digits=3, decimal_places=1)

    class Meta:
        managed = False
        db_table = 'aaa_line'
        unique_together = (('line_id', 'player', 'game', 'attribute'),)


class AaaParlay(models.Model):
    parlay_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('AaaUser', models.DO_NOTHING, blank=True, null=True)
    open = models.IntegerField(blank=True, null=True)
    number_of_legs = models.IntegerField(blank=True, null=True)
    amount_wagered = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'aaa_parlay'


class AaaPlayer(models.Model):
    player_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    team_name = models.ForeignKey('AaaTeam', models.DO_NOTHING, db_column='team_name')

    class Meta:
        managed = False
        db_table = 'aaa_player'


class AaaStats(models.Model):
    player_id = models.IntegerField(primary_key=True)  # The composite primary key (player_id, game_id, attribute) found, that is not supported. The first column is selected.
    game_id = models.IntegerField()
    attribute = models.CharField(max_length=30)
    value = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'aaa_stats'
        unique_together = (('player_id', 'game_id', 'attribute'),)


class AaaTeam(models.Model):
    team_name = models.CharField(primary_key=True, max_length=30)
    city = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'aaa_team'


class AaaUser(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=32)
    name = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    balance = models.DecimalField(max_digits=11, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'aaa_user'
        unique_together = (('user_id', 'user_name'),)


