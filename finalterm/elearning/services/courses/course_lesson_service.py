from elearning.models import Course, CourseLesson, File, User


class CourseLessonService:
    @staticmethod
    def create_lesson_with_file(course: Course, lesson_data: dict, user: User):
        file_data = lesson_data.pop("file", None)
        lesson = CourseLesson.objects.create(
            course=course,
            title=lesson_data["title"],
            description=lesson_data["description"],
            content=lesson_data["content"],
        )

        if file_data:
            file = File.objects.create(
                file=file_data,
                original_name=file_data.name,
                uploaded_by=user,
            )
            lesson.file = file

        lesson.save()
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
                old_file.delete()

            # Create new file
            if file_data:
                new_file = File.objects.create(
                    file=file_data,
                    original_name=file_data.name,
                    uploaded_by=user,
                )
                lesson.file = new_file

        lesson.save()
        return lesson

    @staticmethod
    def delete_lesson_with_file(lesson: CourseLesson, user: User):
        """Delete lesson and associated file only if no other lessons use it"""
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

        # Delete the lesson
        lesson.delete()

    @staticmethod
    def toggle_lesson_publish_status(lesson: CourseLesson, published_at):
        """Toggle lesson publish status"""
        lesson.published_at = published_at
        lesson.save()
        return lesson
