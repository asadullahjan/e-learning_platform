import * as TabsPrimitive from "@radix-ui/react-tabs";
import React from "react";
import { cn } from "@/lib/utils";

const TabsContent = TabsPrimitive.Content;

const Tabs = TabsPrimitive.Root;

const TabsList = React.forwardRef<HTMLDivElement, TabsPrimitive.TabsListProps>(
  ({ className, ...props }, ref) => (
    <TabsPrimitive.List
      ref={ref}
      className={cn("flex h-10 items-center gap-1 rounded-md bg-muted p-1 mb-4", className)}
      {...props}
    />
  )
);

const TabsTrigger = React.forwardRef<HTMLButtonElement, TabsPrimitive.TabsTriggerProps>(
  ({ className, ...props }, ref) => (
    <TabsPrimitive.Trigger
      ref={ref}
      className={cn(
        "px-3 py-1.5 text-sm rounded-md cursor-pointer transition-colors",
        "data-[state=active]:bg-background data-[state=active]:text-foreground",
        "hover:bg-muted/50",
        className
      )}
      {...props}
    />
  )
);

export { Tabs, TabsList, TabsTrigger, TabsContent };
