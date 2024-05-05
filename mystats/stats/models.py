from django.db import models
from django.utils.timezone import now
class Match(models.Model):
    def __str__(self):
        return "%s %s" % (str(self.match_id), self.player)

    id = models.BigAutoField(primary_key=True)
    match_id = models.IntegerField(default=0)
    player = models.TextField()
    team_id = models.IntegerField(default=0)
    win = models.BooleanField(default=False)
    draw = models.BooleanField(default=False)
    loss = models.BooleanField(default=False)
    date = models.DateTimeField(default=now)

class Stats(models.Model):
    def __str__(self):
        return "%s %s" % (str(self.stat_id), self.player_s)
    id = models.BigAutoField(primary_key=True)
    stat_id = models.IntegerField(default=0)
    player_s = models.TextField()
    fraction = models.DecimalField(max_digits=5,decimal_places=3)