import { toast } from "@/components/hooks/use-toast";
import { ToastActionElement } from "@/components/ui/toast";

export const showToast = {
  success: (message: string, action?: ToastActionElement) => {
    toast({
      description: message,
      variant: "success",
      action: action,
    });
  },

  error: (message: string, action?: ToastActionElement) => {
    toast({
      description: message,
      variant: "destructive",
      action: action,
    });
  },

  warning: (message: string, action?: ToastActionElement) => {
    toast({
      description: message,
      variant: "warning",
      action: action,
    });
  },

  info: (message: string, action?: ToastActionElement) => {
    toast({
      description: message,
      variant: "default",
      action: action,
    });
  },
};
