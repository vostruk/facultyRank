from __future__ import unicode_literals
from django.db.models import signals
from django.db import models
from django.dispatch import dispatcher
import datetime
from django.dispatch import receiver

class University(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=300)

    def __str__(self):
        return self.name


class Faculty(models.Model):
    name = models.CharField(max_length=200)
    shortcut = models.CharField(max_length=50)
    total_rank = models.FloatField(default=0)
    university = models.ForeignKey(University, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Indicator(models.Model):
    name = models.CharField(max_length=300)
    shortcut = models.CharField(max_length=50)
    default_value = models.FloatField(default=0)
    scaling_factor = models.FloatField(default=1.0)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.shortcut


class FacultyIndicators(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    value = models.FloatField(default=0)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.faculty.shortcut + ":" + self.indicator.shortcut + "=" + str(self.value)


# sender - The model class. (MyModel)
# instance - The actual instance being saved.
# created - Boolean; True if a new record was created.
# *args, **kwargs - Capture the unneeded `raw` and `using`(1.3) arguments.
@receiver(signals.post_save,sender=Faculty)
def my_model_post_save(sender, instance, created, *args, **kwargs):
    print("in model save signal")
    if created:
        print("in model created")
        indicators = Indicator.objects.all()
        for i in indicators:
            new_relation = FacultyIndicators(sender, i, 0, datetime.datetime.now())
            new_relation.save()

