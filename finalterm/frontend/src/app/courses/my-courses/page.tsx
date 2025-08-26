import Typography from "@/components/ui/Typography";
import { getServerUser } from "@/lib/auth";
import { redirect } from "next/navigation";
import CourseFormDialog from "../components/course-form-dialog";
import { Button } from "@/components/ui/button";
import { Plus, Loader2 } from "lucide-react";
import { Suspense } from "react";
import MyCoursesClient from "./my-courses-client";

export default async function MyCoursesPage() {
  const user = await getServerUser();

  // Redirect non-teachers to the main courses page
  if (!user || user.role !== "teacher") {
    redirect("/courses");
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <Typography
            variant="h1"
            size="lg"
            className="mb-2"
          >
            My Created Courses
          </Typography>
          <Typography
            variant="p"
            color="muted"
            size="sm"
          >
            Manage all your created courses and view enrollment statistics
          </Typography>
        </div>
        <CourseFormDialog mode="create" />
      </div>

      <Suspense fallback={<div>Loading courses...</div>}>
        <MyCoursesClient />
      </Suspense>
    </div>
  );
}
