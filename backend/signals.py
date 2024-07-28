from django.dispatch import receiver
from .models import Video
from django.db.models.signals import post_save, post_delete
import os
from backend.tasks import convert_360p, convert_720p, convert_1080p, generate_thumbnail, save_thumbnail_to_model
import django_rq

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created:
        print(f"New video created: {instance.id}")
        video_file_path = instance.video_file.path
        thumbnail_file = video_file_path.replace('.mp4', '_thumbnail.png')
        generated_thumbnail = generate_thumbnail(video_file_path, thumbnail_file)
        if generated_thumbnail:
            save_thumbnail_to_model(instance.id, generated_thumbnail)
        queue = django_rq.get_queue('default', autocommit=True)
        queue.enqueue(convert_360p, instance.video_file.path, instance.id)
        queue.enqueue(convert_720p, instance.video_file.path, instance.id)
        queue.enqueue(convert_1080p, instance.video_file.path, instance.id)

@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `Video` object is deleted.
    """
    if instance.video_file:
        if os.path.isfile(instance.video_file.path):
            os.remove(instance.video_file.path)