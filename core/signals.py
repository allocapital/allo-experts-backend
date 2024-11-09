import threading
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.db import transaction

# Create a local flag to store if the signal is being processed
_thread_locals = threading.local()

def sync_bidirectional_relation(instance, action, pk_set, related_model, related_field_name, **kwargs):
    """
    A generic function to synchronize bidirectional many-to-many relations
    without causing infinite recursion by using a thread-local flag.
    """
    if action not in ["post_add", "post_remove"]:
        return

    # Check if the signal is already being processed in the same thread
    if getattr(_thread_locals, 'signal_processing', False):
        return  # If True, skip the processing to prevent recursion

    # Set the flag to True indicating we are processing the signal in this thread
    _thread_locals.signal_processing = True

    try:
        # Wrap the signal handler code in a transaction block
        with transaction.atomic():
            for obj_id in pk_set:
                try:
                    related_obj = related_model.objects.get(pk=obj_id)
                except related_model.DoesNotExist:
                    print(f"Warning: {related_model.__name__} with ID {obj_id} does not exist.")
                    continue 

                related_field = getattr(related_obj, related_field_name)
                if action == "post_add":
                    related_field.add(instance)
                elif action == "post_remove":
                    related_field.remove(instance)
    except Exception as e:
        print(f"An error occurred: {e}")
        raise  # Re-raise the exception to ensure the transaction is rolled back
    finally:
        _thread_locals.signal_processing = False
