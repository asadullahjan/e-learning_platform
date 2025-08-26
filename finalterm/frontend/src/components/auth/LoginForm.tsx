"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { useRouter } from "next/navigation";
import { authService, LoginData } from "@/services/authService";
import { useAuthStore } from "@/store/authStore";
import { Button } from "../ui/button";
import Input from "../ui/Input";
import Typography from "../ui/Typography";

export default function LoginForm() {
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  const { login, error, setError } = useAuthStore();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginData>();

  const onSubmit = async (data: LoginData) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await authService.login(data);
      login(response.user);
      router.push("/home");
    } catch (err: any) {
      const errorMessage =
        err.response?.data?.email?.[0] ||
        err.response?.data?.password?.[0] ||
        err.response?.data?.non_field_errors?.[0] ||
        "Login failed. Please try again.";
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
            Login
          </Typography>
        </div>
        <form
          className="mt-8 space-y-6"
          onSubmit={handleSubmit(onSubmit)}
        >
          <div className="rounded-md space-y-2">
            <div>
              <label
                htmlFor="Email"
                className="sr-only"
              >
                email
              </label>
              <Input
                {...register("email", { required: "email is required" })}
                id="email"
                name="email"
                type="text"
                required
                placeholder="email"
              />
              {errors.email && (
                <Typography
                  variant="p"
                  color="destructive"
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
                {...register("password", { required: "Password is required" })}
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
              {isLoading ? "Signing in..." : "Sign in"}
            </Button>
          </div>

          <div className="text-center">
            <Typography variant="p">
              Don't have an account?{" "}
              <a
                href="/auth/register"
                className="font-medium text-primary hover:text-primary/80"
              >
                Sign up
              </a>
            </Typography>
          </div>
        </form>
      </div>
    </div>
  );
}
