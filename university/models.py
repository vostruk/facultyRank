from __future__ import unicode_literals
from django.db.models import signals
from django.db import models
import datetime
from django.dispatch import receiver
from django.contrib.auth.models import Group


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

    def full_name(self):
        return self.indicator.name

    def __str__(self):
        return self.faculty.shortcut + " : " + self.indicator.shortcut


# sender - The model class. (MyModel)
# instance - The actual instance being saved.
# created - Boolean; True if a new record was created.
# *args, **kwargs - Capture the unneeded `raw` and `using`(1.3) arguments.
@receiver(signals.post_save,sender=Faculty)
def faculty_post_save(sender, instance, created, *args, **kwargs):
    if created:
        print("Trigger for indicators after new faculty was created")
        #create a group with a faculty name to be used for faculty staff
        new_group, group_created = Group.objects.get_or_create(name=instance.name + '-' +
                                                                    instance.university.name+"$"+str(instance.id))
        if group_created:
            new_group.save()
        #trigger a list of indicators for this faculty
        indicators = Indicator.objects.all()
        for i in indicators:
            new_relation = FacultyIndicators.objects.create(faculty_id=instance.id, indicator_id=i.id, value = 0.0, pub_date = datetime.datetime.now())
            new_relation.save()

@receiver(signals.post_save,sender=Indicator)
def indicator_post_save(sender, instance, created, *args, **kwargs):
    if created:
        print("Trigger for faculties after new indicator was created")
        faculties = Faculty.objects.all()
        for f in faculties:
            new_relation = FacultyIndicators.objects.create(faculty_id=f.id, indicator_id=instance.id, value = 0.0, pub_date = datetime.datetime.now())
            new_relation.save()

