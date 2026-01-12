import { toast } from "@/components/hooks/use-toast";
import { ToastActionElement } from "@/components/ui/toast";

export const showToast = {
  success: (message: string, action?: ToastActionElement) => {
    toast({
      description: message,
      variant: "success",
      action: action,
      duration: 4000,
    });
  },

  error: (message: string, action?: ToastActionElement) => {
    toast({
      description: message,
      variant: "destructive",
      action: action,
      duration: 6000,
    });
  },

  warning: (message: string, action?: ToastActionElement) => {
    toast({
      description: message,
      variant: "warning",
      action: action,
      duration: 5000,
    });
  },

  info: (message: string, action?: ToastActionElement) => {
    toast({
      description: message,
      variant: "default",
      action: action,
      duration: 3500,
    });
  },
};
