from django.db import models
from django.contrib.auth.models import User

class LikeDislike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item_id = models.ForeignKey('Item', on_delete=models.CASCADE)
    like = models.NullBooleanField(default=None)

class Item(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
