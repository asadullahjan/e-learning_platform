"use client";

import { forwardRef, useImperativeHandle } from "react";
import { useLoadMore } from "@/components/hooks/useLoadMore";
import { statusService, Status } from "@/services/statusService";
import StatusCard from "./status-card";
import Typography from "@/components/ui/Typography";
import { LoadMoreButton } from "@/components/ui/load-more-button";

export interface StatusListRef {
  refresh: () => void;
}

const StatusList = forwardRef<StatusListRef>((props, ref) => {
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
        <Typography variant="p" color="error">
          Error loading statuses: {error}
        </Typography>
      </div>
    );
  }

  if (statuses.length === 0 && !isLoading) {
    return (
      <div className="text-center py-8">
        <Typography variant="p" color="muted">
          No status updates yet. Be the first to share something!
        </Typography>
      </div>
    );
  }

  return (
    <div className="flex flex-col space-y-4">
      {statuses.map((status) => (
        <StatusCard key={status.id} status={status} />
      ))}
      
      {hasNextPage && (
        <div className="pt-4">
          <LoadMoreButton
            onClick={loadMore}
            isLoading={isLoading}
            hasNextPage={hasNextPage}
          />
        </div>
      )}
    </div>
  );
});

StatusList.displayName = "StatusList";

export default StatusList;
