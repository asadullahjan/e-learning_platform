# Clean Architecture for Student Restrictions

## Overview

This document outlines the clean architecture implemented for handling student restrictions in the eLearning platform. The architecture follows the principle of **single source of truth** and **separation of concerns**.

## Architecture Principles

### 1. **Single Source of Truth: Enrollment Status**
- **`enrollment.is_active`** determines access to course content
- Restricted students automatically have `enrollment.is_active = False`
- All other services check enrollment status instead of restrictions

### 2. **Clear Separation of Responsibilities**
- **Restriction Service**: Only handles restrictions and their effects
- **Enrollment Service**: Only place that checks restrictions (when creating/reactivating)
- **Other Services**: Only check enrollment status for access control

### 3. **No Circular Dependencies**
- Services don't import restriction service for access checking
- Policies don't check restrictions directly
- Clean dependency flow: Restrictions → Enrollments → Access Control

## Service Responsibilities

### CourseStudentRestrictionService
✅ **Handles:**
- Creating/deleting/modifying restrictions
- Applying restriction effects (deactivate enrollments & chat participants)
- Managing restriction lifecycle
- Getting restriction information

❌ **Does NOT handle:**
- Access checking for lessons, feedback, chat
- General permission validation

### CourseEnrollmentService
✅ **Handles:**
- Creating/reactivating enrollments
- **ONLY place that checks `is_restricted`** before enrollment operations
- Managing enrollment lifecycle
- Providing enrollment status checking methods

❌ **Does NOT handle:**
- Restriction creation/deletion
- Access control for other features

### Other Services (Lessons, Feedback, Chat)
✅ **Handles:**
- Their specific business logic
- Checking `enrollment.is_active` for access control

❌ **Does NOT handle:**
- Direct restriction checks
- Importing restriction service

## Access Control Flow

```
Student Restricted → Restriction Service → Deactivates Enrollment → 
All Services Check enrollment.is_active → Access Denied
```

### For Restricted Students:
- **Course**: Can see exists, description (like unenrolled users)
- **Lessons**: Can see list, titles, descriptions (like unenrolled users)
- **Feedback**: Can see list (like unenrolled users)
- **Chat**: Can see participants but cannot participate (enrollment inactive)
- **Enrollment**: Cannot create/reactivate (gets permission denied)

## Policy Classes

### Updated Policies:
- **CourseFeedbackPolicy**: Only checks enrollment status
- **CourseLessonPolicy**: Only checks enrollment status  
- **ChatParticipantPolicy**: Only checks enrollment status

### Key Changes:
- Removed direct restriction checks
- Added enrollment status validation
- Clear documentation about restriction handling

## Benefits of This Architecture

1. **No Circular Imports**: Clean dependency flow
2. **Single Source of Truth**: Enrollment status determines access
3. **Automatic Restriction Handling**: Restrictions automatically affect enrollments
4. **Consistent Access Control**: All services use same pattern
5. **Easy to Maintain**: Changes to restrictions only affect enrollment service
6. **Clear Separation**: Each service has single responsibility

## Example Usage

### Checking Course Access:
```python
# ✅ CORRECT: Check enrollment status
from elearning.services.courses.course_enrollment_service import CourseEnrollmentService

can_access = CourseEnrollmentService.is_student_enrolled_and_active(student, course)

# ❌ WRONG: Don't check restrictions directly in other services
# restriction_info = CourseStudentRestrictionService.get_restriction_info(student, course)
```

### Creating Enrollment:
```python
# ✅ CORRECT: Enrollment service handles restriction checks
enrollment = CourseEnrollmentService.enroll_student(course, student)
# This automatically checks restrictions and returns permission denied if restricted
```

## Migration Notes

- All existing restriction checks in other services have been removed
- Services now use enrollment status for access control
- Policies updated to reflect new architecture
- No breaking changes to public APIs
- Clear documentation added to all services and policies

## Testing

- Test that restricted students cannot create/reactivate enrollments
- Test that restricted students see same access as unenrolled users
- Test that restriction effects automatically deactivate enrollments
- Test that all services properly check enrollment status
