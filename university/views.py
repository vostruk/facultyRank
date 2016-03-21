# -*- coding: utf-8 -*-
import sys
from django.shortcuts import render, get_object_or_404, get_list_or_404
from .models import University, Faculty, FacultyIndicators, Indicator
from django.core.urlresolvers import reverse
from django.views import generic

reload(sys)
sys.setdefaultencoding('utf-8')


class IndexView(generic.ListView):
    template_name = 'university/index.html'
    context_object_name = 'university_list'

    def get_queryset(self):
        return University.objects.all()

"""class University(generic.DetailView):
    model = University
    template_name = 'university/faculties.html'
"""

def university(request, university_id):
    chosen_university = get_object_or_404(University, pk=university_id)
    faculty_list = Faculty.objects.filter(university_id=chosen_university.id)
    context = {
        'faculty_list': faculty_list,
        'chosen_university':chosen_university,
    }
    return render(request, 'university/faculties.html', context)


def faculty(request, university_id, faculty_id_chose):
    chosen_faculty = get_object_or_404(Faculty, pk=faculty_id_chose)
    faculty_indicators_list = get_list_or_404(FacultyIndicators, faculty_id = faculty_id_chose)
    indicators_list = Indicator.objects.all()
    context = {
        'chosen_faculty': chosen_faculty,
        'faculty_indicators_list':faculty_indicators_list,
        'indicators_list':indicators_list,
    }
    return render(request, 'university/faculty.html', context)
