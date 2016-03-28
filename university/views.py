# -*- coding: utf-8 -*-
import sys
from django.shortcuts import render, get_object_or_404, get_list_or_404
from .models import University, Faculty, FacultyIndicators, Indicator
from django.core.urlresolvers import reverse
from django.views import generic
from django.template import *

reload(sys)
sys.setdefaultencoding('utf-8')


class IndexView(generic.ListView):
    model = University
    template_name = 'university/index.html'


class FacultiesView(generic.ListView):
    model = Faculty
    template_name = 'university/faculties.html'

    def get_queryset(self):
        return Faculty.objects.filter(university_id=self.kwargs['university_id']).order_by('-total_rank')


class FacultyIndicatorsView(generic.ListView):
    model = FacultyIndicators
    template_name='university/facultyIndicators.html'

    def get_context_data(self, **kwargs):
        context = super(FacultyIndicatorsView, self).get_context_data(**kwargs)
        context['chosen_faculty'] = get_object_or_404(Faculty, pk=self.kwargs['faculty_id_chose'])
        context['faculty_indicators_list'] = get_list_or_404(FacultyIndicators, faculty_id=self.kwargs['faculty_id_chose'])
        context['indicators_list'] = Indicator.objects.all()
        return context