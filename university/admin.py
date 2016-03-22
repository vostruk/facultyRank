from django.contrib import admin
import sys
from .models import University, Faculty, Indicator, FacultyIndicators
from django.utils.translation import ugettext_lazy as _

reload(sys)
sys.setdefaultencoding('utf-8')


class FacultyAdmin(admin.ModelAdmin):
    fields = ['name', 'shortcut', 'university']
    list_display = ('name', 'shortcut', 'university')


class RelatedFacultyFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Related faculty')

    parameter_name = 'faculty'

    def lookups(self, request, model_admin):
        l = []
        for g in request.user.groups.all():
            param3 = g.name.split("$")
            if len(param3)>1:
                f_name = param3[0].split('-')[0]
                l.append((param3[1], f_name))
        return l

    def queryset(self, request, queryset):
        if self.value():
  #          if request.user.is_superuser:
   #             return queryset
            return queryset.filter(faculty__id__exact=self.value())
      #  else:
     #       return queryset


class FacultyIndicatorsAdmin(admin.ModelAdmin):
    fields = ['value', 'pub_date']
    list_display = ('indicator', 'faculty', 'value', 'pub_date')
    list_filter = (RelatedFacultyFilter,)
    search_fields = ['indicator__name']
    list_per_page = 20


admin.site.register(University)
admin.site.register(Faculty, FacultyAdmin)
admin.site.register(Indicator)
admin.site.register(FacultyIndicators,FacultyIndicatorsAdmin)
