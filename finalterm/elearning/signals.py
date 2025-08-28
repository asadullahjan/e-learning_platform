from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver
from django.core.files.storage import default_storage
from .models import (
    Enrollment,
    ChatRoom,
    ChatParticipant,
    File,
    StudentRestriction,
)


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
        # Check if user is restricted before adding to course chat
        from elearning.services.courses.student_restriction_service import (
            StudentRestrictionService,
        )

        restriction_info = StudentRestrictionService.get_restriction_info(
            instance.user, instance.course
        )

        # Only add to chat if not restricted
        if not restriction_info["is_restricted"]:
            # Use get_or_create with soft deletion handling
            participant, created = ChatParticipant.objects.get_or_create(
                chat_room=chatroom,
                user=instance.user,
                defaults={"role": "participant", "is_active": True},
            )
            # If participant exists but is inactive, reactivate them
            if not created and not participant.is_active:
                participant.is_active = True
                participant.save(update_fields=["is_active"])
    else:
        # Soft delete: set is_active to False instead of hard delete
        ChatParticipant.objects.filter(
            chat_room=chatroom, user=instance.user, is_active=True
        ).update(is_active=False)


@receiver(post_save, sender=StudentRestriction)
def apply_restriction_effects(sender, instance, created, **kwargs):
    """Apply restriction effects when a new restriction is created."""
    if not created:
        return

    # Apply restriction effects using the service
    from elearning.services.courses.student_restriction_service import (
        StudentRestrictionService,
    )

    StudentRestrictionService._apply_restriction_effects(instance)


@receiver(post_delete, sender=StudentRestriction)
def remove_restriction_effects(sender, instance, **kwargs):
    """Remove restriction effects when a restriction is deleted."""
    # Remove restriction effects using the service
    from elearning.services.courses.student_restriction_service import (
        StudentRestrictionService,
    )

    StudentRestrictionService._remove_restriction_effects(instance)


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
