import { UserIcon } from "lucide-react";
import Image from "next/image";
import { cn } from "@/lib/utils";

interface AvatarProps {
  src?: string | null;
  alt?: string;
  size?: "sm" | "md" | "lg" | "xl";
  className?: string;
  fallback?: React.ReactNode;
}

const Avatar = ({ src, alt, size = "md", className, fallback }: AvatarProps) => {
  const sizeClasses = {
    sm: "w-8 h-8",
    md: "w-10 h-10",
    lg: "w-12 h-12",
    xl: "w-16 h-16",
  };

  // Handle profile picture URL
  const getImageSrc = (src: string | null | undefined) => {
    if (!src) return null;

    // If it's already a full URL (starts with http), use as is
    if (src.startsWith("http")) return src;

    // If it's a blob URL (preview), use as is
    if (src.startsWith("blob:")) return src;

    // Otherwise, add the NEXT_PUBLIC_SERVER_URL prefix
    return `${process.env.NEXT_PUBLIC_SERVER_URL}${src}`;
  };

  const imageSrc = getImageSrc(src);

  return (
    <div className={cn("rounded-full overflow-hidden bg-gray-100", sizeClasses[size], className)}>
      {imageSrc ? (
        <Image
          src={imageSrc}
          alt={alt || "Avatar"}
          width={64}
          height={64}
          className="w-full h-full object-cover"
        />
      ) : (
        fallback || <UserIcon className="w-full h-full p-2 text-gray-400" />
      )}
    </div>
  );
};

export default Avatar;
