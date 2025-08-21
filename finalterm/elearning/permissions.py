from rest_framework.permissions import BasePermission


class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "teacher"


class IsTeacherOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == "teacher" or request.user.is_superuser
        )


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


class StudentRestrictionPermission(BasePermission):
    """
    Permission class for student restrictions.
    Only teachers can create/delete restrictions.
    Teachers can only manage their own restrictions.
    """
    
    def has_permission(self, request, view):
        # Must be authenticated and a teacher
        if not request.user.is_authenticated:
            return False
        
        if request.user.role != "teacher":
            return False
        
        return True
    
    def has_object_permission(self, request, view, obj):
        # Teachers can only manage their own restrictions
        return obj.teacher == request.user
