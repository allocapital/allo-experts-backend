from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Expert
from mechanisms.models import Mechanism
from courses.models import Course
from builds.models import Build
from categories.models import Category
from core.signals import sync_bidirectional_relation

@receiver(m2m_changed, sender=Expert.mechanisms.through)
def update_mechanisms_relation(sender, instance, action, pk_set, **kwargs):
    """
    A receiver for the 'mechanisms' field of a Expert. This will synchronize
    the mechanism objects when the Expert's mechanisms are modified.
    """
    sync_bidirectional_relation(
        instance=instance,
        action=action,
        pk_set=pk_set,
        related_model=Mechanism,
        related_field_name='experts',
        **kwargs
    )
@receiver(m2m_changed, sender=Expert.courses.through)
def update_courses_relation(sender, instance, action, pk_set, **kwargs):
    """
    A receiver for the 'courses' field of a Expert. This will synchronize
    the expert objects when the Expert's courses are modified.
    """
    sync_bidirectional_relation(
        instance=instance,
        action=action,
        pk_set=pk_set,
        related_model=Course,
        related_field_name='experts',
        **kwargs
    )
@receiver(m2m_changed, sender=Expert.builds.through)
def update_builds_relation(sender, instance, action, pk_set, **kwargs):
    """
    A receiver for the 'builds' field of a Expert. This will synchronize
    the build objects when the Expert's builds are modified.
    """
    sync_bidirectional_relation(
        instance=instance,
        action=action,
        pk_set=pk_set,
        related_model=Build,
        related_field_name='experts',
        **kwargs
    )

@receiver(m2m_changed, sender=Expert.categories.through)
def update_categories_relation(sender, instance, action, pk_set, **kwargs):
    """
    A receiver for the 'categories' field of a Expert. This will synchronize
    the category objects when the Expert's categories are modified.
    """
    sync_bidirectional_relation(
        instance=instance,
        action=action,
        pk_set=pk_set,
        related_model=Category,
        related_field_name='experts',
        **kwargs
    )