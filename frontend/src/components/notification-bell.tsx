"use client";

import { useState, useEffect } from "react";
import { Bell, Check, CheckCheck, Loader2, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { DropdownMenu, DropdownMenuContent, DropdownMenuTrigger } from "@/components/ui/dropdown";
import Typography from "@/components/ui/Typography";
import { notificationService, Notification } from "@/services/notificationService";
import { showToast } from "@/lib/toast";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";
import { useWebSocket } from "@/lib/useWebSocket";

export function NotificationBell() {
  const [isOpen, setIsOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [hasNextPage, setHasNextPage] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const router = useRouter();
  const { user } = useAuthStore();

  const fetchNotifications = async (page: number = 1) => {
    try {
      setIsLoading(true);
      const response = await notificationService.getNotifications(page);

      if (page === 1) {
        setNotifications(response.results);
        setCurrentPage(1);
      } else {
        setNotifications((prev) => [...prev, ...response.results]);
        setCurrentPage(page);
      }

      setHasNextPage(!!response.next);
    } catch (error) {
      console.error("Failed to fetch notifications:", error);
      showToast.error("Failed to fetch notifications");
    } finally {
      setIsLoading(false);
    }
  };

  const loadMore = async () => {
    if (hasNextPage && !isLoading) {
      await fetchNotifications(currentPage + 1);
    }
  };

  const refresh = async () => {
    await fetchNotifications(1);
  };

  // Initial fetch
  useEffect(() => {
    if (user) {
      fetchNotifications(1);
    }
  }, [user]);

  // Update unread count
  useEffect(() => {
    if (notifications.length > 0) {
      const unread = notifications.filter((n) => !n.is_read).length;
      setUnreadCount(unread);
    }
  }, [notifications]);

  const handleNotificationClick = async (notification: Notification) => {
    if (!notification.is_read) {
      try {
        await notificationService.markAsRead(notification.id);
        setUnreadCount((prev) => Math.max(0, prev - 1));
        refresh();
      } catch (error) {
        showToast.error("Failed to mark notification as read");
      }
    }

    router.push(notification.action_url);
    setIsOpen(false);
  };

  const handleMarkAllAsRead = async () => {
    try {
      await notificationService.markAllAsRead();
      setUnreadCount(0);
      setCurrentPage(1); // Reset page counter
      refresh();
      showToast.success("All notifications marked as read");
    } catch (error) {
      showToast.error("Failed to mark all notifications as read");
    }
  };

  const handleManualRefresh = async () => {
    setIsRefreshing(true);
    try {
      setCurrentPage(1);
      await refresh();
      // The refresh will update localNotifications via the useEffect
      showToast.success("Notifications refreshed");
    } catch (error) {
      showToast.error("Failed to refresh notifications");
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleWebSocketMessage = (event: MessageEvent) => {
    try {
      const data = JSON.parse(event.data);

      if (data.type === "notification") {
        const newNotification = data.notification;

        // Check for duplicates before adding
        const isDuplicate = notifications.some((n) => n.id === newNotification.id);

        if (!isDuplicate) {
          // Increment unread count immediately for better UX
          setUnreadCount((prev) => prev + 1);

          // Add the new notification to the beginning of the list immediately
          // This ensures it appears right away without waiting for API refresh
          const updatedNotifications = [newNotification, ...notifications];
          setNotifications(updatedNotifications);

          // Update the useLoadMore data directly
          if (typeof refresh === "function") {
            // Force a refresh to sync with backend
            setCurrentPage(1);
            refresh();
          }

          // Show toast for new notification
          showToast.success(`${newNotification.title}: ${newNotification.message}`);
        }
      }
    } catch (error) {
      console.error("Failed to parse WebSocket message:", error);
    }
  };

  // WebSocket connection for real-time notifications
  const { isConnected, isConnecting, isReconnecting } = useWebSocket({
    url: user ? `${process.env.NEXT_PUBLIC_WEBSOCKET_BASE_URL}/ws/notifications/` : '',
    onMessage: handleWebSocketMessage,
    onOpen: () => console.log("Connected to notification WebSocket"),
    onClose: (event) => console.log("WebSocket connection closed", event.code, event.reason),
    onError: (error) => console.error("WebSocket error:", error),
    autoReconnect: true,
    reconnectInterval: 3000,
    maxReconnectAttempts: 5,
  });

  return (
    <DropdownMenu
      open={isOpen}
      onOpenChange={setIsOpen}
    >
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="sm"
          className="relative p-2"
        >
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
              {unreadCount > 9 ? "9+" : unreadCount}
            </span>
          )}
        </Button>
      </DropdownMenuTrigger>

      <DropdownMenuContent
        className="w-96 max-h-96 overflow-hidden"
        align="end"
      >
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <Typography
              variant="h3"
              size="sm"
              className="font-semibold"
            >
              Notifications
            </Typography>
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleManualRefresh}
                disabled={isRefreshing}
                className="text-xs text-gray-600 hover:text-gray-800"
                title="Refresh notifications"
              >
                <RefreshCw className={`h-3 w-3 mr-1 ${isRefreshing ? "animate-spin" : ""}`} />
                Refresh
              </Button>
              {unreadCount > 0 && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleMarkAllAsRead}
                  className="text-xs"
                >
                  Mark all as read
                </Button>
              )}
            </div>
          </div>
        </div>

        <div className="overflow-y-auto max-h-64">
          {notifications.length === 0 && !isLoading ? (
            <div className="p-4 text-center">
              <Typography
                variant="span"
                color="muted"
              >
                No notifications yet
              </Typography>
            </div>
          ) : (
            notifications.map((notification) => (
              <div
                key={notification.id}
                className={`p-3 border-b border-gray-100 cursor-pointer hover:bg-gray-50 transition-colors ${
                  !notification.is_read ? "bg-blue-50" : ""
                }`}
                onClick={() => handleNotificationClick(notification)}
              >
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 mt-1">
                    {notification.is_read ? (
                      <CheckCheck className="h-4 w-4 text-gray-400" />
                    ) : (
                      <Check className="h-4 w-4 text-blue-500" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <Typography
                      variant="span"
                      size="sm"
                      className="font-medium block"
                    >
                      {notification.title}
                    </Typography>
                    <Typography
                      variant="span"
                      size="xs"
                      color="muted"
                      className="block mt-1"
                    >
                      {notification.message}
                    </Typography>
                    <Typography
                      variant="span"
                      size="xs"
                      color="muted"
                      className="block mt-1"
                    >
                      {new Date(notification.created_at).toLocaleDateString()}
                    </Typography>
                  </div>
                </div>
              </div>
            ))
          )}

          {isLoading && (
            <div className="p-4 text-center">
              <Loader2 className="h-4 w-4 animate-spin mx-auto" />
            </div>
          )}

          {hasNextPage && !isLoading && (
            <div className="p-4 text-center">
              <Button
                variant="outline"
                size="sm"
                onClick={loadMore}
                className="w-full"
              >
                Load More
              </Button>
            </div>
          )}
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
