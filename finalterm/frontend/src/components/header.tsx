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
} from "lucide-react";
import { authService } from "@/services/authService";
import Avatar from "./ui/avatar";
import { NotificationBell } from "./notification-bell";

export default function Header() {
  const { user, isLoading, setUser } = useAuthStore();
  const pathname = usePathname();

  const isActive = (path: string) => pathname === path;

  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="container mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          {/* Logo Section */}
          <div className="flex items-center space-x-3">
            <div className="bg-blue-600 rounded-lg p-2">
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

          {/* Main Navigation Links */}
          <div className="hidden lg:flex justify-center items-center space-x-6">
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

            {/* Quick Navigation Dropdown */}
            <div className="relative">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="outline"
                    size="sm"
                    className="text-gray-600 hover:text-blue-600"
                  >
                    <MenuIcon className="w-4 h-4 mr-2" />
                    Quick Access
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent
                  align="end"
                  className="w-56 mt-3"
                >
                  <DropdownMenuItem asChild>
                    <Link
                      href="/users"
                      className="flex items-center"
                    >
                      <UsersIcon className="w-4 h-4 mr-2" />
                      Browse Users
                    </Link>
                  </DropdownMenuItem>
                  {user?.role === "teacher" && (
                    <>
                      <DropdownMenuItem asChild>
                        <Link
                          href="/restrictions"
                          className="flex items-center"
                        >
                          <ShieldIcon className="w-4 h-4 mr-2" />
                          Manage Restrictions
                        </Link>
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                    </>
                  )}
                  <DropdownMenuItem asChild>
                    <Link
                      href="/profile"
                      className="flex items-center"
                    >
                      <UserIcon className="w-4 h-4 mr-2" />
                      My Profile
                    </Link>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>

          {/* Mobile Navigation Dropdown */}
          <div className="lg:hidden">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-gray-600"
                >
                  <MenuIcon className="w-5 h-5" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent
                align="end"
                className="w-48"
              >
                <DropdownMenuItem asChild>
                  <Link
                    href="/home"
                    className="flex items-center"
                  >
                    <HomeIcon className="w-4 h-4 mr-2" />
                    Home
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link
                    href="/courses"
                    className="flex items-center"
                  >
                    <BookOpenIcon className="w-4 h-4 mr-2" />
                    Courses
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link
                    href="/chats"
                    className="flex items-center"
                  >
                    <MessageSquareIcon className="w-4 h-4 mr-2" />
                    Chats
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link
                    href="/users"
                    className="flex items-center"
                  >
                    <UsersIcon className="w-4 h-4 mr-2" />
                    Browse Users
                  </Link>
                </DropdownMenuItem>
                {user?.role === "teacher" && (
                  <DropdownMenuItem asChild>
                    <Link
                      href="/restrictions"
                      className="flex items-center"
                    >
                      <ShieldIcon className="w-4 h-4 mr-2" />
                      Manage Restrictions
                    </Link>
                  </DropdownMenuItem>
                )}
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild>
                  <Link
                    href="/profile"
                    className="flex items-center"
                  >
                    <UserIcon className="w-4 h-4 mr-2" />
                    Profile
                  </Link>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>

          {/* Right Side - Notifications & User Menu */}
          <div className="flex justify-end items-center space-x-4">
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
                className="mt-2"
              >
                <DropdownMenuItem asChild>
                  <Link
                    href="/profile"
                    className="flex items-center"
                  >
                    <UserIcon className="w-4 h-4 mr-2" />
                    Profile
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  onClick={() => authService.logout()}
                  className="text-red-600 hover:text-red-700"
                >
                  <LogOutIcon className="w-4 h-4 mr-2" />
                  Logout
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </div>
    </header>
  );
}
