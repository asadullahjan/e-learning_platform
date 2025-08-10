import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import CourseContent from "./course-content";
import CourseEnrollments from "./course-enrollments";
import { Course } from "@/lib/types";
import { Button } from "@/components/ui/button";

interface CourseTabsProps {
  course: Course;
  isTeacher: boolean;
  isCourseOwner: boolean;
}

const CourseTabs = ({ course, isTeacher, isCourseOwner }: CourseTabsProps) => {
  const scrollToTab = (tabValue: string) => {
    const tab = document.querySelector(`[data-value="${tabValue}"]`) as HTMLElement;
    if (tab) {
      tab.click();
      tab.scrollIntoView({ behavior: 'smooth' });
    }
  };

  if (isTeacher && isCourseOwner) {
    // Teacher view - show management tabs
    return (
      <Tabs defaultValue="overview">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="students">Students</TabsTrigger>
          <TabsTrigger value="content">Content</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>
        
        <TabsContent value="overview">
          <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white p-4 rounded-lg border">
                <h3 className="font-medium text-gray-900">Total Students</h3>
                <p className="text-2xl font-bold text-primary">{course.total_enrollments || 0}</p>
              </div>
              <div className="bg-white p-4 rounded-lg border">
                <h3 className="font-medium text-gray-900">Active Students</h3>
                <p className="text-2xl font-bold text-green-600">{course.enrollment_count || 0}</p>
              </div>
              <div className="bg-white p-4 rounded-lg border">
                <h3 className="font-medium text-gray-900">Status</h3>
                <p className="text-2xl font-bold text-blue-600">
                  {course.published_at ? "Published" : "Draft"}
                </p>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white p-6 rounded-lg border">
              <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
              <div className="flex flex-wrap gap-3">
                <Button
                  variant="outline"
                  onClick={() => scrollToTab("students")}
                >
                  Manage Students
                </Button>
                <Button
                  variant="outline"
                  onClick={() => scrollToTab("content")}
                >
                  Edit Content
                </Button>
                <Button
                  variant="outline"
                  onClick={() => scrollToTab("settings")}
                >
                  Course Settings
                </Button>
              </div>
            </div>

            {/* Recent Activity Placeholder */}
            <div className="bg-white p-6 rounded-lg border">
              <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
              <p className="text-gray-500">Recent student enrollments and activity will appear here.</p>
            </div>
          </div>
        </TabsContent>
        
        <TabsContent value="students">
          <CourseEnrollments courseId={course.id} />
        </TabsContent>
        
        <TabsContent value="content">
          <CourseContent course={course} />
        </TabsContent>
        
        <TabsContent value="settings">
          <div className="bg-white p-6 rounded-lg border">
            <h3 className="text-lg font-semibold mb-4">Course Settings</h3>
            <p className="text-gray-500">Course management settings will go here.</p>
          </div>
        </TabsContent>
      </Tabs>
    );
  }

  // Student view - show content and enrollment status
  return (
    <Tabs defaultValue="content">
      <TabsList>
        <TabsTrigger value="content">Content</TabsTrigger>
        <TabsTrigger value="progress">Progress</TabsTrigger>
      </TabsList>
      
      <TabsContent value="content">
        <CourseContent course={course} />
      </TabsContent>
      
      <TabsContent value="progress">
        <div className="bg-white p-6 rounded-lg border">
          <h3 className="text-lg font-semibold mb-4">Your Progress</h3>
          <p className="text-gray-500">Progress tracking will be implemented here.</p>
        </div>
      </TabsContent>
    </Tabs>
  );
};

export default CourseTabs;
