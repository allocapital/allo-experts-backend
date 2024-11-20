from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Mechanism
from courses.models import Course
from experts.models import Expert
from builds.models import Build
from categories.models import Category
from core.signals import sync_bidirectional_relation

@receiver(m2m_changed, sender=Mechanism.courses.through)
def update_courses_relation(sender, instance, action, pk_set, **kwargs):
    """
    A receiver for the 'courses' field of a Mechanism. This will synchronize
    the mechanism objects when the Mechanism's courses are modified.
    """
    sync_bidirectional_relation(
        instance=instance,
        action=action,
        pk_set=pk_set,
        related_model=Course,
        related_field_name='mechanisms',
        **kwargs
    )
@receiver(m2m_changed, sender=Mechanism.experts.through)
def update_experts_relation(sender, instance, action, pk_set, **kwargs):
    """
    A receiver for the 'experts' field of a Mechanism. This will synchronize
    the expert objects when the Mechanism's experts are modified.
    """
    sync_bidirectional_relation(
        instance=instance,
        action=action,
        pk_set=pk_set,
        related_model=Expert,
        related_field_name='mechanisms',
        **kwargs
    )
@receiver(m2m_changed, sender=Mechanism.builds.through)
def update_builds_relation(sender, instance, action, pk_set, **kwargs):
    """
    A receiver for the 'builds' field of a Mechanism. This will synchronize
    the build objects when the Mechanism's builds are modified.
    """
    sync_bidirectional_relation(
        instance=instance,
        action=action,
        pk_set=pk_set,
        related_model=Build,
        related_field_name='mechanisms',
        **kwargs
    )
@receiver(m2m_changed, sender=Mechanism.categories.through)
def update_Categories_relation(sender, instance, action, pk_set, **kwargs):
    """
    A receiver for the 'Categories' field of a Mechanism. This will synchronize
    the Category objects when the Mechanism's Categories are modified.
    """
    sync_bidirectional_relation(
        instance=instance,
        action=action,
        pk_set=pk_set,
        related_model=Category,
        related_field_name='mechanisms',
        **kwargs
    )