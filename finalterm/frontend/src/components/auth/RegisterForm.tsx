"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { useRouter } from "next/navigation";
import { authService, RegisterData } from "@/services/authService";
import { useAuthStore } from "@/store/authStore";
import { Button } from "../ui/button";
import Input from "../ui/Input";
import Typography from "../ui/Typography";
import { Select, SelectContent, SelectItem, SelectTrigger } from "../ui/select";

export default function RegisterForm() {
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  const { login, error, setError } = useAuthStore();

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<RegisterData>({
    defaultValues: {
      role: "student",
    },
  });

  const onSubmit = async (data: RegisterData) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await authService.register(data);
      login(response.user);
      router.push("/home");
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.username?.[0] ||
        err.response?.data?.email?.[0] ||
        err.response?.data?.password?.[0] ||
        err.response?.data?.role?.[0] ||
        err.response?.data?.non_field_errors?.[0] ||
        "Registration failed. Please try again.";
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-sm w-full space-y-8 bg-white rounded-lg px-6 py-8 shadow-sm">
        <div className="flex items-center justify-center">
          <Typography
            variant="h1"
            color="primary"
          >
            Sign Up
          </Typography>
        </div>
        <form
          className="mt-8 space-y-6"
          onSubmit={handleSubmit(onSubmit)}
        >
          <div className="rounded-md space-y-4">
            <div className="w-full">
              <Select
                value={watch("role")}
                onValueChange={(value) => setValue("role", value as "student" | "teacher")}
              >
                <SelectTrigger className="w-full">
                  <Typography
                    variant="p"
                    size={"md"}
                  >
                    {watch("role")
                      ? watch("role") === "student"
                        ? "Student"
                        : "Teacher"
                      : "Select Role"}
                  </Typography>
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="student">Student</SelectItem>
                  <SelectItem value="teacher">Teacher</SelectItem>
                </SelectContent>
              </Select>
              {errors.role && (
                <Typography
                  variant="p"
                  color="destructive"
                  className="text-sm mt-1"
                >
                  {errors.role.message}
                </Typography>
              )}
            </div>
            <div>
              <label
                htmlFor="username"
                className="sr-only"
              >
                Username
              </label>
              <Input
                {...register("username", {
                  required: "Username is required",
                  minLength: { value: 3, message: "Username must be at least 3 characters" },
                  pattern: {
                    value: /^[a-zA-Z0-9_]+$/,
                    message: "Username can only contain letters, numbers, and underscores",
                  },
                })}
                id="username"
                name="username"
                type="text"
                required
                placeholder="Username"
              />
              {errors.username && (
                <Typography
                  variant="p"
                  color="destructive"
                  className="text-sm mt-1"
                >
                  {errors.username.message}
                </Typography>
              )}
            </div>
            <div>
              <label
                htmlFor="email"
                className="sr-only"
              >
                Email
              </label>
              <Input
                {...register("email", {
                  required: "Email is required",
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: "Invalid email address",
                  },
                })}
                id="email"
                name="email"
                type="email"
                required
                placeholder="Email"
              />
              {errors.email && (
                <Typography
                  variant="p"
                  color="destructive"
                  className="text-sm mt-1"
                >
                  {errors.email.message}
                </Typography>
              )}
            </div>

            <div>
              <label
                htmlFor="password"
                className="sr-only"
              >
                Password
              </label>
              <Input
                {...register("password", {
                  required: "Password is required",
                  minLength: { value: 8, message: "Password must be at least 8 characters" },
                })}
                id="password"
                name="password"
                type="password"
                required
                placeholder="Password"
              />
              {errors.password && (
                <Typography
                  variant="p"
                  color="destructive"
                  className="text-sm mt-1"
                >
                  {errors.password.message}
                </Typography>
              )}
            </div>
          </div>

          {error && (
            <Typography
              variant="p"
              color="destructive"
              className="text-sm"
            >
              {error}
            </Typography>
          )}

          <div>
            <Button
              type="submit"
              disabled={isLoading}
              loading={isLoading}
              className="w-full"
            >
              {isLoading ? "Creating account..." : "Create account"}
            </Button>
          </div>

          <div className="text-center">
            <Typography variant="p">
              Already have an account?{" "}
              <a
                href="/auth/login"
                className="font-medium text-primary hover:text-primary/80"
              >
                Sign in
              </a>
            </Typography>
          </div>
        </form>
      </div>
    </div>
  );
}
