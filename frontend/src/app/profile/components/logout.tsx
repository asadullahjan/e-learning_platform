"use client";

import { Button } from "@/components/ui/button";
import { authService } from "@/services/authService";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";

export default function Logout() {
  const router = useRouter();
  const { logout } = useAuthStore();

  const handleLogout = async () => {
    try {
      await authService.logout();
      logout();
      router.push("/auth/login");
    } catch (error) {
      console.error("Logout failed:", error);
      // You might want to show an error message to the user here
    }
  };

  return (
    <Button
      onClick={handleLogout}
      variant="destructive"
    >
      Logout
    </Button>
  );
}
