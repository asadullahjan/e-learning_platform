"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import Typography from "./ui/Typography";
import { useAuthStore } from "@/store/authStore";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "./ui/dropdown";
import { Button } from "./ui/button";
import { LogOutIcon, UserIcon } from "lucide-react";
import ProfileAvatar from "@/app/profile/components/profile-header/profile-avatar";
import { authService } from "@/services/authService";

export default function Header() {
  const { user, isLoading, setUser } = useAuthStore();

  return (
    <header className="bg-white shadow-md">
      <div className="container mx-auto px-4 py-4 flex justify-between items-center">
        <div className="flex justify-between items-center">
          <Link href="/">
            <Typography
              variant="h1"
              className="text-2xl font-bold"
            >
              E-Learning
            </Typography>
          </Link>
        </div>
        <div className="flex justify-end items-center">
          <DropdownMenu>
            <DropdownMenuTrigger>
              <ProfileAvatar className="w-10 h-10 md:w-10 md:h-10 border-none" />
            </DropdownMenuTrigger>
            <DropdownMenuContent
              align="end"
              className="mt-2"
            >
              <DropdownMenuItem asChild>
                <Link href="/profile">
                  <UserIcon className="w-4 h-4 mr-2 inline-block" />
                  Profile
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => authService.logout()}>
                <LogOutIcon className="w-4 h-4 mr-2" />
                Logout
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}
