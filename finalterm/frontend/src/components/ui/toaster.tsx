"use client";
import {
  Toast,
  ToastClose,
  ToastDescription,
  ToastProvider,
  ToastTitle,
  ToastViewport,
  ToastIcon,
} from "@/components/ui/toast";
import { useToast } from "@/components/hooks/use-toast";

export function Toaster() {
  const { toasts } = useToast();

  return (
    <ToastProvider>
      {toasts.map(function ({ id, description, action, variant, ...props }) {
        return (
          <Toast
            key={id}
            variant={variant}
            {...props}
          >
            <div className="flex items-center justify-between w-full">
              <div className="flex items-center space-x-3">
                <ToastIcon variant={variant || "default"} />
                {description && (
                  <ToastDescription className="text-sm">{description}</ToastDescription>
                )}
              </div>
              {action}
            </div>
            <ToastClose />
          </Toast>
        );
      })}
      <ToastViewport />
    </ToastProvider>
  );
}
