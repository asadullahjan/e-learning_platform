import { enrollmentService, TeacherEnrollment } from "@/services/enrollmentService";
import { Card, CardContent } from "@/components/ui/card";
import Avatar from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import Input from "@/components/ui/Input";
import Typography from "@/components/ui/Typography";
import { showToast } from "@/lib/toast";

interface CourseEnrollmentsProps {
  courseId: string;
  isTeacher: boolean;
}

const CourseEnrollments = async ({ courseId, isTeacher }: CourseEnrollmentsProps) => {
  const handleDeactivateEnrollment = async (enrollmentId: string) => {
    try {
      await enrollmentService.deactivateEnrollment(enrollmentId);
      // Note: In server component, we'll need to handle this differently
      // For now, this is a placeholder
    } catch (error) {
      console.error("Failed to remove student:", error);
    }
  };

  try {
    const enrollments: TeacherEnrollment[] = await enrollmentService.server.getCourseEnrollments(
      courseId
    );

    if (!enrollments || enrollments.length === 0) {
      return (
        <Card>
          <CardContent className="p-6 text-center text-gray-500">
            <Typography variant="p">No students enrolled yet.</Typography>
          </CardContent>
        </Card>
      );
    }

    const activeEnrollments = enrollments.filter((e) => e.is_active);
    const inactiveEnrollments = enrollments.filter((e) => !e.is_active);

    return (
      <div className="space-y-6">
        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardContent className="p-4">
              <Typography variant="p" className="font-medium text-gray-900">
                Total Enrolled
              </Typography>
              <Typography variant="h2" size="lg" className="text-blue-600">
                {enrollments.length}
              </Typography>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <Typography variant="p" className="font-medium text-gray-900">
                Active Students
              </Typography>
              <Typography variant="h2" size="lg" className="text-green-600">
                {activeEnrollments.length}
              </Typography>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <Typography variant="p" className="font-medium text-gray-900">
                Inactive Students
              </Typography>
              <Typography variant="h2" size="lg" className="text-gray-600">
                {inactiveEnrollments.length}
              </Typography>
            </CardContent>
          </Card>
        </div>

        {/* Search and Filter */}
        <Card>
          <CardContent className="p-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <Input
                  type="text"
                  placeholder="Search students by name or email..."
                  className="w-full"
                />
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  className="transition-all duration-200"
                >
                  All Students
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="transition-all duration-200"
                >
                  Active Only
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="transition-all duration-200"
                >
                  Inactive Only
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Active Students */}
        <div>
          <Typography variant="h3" size="md" className="mb-4">
            Active Students ({activeEnrollments.length})
          </Typography>
          <div className="grid gap-4">
            {activeEnrollments.map((enrollment) => (
              <Card key={enrollment.id}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Avatar
                        src={enrollment.user.profile_picture}
                        alt={enrollment.user.username}
                        size="md"
                        fallback={
                          <div className="h-full w-full bg-primary text-primary-foreground flex items-center justify-center text-sm font-medium rounded-full">
                            {enrollment.user.username.charAt(0).toUpperCase()}
                          </div>
                        }
                      />

                      <div>
                        <Typography variant="h4" size="sm" className="text-gray-900">
                          {enrollment.user.username}
                        </Typography>
                        <Typography variant="p" size="sm" className="text-gray-500">
                          {enrollment.user.email}
                        </Typography>
                        <Typography variant="p" size="xs" className="text-gray-400">
                          Role: {enrollment.user.role}
                        </Typography>
                      </div>
                    </div>

                    <div className="text-right space-y-2">
                      <Typography variant="span" size="xs" className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        Active
                      </Typography>
                      <Typography variant="p" size="xs" className="text-gray-500">
                        Enrolled: {new Date(enrollment.enrolled_at).toLocaleDateString()}
                      </Typography>
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          className="transition-all duration-200"
                        >
                          View Profile
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="transition-all duration-200"
                        >
                          Message
                        </Button>
                        {isTeacher && (
                          <Button
                            size="sm"
                            variant="destructive"
                            className="transition-all duration-200 hover:bg-red-700"
                          >
                            Delete
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Inactive Students (if any) */}
        {inactiveEnrollments.length > 0 && (
          <div>
            <Typography variant="h3" size="md" className="mb-4">
              Inactive Students ({inactiveEnrollments.length})
            </Typography>
            <div className="grid gap-4">
              {inactiveEnrollments.map((enrollment) => (
                <Card key={enrollment.id} className="opacity-75">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <Avatar
                          src={enrollment.user.profile_picture}
                          alt={enrollment.user.username}
                          size="md"
                          fallback={
                            <div className="h-full w-full bg-gray-400 text-white flex items-center justify-center text-sm font-medium rounded-full">
                              {enrollment.user.username.charAt(0).toUpperCase()}
                            </div>
                          }
                        />

                        <div>
                          <Typography variant="h4" size="sm" className="text-gray-700">
                            {enrollment.user.username}
                          </Typography>
                          <Typography variant="p" size="sm" className="text-gray-500">
                            {enrollment.user.email}
                          </Typography>
                          <Typography variant="p" size="xs" className="text-gray-400">
                            Role: {enrollment.user.role}
                          </Typography>
                        </div>
                      </div>

                      <div className="text-right space-y-2">
                        <Typography variant="span" size="xs" className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                          Inactive
                        </Typography>
                        <Typography variant="p" size="xs" className="text-gray-500">
                          Enrolled: {new Date(enrollment.enrolled_at).toLocaleDateString()}
                        </Typography>
                        {enrollment.unenrolled_at && (
                          <Typography variant="p" size="xs" className="text-gray-500">
                            Unenrolled: {new Date(enrollment.unenrolled_at).toLocaleDateString()}
                          </Typography>
                        )}
                        <Button
                          size="sm"
                          variant="outline"
                          className="transition-all duration-200"
                        >
                          Reactivate
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  } catch (error) {
    console.error("Error fetching enrollments:", error);
    return (
      <Card>
        <CardContent className="p-6 text-center text-red-500">
          <Typography variant="p">Error loading enrollments. Please try again.</Typography>
        </CardContent>
      </Card>
    );
  }
};

export default CourseEnrollments;
