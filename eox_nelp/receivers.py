"""
Eox-nelp djangoapp receivers to manage django signals
"""
from completion.models import BlockCompletion
from django.db import models
from django.dispatch import receiver
from lms.djangoapps.courseware.courses import get_course_blocks_completion_summary
@receiver(models.signals.post_save, sender=BlockCompletion)
def send_completion_progress_2_futurex(**kwargs):
    instance = kwargs['instance']
    course_key = instance.context_key #  course_id not need to be in string way, course locator
    block_id = str(instance.block_key)
    user_id = instance.user_id
    user = instance.user
    breakpoint()
    completion_summary = get_course_blocks_completion_summary.__wrapped__(course_key, user)
    pass
#
