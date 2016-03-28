from __future__ import unicode_literals
from django.db.models import signals
from django.db import models
import datetime
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.shortcuts import get_list_or_404
from django.db.models import Q


class University(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    total_rank = models.FloatField(default=0)
    university_managers = models.ManyToManyField(User)

    def __str__(self):
        return self.name


class Faculty(models.Model):
    name = models.CharField(max_length=200)
    shortcut = models.CharField(max_length=50)
    total_rank = models.FloatField(default=0)
    university = models.ForeignKey(University, on_delete=models.CASCADE)
    faculty_managers = models.ManyToManyField(User)

    def __str__(self):
        return self.name


class Indicator(models.Model):
    given_id = models.CharField(max_length=10, default="", unique=True)
    name = models.TextField()
    shortcut = models.CharField(max_length=50)
    default_value = models.FloatField(default=0)
    scaling_factor = models.FloatField(default=1.0)
    pub_date = models.DateField('date published', default=datetime.date.today)

    def __str__(self):
        return self.shortcut


class FacultyIndicators(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    significance_coefficient = models.IntegerField(default=0)
    ease_coefficient = models.IntegerField(default=0)
    value = models.FloatField(default=0)
    time_interval_start = models.DateField('Interval start date', default=datetime.date.today)
    time_interval_end = models.DateField('Interval end date', default=datetime.date.today)
    comment = models.TextField(default="")
    pub_date = models.DateField('date published', default=datetime.date.today)

    def full_name(self):
        return self.indicator.name

    def get_queryset(self, request):
        groups = request.user.groups.all()
        query = Q()
        for g in groups:
            g_list = g.name.split('$')
            if len(g_list)>1:
                query = query | Q(faculty__id=g_list[1])
        return FacultyIndicators.objects.filter(query)

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
            new_relation = FacultyIndicators.objects.create(faculty_id=instance.id, indicator_id=i.id,
                                                            significance_coefficient = 0, ease_coefficient=0,
                                                            time_interval_start=datetime.date.today(),
                                                            time_interval_end=datetime.date.today(), comment="",
                                                            value = 0.0, pub_date = datetime.datetime.now())
            new_relation.save()


@receiver(signals.post_save, sender=Indicator)
def indicator_post_save(sender, instance, created, *args, **kwargs):
    if created:
        print("Trigger for faculties after new indicator was created")
        faculties = Faculty.objects.all()
        for f in faculties:
            new_relation = FacultyIndicators.objects.create(faculty_id=f.id, indicator_id=instance.id,
                                                            significance_coefficient = 0, ease_coefficient=0,
                                                            time_interval_start=datetime.date.today(),
                                                            time_interval_end=datetime.date.today(), comment="",
                                                            value = 0.0, pub_date = datetime.datetime.now())
            new_relation.save()


@receiver(signals.post_save,sender=FacultyIndicators)
def faculty_indicators_post_save(sender, instance, created, *args, **kwargs):
    print("Changing faculty total rank")
    indicators = get_list_or_404(FacultyIndicators, faculty_id = instance.faculty.id)
    instance.faculty.total_rank = 0;
    for i in indicators:
        instance.faculty.total_rank += i.value*i.indicator.scaling_factor
    instance.faculty.save()
