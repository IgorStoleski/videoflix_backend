from django.dispatch import receiver
from .models import Video
from django.db.models.signals import post_save, post_delete
import os
from backend.tasks import convert_480p
import django_rq
from django_rq import enqueue

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    print('Video object has been saved')
    if created:
        print('New video object has been created')
        queue = django_rq.get_queue('default', autocommit=True)
        queue.enqueue(convert_480p, instance.video_file.path)
        print('Video has been converted to 480p')
        

@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `Video` object is deleted.
    """
    if instance.video_file:
        if os.path.isfile(instance.video_file.path):
            os.remove(instance.video_file.path)