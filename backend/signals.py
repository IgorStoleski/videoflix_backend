from django.dispatch import receiver
from .models import Video
from django.db.models.signals import post_save, post_delete
import os
from backend.tasks import convert_360p, convert_720p, convert_1080p, generate_thumbnail, save_thumbnail_to_model
import django_rq

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """
    Signal handler that processes a video after it has been saved to the database.

    This function is triggered after a `Video` instance is saved. If the `Video` instance
    is newly created (`created=True`), it performs several operations:
    1. Generates and logs the creation of a new video.
    2. Creates a thumbnail for the video.
    3. Enqueues several tasks to convert the video into different resolutions (360p, 720p, 1080p).

    :param sender: The model class that just had an instance saved.
    :param instance: The actual instance of the model that was saved.
    :param created: A boolean indicating whether this is a new instance or an update.
    :param kwargs: A dictionary containing any additional keyword arguments.
    """
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