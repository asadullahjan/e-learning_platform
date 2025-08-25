"""
Lesson access and download permissions.

This module contains permission classes that control access to course lessons
and lesson file downloads based on user enrollment and course ownership.
"""

from rest_framework.permissions import BasePermission


class LessonDownloadPermission(BasePermission):
    """
    Permission class for lesson file downloads.
    
    Allows:
    - Teachers to download files from their own courses
    - Students to download files from published lessons in courses 
      they're enrolled in
    """
    
    def has_object_permission(self, request, view, obj):
        """Check if user can download lesson files"""
        # Teachers can download files from their own courses
        if obj.course.teacher == request.user:
            return True
        
        # Students can download files from published lessons in courses 
        # they're enrolled in
        if (obj.published_at and 
                request.user.enrollments.filter(
                    course=obj.course, is_active=True
                ).exists()):
            return True
        
        return False


class IsEnrolledInCourse(BasePermission):
    """
    Permission class for viewing lessons.
    
    Allows:
    - Course owners (teachers) to view all lessons
    - Enrolled students to view published lessons
    """
    
    def has_permission(self, request, view):
        """Check if user has permission to view lessons"""
        course_id = view.kwargs.get("course_pk")
        if not course_id:
            return False
        
        try:
            course = (view.get_queryset().first().course 
                      if view.get_queryset() else None)
            if not course:
                return False
                
            if course.teacher == request.user:
                return True
            if request.user.enrollments.filter(
                course=course, is_active=True
            ).exists():
                return True
            return False
        except AttributeError:
            return False
