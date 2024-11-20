from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Category
from courses.models import Course
from experts.models import Expert
from builds.models import Build
from mechanisms.models import Mechanism
from core.signals import sync_bidirectional_relation

@receiver(m2m_changed, sender=Category.courses.through)
def update_courses_relation(sender, instance, action, pk_set, **kwargs):
    """
    A receiver for the 'courses' field of a Category. This will synchronize
    the Category objects when the Category's courses are modified.
    """
    sync_bidirectional_relation(
        instance=instance,
        action=action,
        pk_set=pk_set,
        related_model=Course,
        related_field_name='categories',
        **kwargs
    )
@receiver(m2m_changed, sender=Category.experts.through)
def update_experts_relation(sender, instance, action, pk_set, **kwargs):
    """
    A receiver for the 'experts' field of a Category. This will synchronize
    the expert objects when the Category's experts are modified.
    """
    sync_bidirectional_relation(
        instance=instance,
        action=action,
        pk_set=pk_set,
        related_model=Expert,
        related_field_name='categories',
        **kwargs
    )
@receiver(m2m_changed, sender=Category.builds.through)
def update_builds_relation(sender, instance, action, pk_set, **kwargs):
    """
    A receiver for the 'builds' field of a Category. This will synchronize
    the build objects when the Category's builds are modified.
    """
    sync_bidirectional_relation(
        instance=instance,
        action=action,
        pk_set=pk_set,
        related_model=Build,
        related_field_name='categories',
        **kwargs
    )

@receiver(m2m_changed, sender=Category.mechanisms.through)
def update_mechanisms_relation(sender, instance, action, pk_set, **kwargs):
    """
    A receiver for the 'mechanisms' field of a Category. This will synchronize
    the build objects when the Category's mechanisms are modified.
    """
    sync_bidirectional_relation(
        instance=instance,
        action=action,
        pk_set=pk_set,
        related_model=Mechanism,
        related_field_name='categories',
        **kwargs
    )