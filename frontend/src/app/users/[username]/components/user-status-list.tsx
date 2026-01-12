"use client";

import { forwardRef, useImperativeHandle } from "react";
import { useLoadMore } from "@/components/hooks/useLoadMore";
import { statusService, Status } from "@/services/statusService";
import StatusCard from "@/app/home/components/status-card";
import Typography from "@/components/ui/Typography";
import { LoadMoreButton } from "@/components/ui/load-more-button";
import { User } from "@/services/userService";

export interface UserStatusListRef {
  refresh: () => void;
}

interface UserStatusListProps {
  user: User;
}

const UserStatusList = forwardRef<UserStatusListRef, UserStatusListProps>(({ user }, ref) => {
  const {
    data: statuses,
    isLoading,
    hasNextPage,
    loadMore,
    refresh,
    error,
  } = useLoadMore<Status>({
    onLoadMore: async (isInitialLoad) => {
      const pageSize = 10;
      const offset = isInitialLoad ? 0 : statuses.length;

      const response = await statusService.getStatuses({
        limit: pageSize.toString(),
        offset: offset.toString(),
        user: user.id,
      });

      return {
        data: response.results,
        hasNextPage: !!response.next,
      };
    },
    pageSize: 10,
  });

  useImperativeHandle(ref, () => ({
    refresh,
  }));

  if (error) {
    return (
      <div className="text-center py-8">
        <Typography
          variant="p"
          color="error"
        >
          Error loading statuses: {error}
        </Typography>
      </div>
    );
  }

  if (statuses.length === 0 && !isLoading) {
    return (
      <div className="text-center py-8">
        <Typography
          variant="p"
          color="muted"
        >
          {user.username} hasn't posted any status updates yet.
        </Typography>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {statuses.map((status) => (
        <div key={status.id}>
          <StatusCard status={status} />
        </div>
      ))}

      {hasNextPage && (
        <LoadMoreButton
          onClick={loadMore}
          isLoading={isLoading}
          hasNextPage={hasNextPage}
        />
      )}
    </div>
  );
});

UserStatusList.displayName = "UserStatusList";

export default UserStatusList;
