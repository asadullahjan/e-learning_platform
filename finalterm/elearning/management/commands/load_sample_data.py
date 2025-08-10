from datetime import datetime
from django.core.management.base import BaseCommand
from ...models import Course, User


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Create teachers
        teacher1 = User.objects.create_user(
            username="john_teacher",
            email="john@example.com",
            password="password123",
            role="teacher",
            first_name="John",
            last_name="Smith",
        )

        teacher2 = User.objects.create_user(
            username="sarah_teacher",
            email="sarah@example.com",
            password="password123",
            role="teacher",
            first_name="Sarah",
            last_name="Johnson",
        )

        # Create students
        student1 = User.objects.create_user(
            username="alice_student",
            email="alice@example.com",
            password="password123",
            role="student",
            first_name="Alice",
            last_name="Brown",
        )

        student2 = User.objects.create_user(
            username="bob_student",
            email="bob@example.com",
            password="password123",
            role="student",
            first_name="Bob",
            last_name="Wilson",
        )

        # Create courses with proper descriptions
        courses_data = [
            {
                "title": "Introduction to React Development",
                "description": (
                    "Learn the fundamentals of React including components, "
                    "state, props, and hooks. Perfect for beginners starting "
                    "their web development journey."
                ),
                "teacher": teacher1,
                "published_at": datetime.now(),
            },
            {
                "title": "Advanced Python Programming",
                "description": (
                    "Master advanced Python concepts including decorators, "
                    "generators, async programming, and design patterns."
                ),
                "teacher": teacher1,
                "published_at": datetime.now(),
            },
            {
                "title": "UI/UX Design Fundamentals",
                "description": (
                    "Create beautiful and functional user interfaces. "
                    "Learn design principles, wireframing, "
                    "and prototyping techniques."
                ),
                "teacher": teacher2,
                "published_at": datetime.now(),
            },
            {
                "title": "Digital Marketing Strategy",
                "description": (
                    "Develop comprehensive digital marketing "
                    "strategies including SEO, social media, "
                    "and content marketing."
                ),
                "teacher": teacher2,
                "published_at": datetime.now(),
            },
        ]

        courses = []
        for course_data in courses_data:
            course = Course.objects.create(**course_data)
            courses.append(course)
