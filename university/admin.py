from django.contrib import admin
import sys
from django.db import models
from .models import University, Faculty, Indicator, FacultyIndicators
from django.utils.translation import ugettext_lazy as _

reload(sys)
sys.setdefaultencoding('utf-8')


class FacultyAdmin(admin.ModelAdmin):
    fields = ['name', 'shortcut', 'university', 'faculty_managers']
    list_display = ('name', 'shortcut', 'total_rank', 'university')


class RelatedFacultyFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Related faculty')

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


class FacultyIndicatorsAdmin(admin.ModelAdmin):
    fields = ['value', 'pub_date']
    list_display = ('indicator', 'faculty', 'value', 'pub_date')
    list_filter = (RelatedFacultyFilter, 'value', 'indicator')
    search_fields = ['indicator__name']
    list_per_page = 20


    def get_queryset(self, request):
        qs = super(FacultyIndicatorsAdmin, self).get_queryset(request)
        if request.user.is_superuser:
                return qs
        fl = FacultyIndicators.objects.exclude(faculty__id__in=request.user.faculty_set.all()).values_list('id', flat=True)
        return qs.exclude(pk__in=fl)



admin.site.register(University)
admin.site.register(Faculty, FacultyAdmin)
admin.site.register(Indicator)
admin.site.register(FacultyIndicators,FacultyIndicatorsAdmin)


