import ProfileAvatar from "./profile-avatar";

const ProfileCover = () => {
  return (
    <div className="relative flex items-center justify-center w-full h-48 bg-gray-200 rounded">
      {/* Avatar positioned at bottom */}
      <div className="absolute -bottom-16 left-8">
        <ProfileAvatar />
      </div>

      {/* Cover text */}
      <div className="absolute bottom-4 right-8 text-white text-opacity-80">
        <div className="text-sm font-medium text-black">Welcome to your profile</div>
      </div>
    </div>
  );
};

export default ProfileCover;
