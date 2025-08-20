"use client";

import { Status } from "@/services/statusService";
import Typography from "@/components/ui/Typography";
import UserAvatar from "@/components/user/user-avatar";
import { formatDistanceToNow } from "date-fns";
import Link from "next/link";

interface StatusCardProps {
  status: Status;
}

export default function StatusCard({ status }: StatusCardProps) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-start gap-3 mb-3">
        <UserAvatar
          user={{
            id: status.user.id,
            username: status.user.username,
            profile_picture: status.user.profile_picture,
            role: status.user.role
          }}
          size="md"
          clickable={true}
        />
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-1">
            <Link 
              href={`/users/${status.user.username}`}
              className="hover:underline"
            >
              <Typography variant="h6" className="text-gray-900 font-medium">
                {status.user.username}
              </Typography>
            </Link>
            <Typography variant="span" className="text-gray-500 text-xs">
              {formatDistanceToNow(new Date(status.created_at), { addSuffix: true })}
            </Typography>
          </div>
          
          <Typography variant="p" className="text-gray-700 leading-relaxed">
            {status.content}
          </Typography>
        </div>
      </div>
    </div>
  );
}
