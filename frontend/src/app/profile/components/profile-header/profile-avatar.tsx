"use client";
import { useAuthStore } from "@/store/authStore";
import { Pen, Loader2 } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { showToast } from "@/lib/toast";
import Avatar from "@/components/ui/avatar";
import { userService } from "@/services/userService";

const ProfileAvatar = ({
  className,
  update = false,
  imageUrl,
}: {
  className?: string;
  update?: boolean;
  imageUrl?: string;
}) => {
  const { user, setUser } = useAuthStore();
  const [profilePicture, setProfilePicture] = useState<string | null>(
    imageUrl || user?.profile_picture || null
  );
  const [isUploading, setIsUploading] = useState(false);
  const canUpdate = update && !imageUrl;

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!user) return;
    const file = e.target.files?.[0];
    if (file) {
      setProfilePicture(URL.createObjectURL(file));

      // Upload immediately
      setIsUploading(true);

      try {
        const form = new FormData();
        form.append("profile_picture", file);

        const response = await userService.updateProfile(user.id, form);
        setUser(response);
        showToast.success("Profile picture updated successfully!");

        // Clear preview after successful upload
        setProfilePicture(null);
      } catch (error: any) {
        console.error("Error uploading profile picture:", error);
        showToast.error("Failed to upload profile picture. Please try again.");
        // Clear preview on error
        setProfilePicture(null);
      } finally {
        setIsUploading(false);
      }
    }
  };

  return (
    <div className={cn("relative group", className)}>
      {/* Loading overlay */}
      {isUploading && (
        <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center z-20 rounded-full">
          <Loader2 className="w-6 h-6 text-white animate-spin" />
        </div>
      )}

      {/* Edit overlay */}
      {canUpdate && (
        <div className="absolute inset-0 bg-black bg-opacity-0 opacity-0 group-hover:opacity-60 group-hover:bg-opacity-60 cursor-pointer transition-all duration-200 items-center justify-center z-10 pointer-events-none flex rounded-full">
          <Pen className="w-5 h-5 md:w-6 md:h-6 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
        </div>
      )}

      <input
        type="file"
        accept="image/*"
        className="hidden"
        id="profile-picture-input"
        onChange={handleFileChange}
        disabled={!canUpdate}
      />
      <label
        htmlFor="profile-picture-input"
        className={`cursor-pointer block w-full h-full hover:scale-105 transition-transform duration-200`}
      >
        <Avatar
          src={profilePicture}
          alt="Profile Picture"
          size="xl"
          className="w-20 h-20 md:w-32 md:h-32 border-4 border-white shadow-lg rounded-full"
        />
      </label>
    </div>
  );
};

export default ProfileAvatar;
