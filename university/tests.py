from django.test import TestCase
from django.core.urlresolvers import reverse
import datetime
from django.utils import timezone
from django.test import Client
from university.models import *
from django.test.utils import setup_test_environment
setup_test_environment()


def create_random_university(n):
    return University.objects.create(name=n, shortcut=n)
def create_random_faculty(n, u):
    return Faculty.objects.create(name=n, shortcut=n, university=u)


class FacultiesViewTests(TestCase):
    def test_index_view_with_no_universities(self):

        #If no universities added yet, an appropriate message should be shown.
        response = self.client.get(reverse('university:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No universities added yet")
        self.assertQuerysetEqual(response.context['object_list'], [])

    def test_index_view_with_a_university(self):

        uni = create_random_university("Politechnika Warszawska")
        fac = create_random_faculty("EiTI", uni )
        response = self.client.get(reverse('university:index'))
        self.assertQuerysetEqual(
            response.context['object_list'],
            ['<University: Politechnika Warszawska>']
        )
        #teraz logowanie użytkownika
        #c.login(username='fred', password='secret')