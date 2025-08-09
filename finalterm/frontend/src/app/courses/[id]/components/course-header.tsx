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
    <Card className="mb-8">
      <CardHeader className="pb-4">
        <h1 className="text-3xl font-bold text-gray-900">{course.title}</h1>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Description */}
        <p className="text-gray-600 text-lg leading-relaxed">{course.description}</p>

        {/* Action Button */}
        <CourseActions
          isTeacher={isTeacher}
          isCourseOwner={isCourseOwner}
          courseId={course.id}
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
    </Card>
  );
};

export default CourseHeader;
