import { redirect } from "next/navigation";
import { getServerUser } from "@/lib/auth";
import RestrictionsManagement from "./components/restrictions-management";

export default async function RestrictionsPage() {
  const user = await getServerUser();
  
  if (!user) {
    redirect("/auth/login");
  }
  
  if (user.role !== "teacher") {
    redirect("/");
  }

  return (
    <div className="container mx-auto py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Student Restrictions Management
        </h1>
        <p className="text-gray-600">
          Manage student restrictions across all your courses
        </p>
      </div>
      
      <RestrictionsManagement />
    </div>
  );
}
