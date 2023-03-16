"""
Eox-nelp djangoapp receivers to manage django signals
"""
from completion.models import BlockCompletion
from django.db import models
from django.dispatch import receiver


@receiver(models.signals.post_save, sender=BlockCompletion)
def send_completion_progress_2_futurex(**kwargs):
    instance = kwargs['instance']
    course_id = str(instance.context_key)
    block_id = str(instance.block_key)
    user_id = instance.user_id
    breakpoint()
    pass
#
