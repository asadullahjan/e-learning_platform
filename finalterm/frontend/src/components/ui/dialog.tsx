import * as DialogPrimitive from "@radix-ui/react-dialog";
import { DialogClose } from "@radix-ui/react-dialog";
import { Button } from "./button";
import { X } from "lucide-react";

const Dialog = DialogPrimitive.Root;
const DialogTrigger = DialogPrimitive.Trigger;
const DialogPortal = DialogPrimitive.Portal;

const DialogOverlay = ({ children, ...props }: DialogPrimitive.DialogOverlayProps) => {
  return (
    <DialogPrimitive.Overlay
      className="fixed inset-0 bg-black/70"
      {...props}
    >
      {children}
    </DialogPrimitive.Overlay>
  );
};

const DialogContent = ({ children, ...props }: DialogPrimitive.DialogContentProps) => {
  return (
    <DialogPortal>
      <DialogOverlay />
      <DialogPrimitive.Content
        className="z-50 p-6 fixed inset-0 top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 rounded-lg max-w-lg max-h-[60vh] w-full h-fit m-1 bg-white overflow-y-auto"
        {...props}
      >
        {children}
        <DialogClose asChild>
          <Button
            variant="ghost"
            className="absolute top-2 right-2"
          >
            <X className="w-4 h-4" />
          </Button>
        </DialogClose>
      </DialogPrimitive.Content>
    </DialogPortal>
  );
};

const DialogTitle = ({ children, ...props }: DialogPrimitive.DialogTitleProps) => {
  return (
    <DialogPrimitive.Title
      className="text-lg font-semibold mb-3"
      {...props}
    >
      {children}
    </DialogPrimitive.Title>
  );
};

const DialogDescription = ({ children, ...props }: DialogPrimitive.DialogDescriptionProps) => {
  return (
    <DialogPrimitive.Description
      className="text-sm text-gray-500 mb-5"
      {...props}
    >
      {children}
    </DialogPrimitive.Description>
  );
};

export { Dialog, DialogTrigger, DialogContent, DialogTitle, DialogDescription, DialogPortal };
