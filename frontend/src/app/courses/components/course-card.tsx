import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import Typography from "@/components/ui/Typography";
import { Course } from "@/lib/types";
import { Calendar, User, BookOpen } from "lucide-react";
import Link from "next/link";

export default function CourseCard({ course }: { course: Course }) {
  // Format the published date
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  return (
    <Link
      href={`/courses/${course.id}`}
      className="block"
    >
      <Card className="hover:shadow-lg transition-shadow duration-200 cursor-pointer flex flex-col h-full">
        <CardHeader className="pb-3">
          <Typography
            variant="h3"
            size="lg"
            className="text-gray-900 line-clamp-2"
          >
            {course.title}
          </Typography>
        </CardHeader>
        <CardContent className="pt-0 flex flex-col flex-grow">
          <div className="space-y-4 flex flex-col flex-grow">
            {/* Description */}
            <Typography
              variant="p"
              size="sm"
              className="text-gray-600 line-clamp-3 leading-relaxed flex-grow"
            >
              {course.description}
            </Typography>

            {/* Course metadata */}
            <div className="flex items-center justify-between text-xs text-gray-500">
              <div className="flex items-center gap-1">
                <User className="w-3 h-3" />
                <Link href={`/users/${course.teacher.username}`}>
                  <Typography
                    variant="span"
                    size="xs"
                    className="font-medium hover:text-primary transition-colors cursor-pointer"
                  >
                    {course.teacher.username}
                  </Typography>
                </Link>
              </div>
              <div className="flex items-center gap-1">
                <Calendar className="w-3 h-3" />
                <Typography
                  variant="span"
                  size="xs"
                >
                  {formatDate(course.published_at)}
                </Typography>
              </div>
            </div>

            {/* Action button - pushed to bottom */}
            <div className="pt-2 mt-auto">
              <div className="w-full bg-primary hover:bg-primary/90 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center gap-2">
                <BookOpen className="w-4 h-4" />
                <Typography
                  variant="span"
                  size="sm"
                  className="font-medium"
                >
                  View Course
                </Typography>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
