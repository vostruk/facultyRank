# -*- coding: utf-8 -*-
import sys

from django.contrib import admin
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _
from .models import University, Faculty, Indicator, FacultyIndicators, IndicatorIntervals




class FacultyAdmin(admin.ModelAdmin):
    fields = ['name', 'shortcut', 'university', 'faculty_managers']
    list_display = ('name', 'shortcut', 'total_rank', 'university')


class RelatedFacultyFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Wydział')

    parameter_name = 'faculty'

    def lookups(self, request, model_admin):
        if request.user.is_superuser:
            fall=Faculty.objects.all()
            return [(f.id, f.name) for f in fall]
        l = []
        for g in request.user.faculty_set.all():
            l.append((g.id, g.name))
        return l

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(faculty_id=self.value())
        return queryset


class CorrespondingDateFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Okres')

    parameter_name = 'time_interval'

    def lookups(self, request, model_admin):
        l=[]
        dates = IndicatorIntervals.objects.all()
        for d in dates:
            l.append((d.id, d))
        return l

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(time_interval_id=self.value())


class FacultyIndicatorsAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj and not request.user.is_superuser:
            return ['faculty', 'indicator'] # Return a list or tuple of readonly fields' names
        return []

#    readonly_fields= []
    fields = ['indicator', 'faculty', 'value', 'significance_coefficient', 'ease_coefficient', 'time_interval', 'pub_date']
    list_display = ('indicator', 'faculty', 'value', 'time_interval')
    list_filter = (RelatedFacultyFilter, 'value', 'indicator', CorrespondingDateFilter)
    search_fields = ['indicator__name']
    list_per_page = 20



    def get_queryset(self, request):
        qs = super(FacultyIndicatorsAdmin, self).get_queryset(request)
        if request.user.is_superuser:
                return qs
        fl = FacultyIndicators.objects.exclude(faculty__id__in=request.user.faculty_set.all()).values_list('id', flat=True)
        return qs.exclude(pk__in=fl)

    def export_csv(modeladmin, request, queryset):
        import csv
        from django.utils.encoding import smart_str
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=facultyIndicators.csv'
        writer = csv.writer(response, csv.excel)
        response.write(u'\ufeff'.encode('utf8')) # BOM (optional...Excel needs it to open UTF-8 file properly)
        writer.writerow([
            smart_str(u"ID"),
            smart_str(u"faculty"),
            smart_str(u"Indicator"),
            smart_str(u"Value"),
            smart_str(u"Start date"),
            smart_str(u"Finish date"),
        ])
        for obj in queryset:
            writer.writerow([
                smart_str(obj.pk),
                smart_str(obj.faculty),
                smart_str(obj.indicator),
                smart_str(obj.value),
                smart_str(obj.time_interval.start_date),
                smart_str(obj.time_interval.end_date),
            ])
        return response

    def export_xlsx(modeladmin, request, queryset):
        import openpyxl
        from openpyxl.cell import get_column_letter
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=facultyIndicators.xlsx'
        wb = openpyxl.Workbook()
        ws = wb.get_active_sheet()
        ws.title = "MyModel"

        row_num = 0

        columns = [
            (u"ID", 15),
            (u"Faculty", 40),
            (u"Indicator", 40),
            (u"Value", 10),
            (u"Start date", 15),
            (u"End date", 15),
            (u"Comment", 15),
        ]

        for col_num in xrange(len(columns)):
            c = ws.cell(row=row_num + 1, column=col_num + 1)
            c.value = columns[col_num][0]
            c.style.font.bold = True
            # set column width
            ws.column_dimensions[get_column_letter(col_num+1)].width = columns[col_num][1]

        for obj in queryset:
            row_num += 1
            row = [
                obj.pk,
                str(obj.faculty),
                str(obj.indicator),
                obj.value,
                obj.time_interval.start_date,
                obj.time_interval.end_date,
                obj.comment,
            ]
            for col_num in xrange(len(row)):
                c = ws.cell(row=row_num + 1, column=col_num + 1)
                c.value = row[col_num]
                c.style.alignment.wrap_text = True

        wb.save(response)
        return response

    actions = [export_csv, export_xlsx]
    export_xlsx.short_description = u"Eksport do XLSX"
    export_csv.short_description = u"Eksport do CSV"


admin.site.register(University)
admin.site.register(Faculty, FacultyAdmin)
admin.site.register(Indicator)
admin.site.register(FacultyIndicators,FacultyIndicatorsAdmin)
admin.site.register(IndicatorIntervals)

