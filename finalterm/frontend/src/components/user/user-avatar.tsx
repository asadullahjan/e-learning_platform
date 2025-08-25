import Link from "next/link";
import Avatar from "@/components/ui/avatar";
import Typography from "../ui/Typography";
import { User } from "@/services/authService";

interface UserAvatarProps {
  user: User;
  size?: "sm" | "md" | "lg" | "xl" | "2xl" | "4xl";
  showName?: boolean;
  clickable?: boolean;
  className?: string;
}

const UserAvatar = ({
  user,
  size = "md",
  showName = false,
  clickable = true,
  className,
}: UserAvatarProps) => {
  const displayName = user.username;

  const avatar = (
    <Avatar
      src={user.profile_picture}
      alt={displayName}
      size={size}
      className={className}
    />
  );

  if (!clickable) {
    return showName ? (
      <div className="flex items-center gap-2">
        {avatar}
        <div className="flex flex-col">
          <Typography
            variant={"span"}
            className="font-semibold"
          >
            {displayName}
          </Typography>
          <Typography variant={"span"}>{user.role}</Typography>
        </div>
      </div>
    ) : (
      avatar
    );
  }

  return (
    <Link
      href={`/users/${user.username}`}
      className="hover:opacity-80 transition-opacity"
    >
      {showName ? (
        <div className="flex items-center gap-2">
          {avatar}
          <div className="flex flex-col">
            <Typography
              variant={"span"}
              className="font-semibold"
            >
              {displayName}
            </Typography>
            <Typography variant={"span"}>{user.role}</Typography>
          </div>
        </div>
      ) : (
        avatar
      )}
    </Link>
  );
};

export default UserAvatar;
