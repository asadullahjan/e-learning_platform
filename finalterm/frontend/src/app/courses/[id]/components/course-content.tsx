import { Card, CardContent } from "@/components/ui/card";
import { Course } from "@/lib/types";

const CourseContent = ({ course }: { course: Course }) => {
  return (
    <Card>
      <CardContent>Course content will be Here</CardContent>
    </Card>
  );
};

export default CourseContent;
