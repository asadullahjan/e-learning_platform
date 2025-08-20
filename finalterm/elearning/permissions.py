from rest_framework.permissions import BasePermission


class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "teacher"


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "student"


class IsCourseOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Only the course creator can edit/delete
        return obj.teacher == request.user


class IsCourseOwnerOrEnrollmentOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Course owner can view enrollments for their course
        if obj.course.teacher == request.user:
            return True
        # User can view their own enrollment
        if obj.user == request.user:
            return True
        return False
