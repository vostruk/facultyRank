from __future__ import unicode_literals
from django.db.models import signals
from django.db import models
import datetime
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.shortcuts import get_list_or_404
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

class University(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    total_rank = models.FloatField(default=0)
    university_managers = models.ManyToManyField(User)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Uniwersytet')
        verbose_name_plural = _('Uniwersytety')


class Faculty(models.Model):
    name = models.CharField(max_length=200, verbose_name = _('Nazwa'))
    shortcut = models.CharField(max_length=50, verbose_name = _('Nazwa skrócona'))
    total_rank = models.FloatField(default=0)
    university = models.ForeignKey(University, on_delete=models.CASCADE, verbose_name = _('Uniwersytet'))
    faculty_managers = models.ManyToManyField(User, verbose_name = _('Administratorzy wydziału'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Wydział')
        verbose_name_plural = _('Wydziały')


class Indicator(models.Model):
    given_id = models.CharField(max_length=10, default="", unique=True, verbose_name = _('Nadany identyfikator'))
    name = models.TextField(verbose_name = _('Wskaźnik'))
    shortcut = models.CharField(max_length=50, verbose_name = _('Krótka nazwa'))
    default_value = models.FloatField(default=0, verbose_name = _('Wartość domyślna'))
    scaling_factor = models.FloatField(default=1.0, verbose_name = _('Współczynnik skalowania'))
    pub_date = models.DateField( verbose_name = _('Data utworzenia'), default=datetime.date.today)

    def __str__(self):
        return self.shortcut

    class Meta:
        verbose_name = _('Wskaźnik')
        verbose_name_plural = _('Wskaźniki')


class IndicatorIntervals(models.Model):
    start_date = models.DateField('Data początku okresu', default=datetime.date.today)
    end_date = models.DateField('Data konca okresu', default=datetime.date.today)
    comment = models.TextField(default="", verbose_name = _('Uwagi'))

    def __str__(self):
        return str(self.start_date.month) + ":" + str(self.start_date.year) + " - " + \
               str(self.end_date.month) + ":" + str(self.end_date.year)

    class Meta:
        verbose_name = _('Okres wskaźnika')
        verbose_name_plural = _('Okresy wskaźników')


class FacultyIndicators(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    significance_coefficient = models.IntegerField(default=0)
    ease_coefficient = models.IntegerField(default=0)
    value = models.FloatField(default=0)
    time_interval = models.ForeignKey(IndicatorIntervals, on_delete=models.CASCADE)
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

    class Meta:
        verbose_name = _('Wskaźnik wydziałowy')
        verbose_name_plural = _('Wskaźniki wydziałowe')


# sender - The model class. (MyModel)
# instance - The actual instance being saved.
# created - Boolean; True if a new record was created.
# *args, **kwargs - Capture the unneeded `raw` and `using`(1.3) arguments.
@receiver(signals.post_save,sender=Faculty)
def faculty_post_save(sender, instance, created, *args, **kwargs):
    if created:
        print("Trigger for indicators after new faculty was created")
        #create a group with a faculty name to be used for faculty staff
        #new_group, group_created = Group.objects.get_or_create(name=instance.name + '-' +
        #                                                            instance.university.name+"$"+str(instance.id))
        #if group_created:
        #    new_group.save()
        #trigger a list of indicators for this faculty
        intervals = IndicatorIntervals.objects.all()
        indicators = Indicator.objects.all()
        for i in indicators:
            for inter in intervals:
                new_relation = FacultyIndicators.objects.create(faculty_id=instance.id, indicator_id=i.id,
                                                                significance_coefficient = 0, ease_coefficient=0,
                                                                value = 0.0, time_interval_id=inter.id,
                                                                pub_date = datetime.datetime.now())
                new_relation.save()


@receiver(signals.post_save, sender=IndicatorIntervals)
def interval_post_save(sender, instance, created, *args, **kwargs):
    if created:
        print("Trigger for faculties after new indicator was created")
        faculties = Faculty.objects.all()
        indicators = Indicator.objects.all()
        for f in faculties:
            for i in indicators:
                new_relation = FacultyIndicators.objects.create(faculty_id=f.id, indicator_id=i.id,
                                                                significance_coefficient = 0, ease_coefficient=0,
                                                                value = 0.0, time_interval_id = instance.id,
                                                                pub_date = datetime.datetime.now())
                new_relation.save()


@receiver(signals.post_save, sender=Indicator)
def indicator_post_save(sender, instance, created, *args, **kwargs):
    if created:
        print("Trigger for faculties after new indicator was created")
        faculties = Faculty.objects.all()
        intervals = IndicatorIntervals.objects.all()
        for f in faculties:
            for i in intervals:
                new_relation = FacultyIndicators.objects.create(faculty_id=f.id, indicator_id=instance.id,
                                                                significance_coefficient = 0, ease_coefficient=0,
                                                                value = 0.0, time_interval_id = i.id,
                                                                pub_date = datetime.datetime.now())
                new_relation.save()


@receiver(signals.post_save,sender=FacultyIndicators)
def faculty_indicators_post_save(sender, instance, created, *args, **kwargs):
    print("Changing faculty total rank")
    indicators = get_list_or_404(FacultyIndicators, faculty_id = instance.faculty.id)
    instance.faculty.total_rank = 0;
    for i in indicators:
        instance.faculty.total_rank += i.value*i.indicator.scaling_factor
    instance.faculty.save()
