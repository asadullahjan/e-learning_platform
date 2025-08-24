from elearning.models import Course, CourseLesson, File, User
from elearning.services.notification_service import NotificationService


class CourseLessonService:
    @staticmethod
    def create_lesson_with_file(course: Course, lesson_data: dict, user: User):
        file_data = lesson_data.pop("file", None)
        lesson = CourseLesson.objects.create(
            course=course,
            title=lesson_data["title"],
            description=lesson_data["description"],
            content=lesson_data.get("content", ""),
        )

        if file_data:
            file = File.objects.create(
                file=file_data,
                original_name=file_data.name,
                uploaded_by=user,
            )
            lesson.file = file

        lesson.save()

        # Notify enrolled students about new lesson
        enrolled_user_ids = [
            enrollment.user.id
            for enrollment in course.enrollment_set.filter(is_active=True)
        ]

        NotificationService.create_notifications_and_send(
            user_ids=enrolled_user_ids,
            title="New Lesson Available",
            message=f"Check out the new lesson: {lesson.title}",
            action_url=f"/courses/{course.id}/lessons/{lesson.id}",
        )

        return lesson

    @staticmethod
    def update_lesson_with_file(
        lesson: CourseLesson, lesson_data: dict, user: User
    ):
        """Update lesson and optionally update/replace file"""
        # Update basic fields
        if "title" in lesson_data:
            lesson.title = lesson_data["title"]
        if "description" in lesson_data:
            lesson.description = lesson_data["description"]
        if "content" in lesson_data:
            lesson.content = lesson_data["content"]

        # Handle file update if provided
        if "file" in lesson_data:
            file_data = lesson_data["file"]

            # Delete old file if it exists
            if lesson.file:
                old_file = lesson.file
                lesson.file = None
                lesson.save()

                # Check if other lessons use this file before deleting
                other_lessons_using_file = (
                    CourseLesson.objects.filter(file=old_file)
                    .exclude(id=lesson.id)
                    .exists()
                )

                # Only delete if no other lessons use it
                if not other_lessons_using_file:
                    old_file.delete()  # This will trigger the signal

            # Create new file
            if file_data:
                new_file = File.objects.create(
                    file=file_data,
                    original_name=file_data.name,
                    uploaded_by=user,
                )
                lesson.file = new_file

        lesson.save()
        
        # Notify enrolled students about lesson update
        enrolled_user_ids = [
            enrollment.user.id 
            for enrollment in lesson.course.enrollment_set.filter(is_active=True)
        ]
        
        NotificationService.create_notifications_and_send(
            user_ids=enrolled_user_ids,
            title="Lesson Updated",
            message=(
                f"The lesson '{lesson.title}' has been updated"
            ),
            action_url=(
                f"/courses/{lesson.course.id}/lessons/{lesson.id}"
            )
        )
        
        return lesson

    @staticmethod
    def delete_lesson_with_file(lesson: CourseLesson, user: User):
        """Delete lesson and associated file only if no other lessons use it"""
        # Store lesson info before deletion for notification
        lesson_title = lesson.title
        course_id = lesson.course.id
        
        # Check if other lessons use this file
        if lesson.file:
            file_to_check = lesson.file
            other_lessons_using_file = (
                CourseLesson.objects.filter(file=file_to_check)
                .exclude(id=lesson.id)
                .exists()
            )

            # Only delete file if no other lessons use it
            if not other_lessons_using_file:
                file_to_check.delete()

        # Notify enrolled students about lesson deletion
        enrolled_user_ids = [
            enrollment.user.id 
            for enrollment in lesson.course.enrollment_set.filter(is_active=True)
        ]
        
        NotificationService.create_notifications_and_send(
            user_ids=enrolled_user_ids,
            title="Lesson Removed",
            message=f"The lesson '{lesson_title}' has been removed from the course",
            action_url=f"/courses/{course_id}"
        )

        # Delete the lesson
        lesson.delete()

    @staticmethod
    def toggle_lesson_publish_status(lesson: CourseLesson, published_at):
        """Toggle lesson publish status"""
        lesson.published_at = published_at
        lesson.save()
        
        # Notify enrolled students about lesson status change
        enrolled_user_ids = [
            enrollment.user.id 
            for enrollment in lesson.course.enrollment_set.filter(is_active=True)
        ]
        
        if published_at:
            # Lesson was published
            title = "Lesson Published"
            message = f"The lesson '{lesson.title}' is now available"
            action_url = f"/courses/{lesson.course.id}/lessons/{lesson.id}"
        else:
            # Lesson was unpublished
            title = "Lesson Unpublished"
            message = f"The lesson '{lesson.title}' is no longer available"
            action_url = f"/courses/{lesson.course.id}"
        
        NotificationService.create_notifications_and_send(
            user_ids=enrolled_user_ids,
            title=title,
            message=message,
            action_url=action_url
        )
        
        return lesson
