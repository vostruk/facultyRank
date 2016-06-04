# -*- coding: utf-8 -*-
import sys
from django.shortcuts import render, get_object_or_404, get_list_or_404
from .models import University, Faculty, FacultyIndicators, Indicator, IndicatorIntervals
from django.core.urlresolvers import reverse
from django.views import generic
from django.template import *
from chartit import DataPool, Chart
from datetime import datetime
from datetime import date
reload(sys)
sys.setdefaultencoding('utf-8')


class IndexView(generic.ListView):
    model = University
    template_name = 'university/index.html'

class calcMethod(generic.ListView):
    model = University
    template_name = 'university/calcMethod.html'

class people(generic.ListView):
    model = University
    template_name = 'university/people.html'

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
       # context['faculty_indicators_list'] = get_list_or_404(FacultyIndicators, faculty_id=self.kwargs['faculty_id_chose'])
        indicators_list = Indicator.objects.all()
        #context['indicators_list'] = indicators_list
        context['times_list'] = IndicatorIntervals.objects.order_by('-end_date')
        times = IndicatorIntervals.objects.all()

        seriesAll = []
        termsAll = {}

        for i in indicators_list:
            seriesAll.append({'options': {
                   'source': FacultyIndicators.objects.filter(indicator_id=i.id, faculty_id=self.kwargs['faculty_id_chose'])},
                  'terms': [
                      {str(i.shortcut):'value'},
                      {'time_interval'+str(i.id) : 'time_interval__end_date'}

                    ]})
            termsAll['time_interval'+str(i.id)] = [str(i.shortcut)]

        series_optAll = [{'options':{
                          'type': 'line',
                          'stacking': False},
                        'terms': termsAll}]

        indicatorsChartData = \
            DataPool(
               series=seriesAll
              )

        #Step 2: Create the Chart objec
        chtIndicatorsTime = Chart(
                datasource = indicatorsChartData,
                series_options = series_optAll,
                chart_options =
                  {'title': {
                       'text': 'Zmiana wskaźników w czasie'},
                   'xAxis': {
                        'title': {
                           'text': 'Time period'}}}#,
                   # x_sortf_mapf_mts=(None, lambda inr: datetime.fromtimestamp(inr).strftime("%H:%M"), False)
        )

        last_period = IndicatorIntervals.objects.order_by('-end_date')[0]

        indicatorsPieData = \
            DataPool(
                series=
                [{'options': {
                    'source':FacultyIndicators.objects.filter(time_interval_id=last_period.id, faculty_id=self.kwargs['faculty_id_chose']
                            )
                },
                  'terms': [
                    'indicator__shortcut',
                    'value']}
                 ]
              )
        chtPie = Chart(
            datasource = indicatorsPieData,
            series_options =
              [{'options':{
                  'type': 'pie',
                  'stacking': False
                },
                'terms':{
                  'indicator__shortcut': [
                    'value']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Udzial wskazkikow w ogolnym rankingu'}}
        )
        context['indicatorsChart'] = [
                                      chtIndicatorsTime,
                                      chtIndicatorsTime
                                    ]
        return context


