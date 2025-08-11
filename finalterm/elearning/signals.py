from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Enrollment, ChatRoom, ChatParticipant


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
