from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Course
from mechanisms.models import Mechanism
from experts.models import Expert
from builds.models import Build
from categories.models import Category
from core.signals import sync_bidirectional_relation

@receiver(m2m_changed, sender=Course.mechanisms.through)
def update_mechanisms_relation(sender, instance, action, pk_set, **kwargs):
    """
    A receiver for the 'mechanisms' field of a Course. This will synchronize
    the mechanism objects when the Course's mechanisms are modified.
    """
    sync_bidirectional_relation(
        instance=instance,
        action=action,
        pk_set=pk_set,
        related_model=Mechanism,
        related_field_name='courses',
        **kwargs
    )
@receiver(m2m_changed, sender=Course.experts.through)
def update_experts_relation(sender, instance, action, pk_set, **kwargs):
    """
    A receiver for the 'experts' field of a Course. This will synchronize
    the expert objects when the Course's experts are modified.
    """
    sync_bidirectional_relation(
        instance=instance,
        action=action,
        pk_set=pk_set,
        related_model=Expert,
        related_field_name='courses',
        **kwargs
    )
@receiver(m2m_changed, sender=Course.builds.through)
def update_builds_relation(sender, instance, action, pk_set, **kwargs):
    """
    A receiver for the 'builds' field of a Course. This will synchronize
    the build objects when the Course's builds are modified.
    """
    sync_bidirectional_relation(
        instance=instance,
        action=action,
        pk_set=pk_set,
        related_model=Build,
        related_field_name='courses',
        **kwargs
    )
@receiver(m2m_changed, sender=Course.categories.through)
def update_categories_relation(sender, instance, action, pk_set, **kwargs):
    """
    A receiver for the 'categories' field of a Course. This will synchronize
    the category objects when the Course's categories are modified.
    """
    sync_bidirectional_relation(
        instance=instance,
        action=action,
        pk_set=pk_set,
        related_model=Category,
        related_field_name='courses',
        **kwargs
    )