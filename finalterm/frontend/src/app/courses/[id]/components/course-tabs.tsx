import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import CourseEnrollments from "./course-enrollments";
import { Course } from "@/lib/types";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import Typography from "@/components/ui/Typography";
import { LessonList } from "./lesson-list";
import FeedbackSection from "./feedback-section";
import RestrictionsSection from "./restrictions-section";
import { enrollmentService } from "@/services/enrollmentService";
import CourseChat from "./course-chat";

interface CourseTabsProps {
  course: Course;
  isTeacher: boolean;
  isCourseOwner: boolean;
  isEnrolled: boolean;
  defaultTab?: string;
}

interface TabConfig {
  value: string;
  label: string;
  content: React.ReactNode;
}

const CourseTabs = async ({
  course,
  isTeacher,
  isCourseOwner,
  isEnrolled,
  defaultTab,
}: CourseTabsProps) => {
  // Fetch enrollments data for teacher view
  let enrollments: any[] = [];
  if (isTeacher && isCourseOwner) {
    try {
      enrollments = await enrollmentService.server.getCourseEnrollments(course.id, {
        status: "all", // Show all enrollments initially
      });
    } catch (error) {
      console.error("Failed to fetch enrollments:", error);
    }
  }

  // Tab configurations to eliminate repetition
  const teacherTabs: TabConfig[] = [
    {
      value: "overview",
      label: "Overview",
      content: (
        <div className="space-y-6">
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardContent className="p-4">
                <Typography
                  variant="p"
                  className="font-medium text-gray-900"
                >
                  Total Students
                </Typography>
                <Typography
                  variant="h2"
                  size="lg"
                  className="text-primary"
                >
                  {course.total_enrollments || 0}
                </Typography>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <Typography
                  variant="p"
                  className="font-medium text-gray-900"
                >
                  Active Students
                </Typography>
                <Typography
                  variant="h2"
                  size="lg"
                  className="text-green-600"
                >
                  {course.enrollment_count || 0}
                </Typography>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <Typography
                  variant="p"
                  className="font-medium text-gray-900"
                >
                  Status
                </Typography>
                <Typography
                  variant="h2"
                  size="lg"
                  className="text-blue-600"
                >
                  {course.published_at ? "Published" : "Draft"}
                </Typography>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity Placeholder */}
          <Card>
            <CardHeader>
              <Typography
                variant="h3"
                size="md"
              >
                Recent Activity
              </Typography>
            </CardHeader>
            <CardContent>
              <Typography
                variant="p"
                color="muted"
              >
                Recent course activity will be displayed here.
              </Typography>
            </CardContent>
          </Card>
        </div>
      ),
    },
    {
      value: "enrollments",
      label: "Enrollments",
      content: (
        <CourseEnrollments
          courseId={course.id}
          isTeacher={true}
          enrollments={enrollments}
        />
      ),
    },
    {
      value: "feedback",
      label: "Feedback",
      content: (
        <FeedbackSection
          courseId={course.id}
          isEnrolled={isEnrolled}
        />
      ),
    },
    {
      value: "restrictions",
      label: "Restrictions",
      content: (
        <RestrictionsSection
          courseId={course.id}
          courseTitle={course.title}
        />
      ),
    },
    {
      value: "lessons",
      label: "Lessons",
      content: (
        <LessonList
          courseId={course.id}
          isTeacher={true}
        />
      ),
    },
  ];

  const studentTabs: TabConfig[] = [
    {
      value: "content",
      label: "Content",
      content: (
        <LessonList
          courseId={course.id}
          isTeacher={false}
        />
      ),
    },
    {
      value: "feedback",
      label: "Feedback",
      content: (
        <FeedbackSection
          courseId={course.id}
          isEnrolled={isEnrolled}
        />
      ),
    },
    ...(course.course_chat_id
      ? [
          {
            value: "chat",
            label: "Chat",
            content: <CourseChat chatId={course.course_chat_id || ""} />,
          },
        ]
      : []),
  ];

  // Reusable function to render tabs - eliminates repetition
  const renderTabs = (tabs: TabConfig[], defaultValue: string) => (
    <Tabs defaultValue={defaultValue}>
      <TabsList className="transition-all duration-200">
        {tabs.map((tab) => (
          <TabsTrigger
            key={tab.value}
            value={tab.value}
          >
            {tab.label}
          </TabsTrigger>
        ))}
      </TabsList>

      {tabs.map((tab) => (
        <TabsContent
          key={tab.value}
          value={tab.value}
        >
          {tab.content}
        </TabsContent>
      ))}
    </Tabs>
  );

  if (isTeacher && isCourseOwner) {
    return renderTabs(teacherTabs, defaultTab || "overview");
  }

  return renderTabs(studentTabs, defaultTab || "content");
};

export default CourseTabs;
