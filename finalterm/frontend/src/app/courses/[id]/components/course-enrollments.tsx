import { enrollmentService, TeacherEnrollment } from "@/services/enrollmentService";
import { Card, CardContent } from "@/components/ui/card";
import Avatar from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import Input from "@/components/ui/Input";

const CourseEnrollments = async ({ courseId }: { courseId: string }) => {
  try {
    const enrollments: TeacherEnrollment[] = await enrollmentService.server.getCourseEnrollments(
      courseId
    );

    if (!enrollments || enrollments.length === 0) {
      return (
        <Card>
          <CardContent className="p-6 text-center text-gray-500">
            <p>No students enrolled yet.</p>
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
          <div className="bg-white p-4 rounded-lg border">
            <h3 className="font-medium text-gray-900">Total Enrolled</h3>
            <p className="text-2xl font-bold text-blue-600">{enrollments.length}</p>
          </div>
          <div className="bg-white p-4 rounded-lg border">
            <h3 className="font-medium text-gray-900">Active Students</h3>
            <p className="text-2xl font-bold text-green-600">{activeEnrollments.length}</p>
          </div>
          <div className="bg-white p-4 rounded-lg border">
            <h3 className="font-medium text-gray-900">Inactive Students</h3>
            <p className="text-2xl font-bold text-gray-600">{inactiveEnrollments.length}</p>
          </div>
        </div>

        {/* Search and Filter */}
        <div className="bg-white p-4 rounded-lg border">
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
              >
                All Students
              </Button>
              <Button
                variant="outline"
                size="sm"
              >
                Active Only
              </Button>
              <Button
                variant="outline"
                size="sm"
              >
                Inactive Only
              </Button>
            </div>
          </div>
        </div>

        {/* Active Students */}
        <div>
          <h3 className="text-lg font-semibold mb-4">
            Active Students ({activeEnrollments.length})
          </h3>
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
                        <h4 className="font-medium text-gray-900">{enrollment.user.username}</h4>
                        <p className="text-sm text-gray-500">{enrollment.user.email}</p>
                        <p className="text-xs text-gray-400">Role: {enrollment.user.role}</p>
                      </div>
                    </div>

                    <div className="text-right space-y-2">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        Active
                      </span>
                      <p className="text-xs text-gray-500">
                        Enrolled: {new Date(enrollment.enrolled_at).toLocaleDateString()}
                      </p>
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                        >
                          View Profile
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                        >
                          Message
                        </Button>
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
            <h3 className="text-lg font-semibold mb-4">
              Inactive Students ({inactiveEnrollments.length})
            </h3>
            <div className="grid gap-4">
              {inactiveEnrollments.map((enrollment) => (
                <Card
                  key={enrollment.id}
                  className="opacity-75"
                >
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
                          <h4 className="font-medium text-gray-700">{enrollment.user.username}</h4>
                          <p className="text-sm text-gray-500">{enrollment.user.email}</p>
                          <p className="text-xs text-gray-400">Role: {enrollment.user.role}</p>
                        </div>
                      </div>

                      <div className="text-right space-y-2">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                          Inactive
                        </span>
                        <p className="text-xs text-gray-500">
                          Enrolled: {new Date(enrollment.enrolled_at).toLocaleDateString()}
                        </p>
                        {enrollment.unenrolled_at && (
                          <p className="text-xs text-gray-500">
                            Unenrolled: {new Date(enrollment.unenrolled_at).toLocaleDateString()}
                          </p>
                        )}
                        <Button
                          size="sm"
                          variant="outline"
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
          <p>Error loading enrollments. Please try again.</p>
        </CardContent>
      </Card>
    );
  }
};

export default CourseEnrollments;
