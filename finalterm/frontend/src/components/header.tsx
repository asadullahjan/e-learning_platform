"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import Typography from "./ui/Typography";
import { useAuthStore } from "@/store/authStore";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "./ui/dropdown";
import { Button } from "./ui/button";
import {
  LogOutIcon,
  UserIcon,
  BookOpenIcon,
  MessageSquareIcon,
  HomeIcon,
  UsersIcon,
  ShieldIcon,
  MenuIcon,
  GraduationCapIcon,
  ActivityIcon,
  PlayIcon,
} from "lucide-react";
import { authService } from "@/services/authService";
import Avatar from "./ui/avatar";
import { NotificationBell } from "./notification-bell";
import { useRouter } from "next/navigation";

export default function Header() {
  const { user, isLoading, setUser } = useAuthStore();
  const pathname = usePathname();
  const router = useRouter();
  const isActive = (path: string) => pathname === path;

  return (
    <>
      {/* Demo Video Banner */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-4">
        <div className="container mx-auto flex items-center justify-center space-x-2">
          <PlayIcon className="w-5 h-5" />
          <span className="font-semibold text-sm md:text-base">Demo Video:</span>
          <a
            href="https://youtu.be/bwJ8uLWKTjk"
            target="_blank"
            rel="noopener noreferrer"
            className="underline hover:no-underline font-medium text-sm md:text-base transition-all duration-200 hover:text-yellow-200"
          >
            Watch the Application Demo
          </a>
        </div>
      </div>

      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            {/* Mobile Navigation Dropdown - Center (Mobile Only) */}
            <div className="lg:hidden  flex ">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-gray-600 hover:bg-gray-100 rounded-full px-3 py-2"
                  >
                    <MenuIcon className="w-5 h-5" />
                    <span className="ml-2 text-sm font-medium">Menu</span>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent
                  align="center"
                  className="w-56 mt-2"
                >
                  <DropdownMenuItem asChild>
                    <Link
                      href="/home"
                      className="flex items-center w-full"
                    >
                      <HomeIcon className="w-4 h-4 mr-3" />
                      Home
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link
                      href="/courses"
                      className="flex items-center w-full"
                    >
                      <BookOpenIcon className="w-4 h-4 mr-3" />
                      Courses
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link
                      href="/chats"
                      className="flex items-center w-full"
                    >
                      <MessageSquareIcon className="w-4 h-4 mr-3" />
                      Chats
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link
                      href="/users"
                      className="flex items-center w-full"
                    >
                      <UsersIcon className="w-4 h-4 mr-3" />
                      Browse Users
                    </Link>
                  </DropdownMenuItem>
                  {user?.role === "teacher" && (
                    <DropdownMenuItem asChild>
                      <Link
                        href="/restrictions"
                        className="flex items-center w-full"
                      >
                        <ShieldIcon className="w-4 h-4 mr-3" />
                        Manage Restrictions
                      </Link>
                    </DropdownMenuItem>
                  )}
                  {user?.role === "teacher" && (
                    <DropdownMenuItem asChild>
                      <Link
                        href="/courses/my-courses"
                        className="flex items-center w-full"
                      >
                        <BookOpenIcon className="w-4 h-4 mr-3" />
                        My Created Courses
                      </Link>
                    </DropdownMenuItem>
                  )}
                  {user?.role === "student" && (
                    <DropdownMenuItem asChild>
                      <Link
                        href="/courses/enrolled"
                        className="flex items-center w-full"
                      >
                        <BookOpenIcon className="w-4 h-4 mr-3" />
                        My Enrolled Courses
                      </Link>
                    </DropdownMenuItem>
                  )}
                  <DropdownMenuSeparator />
                </DropdownMenuContent>
              </DropdownMenu>
            </div>

            {/* Logo Section - Left Side */}
            <div className="flex items-center space-x-3 flex-shrink-0">
              <div className="bg-blue-600 rounded-lg p-2 lg:block hidden">
                <GraduationCapIcon className="w-6 h-6 text-white" />
              </div>
              <Link href="/">
                <Typography
                  variant="h1"
                  className="text-2xl font-bold text-gray-900"
                >
                  E-Learning
                </Typography>
              </Link>
            </div>

            {/* Main Navigation Links - Center (Desktop Only) */}
            <div className="hidden lg:flex justify-center items-center space-x-6 flex-1">
              <Link
                href="/home"
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive("/home")
                    ? "bg-blue-100 text-blue-700"
                    : "text-gray-600 hover:text-blue-600 hover:bg-gray-50"
                }`}
              >
                <HomeIcon className="w-4 h-4 inline mr-2" />
                Home
              </Link>
              <Link
                href="/users"
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive("/users")
                    ? "bg-blue-100 text-blue-700"
                    : "text-gray-600 hover:text-blue-600 hover:bg-gray-50"
                }`}
              >
                <UsersIcon className="w-4 h-4 inline mr-2" />
                Users
              </Link>

              <Link
                href="/courses"
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive("/courses")
                    ? "bg-blue-100 text-blue-700"
                    : "text-gray-600 hover:text-blue-600 hover:bg-gray-50"
                }`}
              >
                <BookOpenIcon className="w-4 h-4 inline mr-2" />
                Courses
              </Link>

              {user?.role === "teacher" && (
                <Link
                  href="/restrictions"
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive("/restrictions")
                      ? "bg-blue-100 text-blue-700"
                      : "text-gray-600 hover:text-blue-600 hover:bg-gray-50"
                  }`}
                >
                  <ShieldIcon className="w-4 h-4 inline mr-2" />
                  Manage Restrictions
                </Link>
              )}

              <Link
                href="/chats"
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive("/chats")
                    ? "bg-blue-100 text-blue-700"
                    : "text-gray-600 hover:text-blue-600 hover:bg-gray-50"
                }`}
              >
                <MessageSquareIcon className="w-4 h-4 inline mr-2" />
                Chats
              </Link>
            </div>

            {/* Right Side - Notifications & User Menu */}
            <div className="flex justify-end items-center space-x-3 flex-shrink-0">
              {user && <NotificationBell />}

              <DropdownMenu>
                <DropdownMenuTrigger>
                  <Avatar
                    src={user?.profile_picture}
                    alt={user?.username}
                    className="w-8 h-8 cursor-pointer hover:opacity-80 transition-opacity"
                  />
                </DropdownMenuTrigger>
                <DropdownMenuContent
                  align="end"
                  className="mt-2 w-48"
                >
                  <DropdownMenuItem asChild>
                    <Link
                      href="/profile"
                      className="flex items-center w-full"
                    >
                      <UserIcon className="w-4 h-4 mr-3" />
                      Profile
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    onClick={() => {
                      authService.logout();
                      setUser(null);
                      router.push("/auth/login");
                    }}
                    className="text-red-600 hover:text-red-700"
                  >
                    <LogOutIcon className="w-4 h-4 mr-3" />
                    Logout
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </div>
      </header>
    </>
  );
}
