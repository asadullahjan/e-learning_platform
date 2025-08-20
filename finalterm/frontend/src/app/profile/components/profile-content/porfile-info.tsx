"use client";
import { Button } from "@/components/ui/button";
import Input from "@/components/ui/Input";
import Typography from "@/components/ui/Typography";
import { authService } from "@/services/authService";
import { useAuthStore } from "@/store/authStore";
import { useEffect, useState } from "react";
import Logout from "../logout";
import { Card, CardContent } from "@/components/ui/card";

const ProfileInfo = () => {
  const { user, isLoading, setUser } = useAuthStore();
  const [isEditing, setIsEditing] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<{ [key: string]: string[] }>({});
  const [message, setMessage] = useState({
    success: "",
    error: "",
  });
  const [formData, setFormData] = useState({
    username: user?.username,
    email: user?.email,
    first_name: user?.first_name,
    last_name: user?.last_name,
    role: user?.role,
  });

  useEffect(() => {
    setFormData({
      username: user?.username,
      email: user?.email,
      first_name: user?.first_name,
      last_name: user?.last_name,
      role: user?.role,
    });
  }, [user]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleEditProfile = async () => {
    setIsEditing(true);
    if (isEditing) {
      try {
        const form = new FormData();
        for (const [key, value] of Object.entries(formData)) {
          form.append(key, value || "");
        }

        const response = await authService.updateProfile(form);
        setMessage({
          success: "Profile updated successfully",
          error: "",
        });
        setFieldErrors({});
        setUser(response.user);
        setIsEditing(false);
      } catch (error: any) {
        console.error("Error updating profile:", error);
        if (error.response && error.response.status === 400) {
          setFieldErrors(error.response.data); // Django sends field-level errors
        } else {
          setMessage({ success: "", error: "Something went wrong." });
        }
      }
    }
  };

  if (!user) return;

  return (
    <Card className="pt-6">
      <CardContent>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div>
              <Typography
                variant="h1"
                size={"sm"}
              >
                {user.username ? `${user.username}` : "Profile"}
              </Typography>
              <Typography variant="p">
                Role: {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
              </Typography>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {isEditing && (
              <Button
                variant="outline"
                onClick={() => setIsEditing(false)}
              >
                Cancel
              </Button>
            )}
            <Button
              variant="outline"
              onClick={() => handleEditProfile()}
            >
              {isEditing ? "Save" : "Edit Profile"}
            </Button>
            <Logout />
          </div>
        </div>

        <div className="mt-6 border-t border-gray-200 pt-6">
          <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
            <div>
              <dt className="text-sm font-medium text-gray-500">Username</dt>
              {isEditing ? (
                <div>
                  <Input
                    type="text"
                    name="username"
                    value={formData.username}
                    onChange={handleInputChange}
                    className="mt-1 text-sm text-gray-900"
                  />
                  {fieldErrors.username && (
                    <Typography
                      variant="span"
                      color="error"
                    >
                      {fieldErrors.username}
                    </Typography>
                  )}
                </div>
              ) : (
                <dd className="mt-1 text-sm text-gray-900">{user.username || "Not set"}</dd>
              )}
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Email</dt>
              {isEditing ? (
                <div>
                  <Input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    className="mt-1 text-sm text-gray-900"
                  />
                  {fieldErrors.email && (
                    <Typography
                      variant="span"
                      color="error"
                    >
                      {fieldErrors.email}
                    </Typography>
                  )}
                </div>
              ) : (
                <dd className="mt-1 text-sm text-gray-900">{user.email}</dd>
              )}
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">First Name</dt>
              {isEditing ? (
                <div>
                  <Input
                    type="text"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleInputChange}
                    className="mt-1 text-sm text-gray-900"
                  />
                  {fieldErrors.first_name && (
                    <Typography
                      variant="span"
                      color="error"
                    >
                      {fieldErrors.first_name}
                    </Typography>
                  )}
                </div>
              ) : (
                <dd className="mt-1 text-sm text-gray-900">{user.first_name || "Not set"}</dd>
              )}
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Last Name</dt>
              {isEditing ? (
                <div>
                  <Input
                    type="text"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleInputChange}
                    className="mt-1 text-sm text-gray-900"
                  />
                  {fieldErrors.last_name && (
                    <Typography
                      variant="span"
                      color="error"
                    >
                      {fieldErrors.last_name}
                    </Typography>
                  )}
                </div>
              ) : (
                <dd className="mt-1 text-sm text-gray-900">{user.last_name || "Not set"}</dd>
              )}
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Role</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Member Since</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {new Date(user.created_at).toLocaleDateString()}
              </dd>
            </div>
          </dl>
        </div>
      </CardContent>
    </Card>
  );
};

export default ProfileInfo;
