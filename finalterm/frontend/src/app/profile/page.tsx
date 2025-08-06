import ProfileCover from "./components/profile-header/profile-cover";
import ProfileInfo from "./components/profile-content/porfile-info";

export default function ProfilePage() {
  return (
    <div className="flex flex-col gap-14">
      <ProfileCover />
      <div className="mt-8">
        <ProfileInfo />
      </div>
    </div>
  );
}
