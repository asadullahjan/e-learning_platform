"use client";
import { useAuthStore } from "@/store/authStore";
import { Pen, UserIcon, Loader2 } from "lucide-react";
import Image from "next/image";
import { useState } from "react";
import { authService } from "@/services/authService";

const ProfileAvatar = () => {
  const { user, setUser } = useAuthStore();
  const [profilePicture, setProfilePicture] = useState<string | null>(
    user?.profile_picture || null
  );
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState({
    success: "",
    error: "",
  });

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setProfilePicture(URL.createObjectURL(file));

      // Upload immediately
      setIsUploading(true);
      setMessage({ success: "", error: "" });

      try {
        const form = new FormData();
        form.append("profile_picture", file);

        const response = await authService.updateProfile(form);
        setUser(response.user);
        setMessage({
          success: "Profile picture updated successfully!",
          error: "",
        });

        // Clear preview after successful upload
        setProfilePicture(null);
      } catch (error: any) {
        console.error("Error uploading profile picture:", error);
        setMessage({
          success: "",
          error: "Failed to upload profile picture. Please try again.",
        });
        // Clear preview on error
        setProfilePicture(null);
      } finally {
        setIsUploading(false);
      }
    }
  };

  return (
    <div className="relative group w-20 h-20 md:w-32 md:h-32 bg-white rounded-full overflow-hidden shadow-lg border-4 border-white">
      {/* Loading overlay */}
      {isUploading && (
        <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center z-20">
          <Loader2 className="w-6 h-6 text-white animate-spin" />
        </div>
      )}

      {/* Success/Error messages */}
      {message.success && (
        <div className="absolute -bottom-12 left-1/2 transform -translate-x-1/2 bg-green-500 text-white px-3 py-1 rounded-md text-xs whitespace-nowrap z-30 shadow-lg">
          {message.success}
        </div>
      )}
      {message.error && (
        <div className="absolute -bottom-12 left-1/2 transform -translate-x-1/2 bg-red-500 text-white px-3 py-1 rounded-md text-xs whitespace-nowrap z-30 shadow-lg">
          {message.error}
        </div>
      )}

      {/* Edit overlay */}
      <div className="absolute inset-0 bg-black bg-opacity-0 opacity-0 group-hover:opacity-60 group-hover:bg-opacity-60 cursor-pointer transition-all duration-200 items-center justify-center z-10 pointer-events-none flex">
        <Pen className="w-5 h-5 md:w-6 md:h-6 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
      </div>

      <input
        type="file"
        accept="image/*"
        className="hidden"
        id="profile-picture-input"
        onChange={handleFileChange}
      />
      <label
        htmlFor="profile-picture-input"
        className={`cursor-pointer block w-full h-full hover:scale-105 transition-transform duration-200`}
      >
        {profilePicture ? (
          <Image
            src={profilePicture}
            alt="Profile Picture Preview"
            width={128}
            height={128}
            className="w-full h-full object-cover"
          />
        ) : user?.profile_picture ? (
          <Image
            src={`${process.env.NEXT_PUBLIC_URL}${user?.profile_picture}`}
            alt="Profile Picture"
            width={128}
            height={128}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-gray-100 to-gray-200">
            <UserIcon className="w-8 h-8 md:w-12 md:h-12 text-gray-400" />
          </div>
        )}
      </label>
    </div>
  );
};

export default ProfileAvatar;
