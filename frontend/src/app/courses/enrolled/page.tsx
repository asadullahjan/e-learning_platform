import Typography from "@/components/ui/Typography";
import { getServerUser } from "@/lib/auth";
import { redirect } from "next/navigation";
import { Suspense } from "react";
import EnrolledCoursesClient from "./enrolled-courses-client";

export default async function EnrolledCoursesPage() {
  const user = await getServerUser();

  // Redirect non-students to the main courses page
  if (!user || user.role !== "student") {
    redirect("/courses");
  }

  return (
    <div className="flex flex-col gap-4">
      <div>
        <Typography
          variant="h1"
          size="lg"
          className="mb-2"
        >
          My Enrolled Courses
        </Typography>
        <Typography
          variant="p"
          color="muted"
          size="sm"
        >
          Track your progress and access all your enrolled courses
        </Typography>
      </div>

      <Suspense fallback={<div>Loading enrollments...</div>}>
        <EnrolledCoursesClient />
      </Suspense>
    </div>
  );
}
