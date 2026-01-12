"use client";
import { Dialog, DialogContent, DialogTitle } from "./dialog";
import { Button } from "./button";
import { AlertTriangle, Info, HelpCircle, AlertCircle } from "lucide-react";
import Typography from "./Typography";

interface ConfirmDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  description: string;
  confirmText?: string;
  cancelText?: string;
  variant?: "danger" | "warning" | "info" | "default";
  isLoading?: boolean;
}

export default function ConfirmDialog({
  isOpen,
  onClose,
  onConfirm,
  title,
  description,
  confirmText = "Confirm",
  cancelText = "Cancel",
  variant = "default",
  isLoading = false,
}: ConfirmDialogProps) {
  const handleConfirm = () => {
    onConfirm();
    onClose();
  };

  const getVariantStyles = () => {
    switch (variant) {
      case "danger":
        return {
          icon: <AlertTriangle className="w-5 h-5 text-red-500" />,
          confirmButton: "bg-red-600 hover:bg-red-700 text-white",
          titleColor: "text-red-900",
        };
      case "warning":
        return {
          icon: <AlertCircle className="w-5 h-5 text-yellow-500" />,
          confirmButton: "bg-yellow-600 hover:bg-yellow-700 text-white",
          titleColor: "text-yellow-900",
        };
      case "info":
        return {
          icon: <Info className="w-5 h-5 text-blue-500" />,
          confirmButton: "bg-blue-600 hover:bg-blue-700 text-white",
          titleColor: "text-blue-900",
        };
      default:
        return {
          icon: <HelpCircle className="w-5 h-5 text-gray-500" />,
          confirmButton: "bg-gray-600 hover:bg-gray-700 text-white",
          titleColor: "text-gray-900",
        };
    }
  };

  const styles = getVariantStyles();

  return (
    <Dialog
      open={isOpen}
      onOpenChange={onClose}
    >
      <DialogContent>
        <div className="flex items-center gap-3">
          {styles.icon}
          <DialogTitle className={`text-sm font-medium ${styles.titleColor}`}>{title}</DialogTitle>
        </div>

        <div className="space-y-4">
          <Typography
            variant="p"
            size="sm"
            className="text-gray-700"
          >
            {description}
          </Typography>

          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={onClose}
              disabled={isLoading}
              size="sm"
            >
              {cancelText}
            </Button>
            <Button
              type="button"
              onClick={handleConfirm}
              disabled={isLoading}
              size="sm"
              className={styles.confirmButton}
            >
              {isLoading ? "Loading..." : confirmText}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
