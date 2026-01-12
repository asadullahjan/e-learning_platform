import UserAvatar from "@/components/user/user-avatar";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Course } from "@/lib/types";
import CourseActions from "./course-actions";
import Typography from "@/components/ui/Typography";

type CourseHeaderProps = {
  course: Course;
  isTeacher: boolean;
  isCourseOwner: boolean;
};

const CourseHeader = ({ course, isTeacher, isCourseOwner }: CourseHeaderProps) => {
  return (
    <Card className="mb-20 pb-10 relative overflow-visible">
      <CardHeader className="pb-4">
        <Typography
          variant="h1"
          size="lg"
          className="text-gray-900"
        >
          {course.title}
        </Typography>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Description */}
        <Typography
          variant="p"
          size="md"
          className="text-gray-600 leading-relaxed"
        >
          {course.description}
        </Typography>

        {/* Action Button */}
        <CourseActions
          isTeacher={isTeacher}
          isCourseOwner={isCourseOwner}
          courseId={course.id}
          isEnrolled={course.is_enrolled}
          course={course}
        />

        {/* Teacher Info */}
        <div className="flex flex-col gap-4 pt-4 border-t border-gray-200">
          <UserAvatar
            user={course.teacher}
            size="lg"
            showName={true}
            clickable={true}
          />
        </div>
      </CardContent>

      {/* Floating Stats Card - Absolute positioned at bottom center */}
      <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-1/2 z-1">
        <Card className="shadow border-0 bg-white">
          <CardContent className="px-8 py-4">
            <div className="flex gap-12">
              <div className="flex flex-col items-center">
                <Typography
                  variant="h2"
                  size="lg"
                  className="text-blue-600"
                >
                  {course.enrollment_count}
                </Typography>
                <Typography
                  variant="p"
                  size="sm"
                  className="text-gray-600 font-medium"
                >
                  Active Students
                </Typography>
              </div>
              <div className="flex flex-col items-center">
                <Typography
                  variant="h2"
                  size="lg"
                  className="text-green-600"
                >
                  {course.total_enrollments}
                </Typography>
                <Typography
                  variant="p"
                  size="sm"
                  className="text-gray-600 font-medium"
                >
                  Total Enrollments
                </Typography>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </Card>
  );
};

export default CourseHeader;
