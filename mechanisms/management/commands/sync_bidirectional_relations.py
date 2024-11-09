from django.core.management.base import BaseCommand
from mechanisms.models import Mechanism
from experts.models import Expert
from builds.models import Build
from courses.models import Course

def ensure_bidirectional_relation(instance, related_field_name, reverse_related_field_name):
    related_objects = getattr(instance, related_field_name).all()
    reverse_related_field = reverse_related_field_name

    for related_obj in related_objects:
        reverse_relation = getattr(related_obj, reverse_related_field)
        if instance not in reverse_relation.all():
            reverse_relation.add(instance)

class Command(BaseCommand):
    help = 'Ensure bidirectional relationships for all related fields'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting bidirectional relations sync...\n')

        for mechanism in Mechanism.objects.all():
            ensure_bidirectional_relation(mechanism, 'builds', 'mechanisms')
            ensure_bidirectional_relation(mechanism, 'experts', 'mechanisms')
            ensure_bidirectional_relation(mechanism, 'courses', 'mechanisms')

        for expert in Expert.objects.all():
            ensure_bidirectional_relation(expert, 'builds', 'experts')
            ensure_bidirectional_relation(expert, 'mechanisms', 'experts')
            ensure_bidirectional_relation(expert, 'courses', 'experts')

        for build in Build.objects.all():
            ensure_bidirectional_relation(build, 'mechanisms', 'builds')
            ensure_bidirectional_relation(build, 'experts', 'builds')
            ensure_bidirectional_relation(build, 'courses', 'builds')

        for course in Course.objects.all():
            ensure_bidirectional_relation(course, 'builds', 'courses')
            ensure_bidirectional_relation(course, 'experts', 'courses')
            ensure_bidirectional_relation(course, 'mechanisms', 'courses')

        self.stdout.write('Bidirectional relationships updated successfully!\n')
