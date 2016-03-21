from django.contrib import admin
import sys
from .models import University, Faculty, Indicator, FacultyIndicators

reload(sys)
sys.setdefaultencoding('utf-8')

class FacultyAdmin(admin.ModelAdmin):
    fields = ['name', 'shortcut', 'university']

admin.site.register(University)
admin.site.register(Faculty, FacultyAdmin)
admin.site.register(Indicator)
admin.site.register(FacultyIndicators)
