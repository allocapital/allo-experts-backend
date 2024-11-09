from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Build
from mechanisms.models import Mechanism
from experts.models import Expert
from courses.models import Course
from core.signals import sync_bidirectional_relation

@receiver(m2m_changed, sender=Build.mechanisms.through)
def update_mechanisms_relation(sender, instance, action, pk_set, **kwargs):
    """
    A receiver for the 'mechanisms' field of a Build. This will synchronize
    the mechanism objects when the Build's mechanisms are modified.
    """
    sync_bidirectional_relation(
        instance=instance,
        action=action,
        pk_set=pk_set,
        related_model=Mechanism,
        related_field_name='builds',
        **kwargs
    )
@receiver(m2m_changed, sender=Build.experts.through)
def update_experts_relation(sender, instance, action, pk_set, **kwargs):
    """
    A receiver for the 'experts' field of a Build. This will synchronize
    the expert objects when the Build's experts are modified.
    """
    sync_bidirectional_relation(
        instance=instance,
        action=action,
        pk_set=pk_set,
        related_model=Expert,
        related_field_name='builds',
        **kwargs
    )
@receiver(m2m_changed, sender=Build.courses.through)
def update_courses_relation(sender, instance, action, pk_set, **kwargs):
    """
    A receiver for the 'courses' field of a Build. This will synchronize
    the build objects when the Build's courses are modified.
    """
    sync_bidirectional_relation(
        instance=instance,
        action=action,
        pk_set=pk_set,
        related_model=Course,
        related_field_name='builds',
        **kwargs
    )