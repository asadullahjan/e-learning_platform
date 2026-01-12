import * as React from "react";
import { cn } from "@/lib/utils";
import * as _Select from "@radix-ui/react-select";
import { ChevronDownIcon } from "lucide-react";

const Select = _Select.Root;
const SelectValue = _Select.Value;

const SelectTrigger = ({ children, className, ...props }: _Select.SelectTriggerProps) => {
  return (
    <_Select.Trigger
      {...props}
      className={cn(
        "w-full border border-accent cursor-pointer rounded-md px-4 py-2 flex items-center justify-between outline-primary focus:outline-primary",
        className
      )}
    >
      {children}
      <_Select.Icon>
        <ChevronDownIcon className="w-4 h-4 ml-2" />
      </_Select.Icon>
    </_Select.Trigger>
  );
};

const SelectContent = ({ children, className, ...props }: _Select.SelectContentProps) => {
  return (
    <_Select.Content
      {...props}
      className={cn(
        "overflow-hidden bg-white border border-accent rounded-md shadow-lg",
        className
      )}
      position="popper"
      sideOffset={4}
    >
      <_Select.Viewport className="p-1 w-[var(--radix-select-trigger-width)]">
        {children}
      </_Select.Viewport>
    </_Select.Content>
  );
};

const SelectItem = React.forwardRef<
  React.ElementRef<typeof _Select.Item>,
  React.ComponentPropsWithoutRef<typeof _Select.Item>
>(({ className, children, ...props }, ref) => {
  return (
    <_Select.Item
      ref={ref}
      className={cn(
        "relative flex w-full cursor-pointer select-none items-center rounded-sm px-4 py-2 text-sm outline-none focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50",
        className
      )}
      {...props}
    >
      <_Select.ItemText>{children}</_Select.ItemText>
    </_Select.Item>
  );
});
SelectItem.displayName = _Select.Item.displayName;

export { Select, SelectContent, SelectItem, SelectTrigger, SelectValue };
