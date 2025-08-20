from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.core.files.storage import default_storage
from .models import Enrollment, ChatRoom, ChatParticipant, File


@receiver(post_save, sender=Enrollment)
def sync_user_course_chat(sender, instance, created, **kwargs):
    """Add/remove user in course chatroom based on enrollment status."""
    try:
        chatroom = ChatRoom.objects.get(
            course=instance.course, chat_type="course"
        )
    except ChatRoom.DoesNotExist:
        return

    if instance.is_active:
        ChatParticipant.objects.get_or_create(
            chat_room=chatroom,
            user=instance.user,
            defaults={"role": "participant"},
        )
    else:
        ChatParticipant.objects.filter(
            chat_room=chatroom, user=instance.user
        ).delete()


@receiver(pre_delete, sender=File)
def delete_file_on_model_delete(sender, instance, **kwargs):
    """
    Automatically delete the physical file when the File model is deleted.
    This ensures no orphaned files remain on disk.
    """
    if instance.file:
        try:
            # Delete the physical file using Django's storage backend
            default_storage.delete(instance.file.name)
        except Exception as e:
            print(f"Error deleting file {instance.file.name}: {e}")
            pass
