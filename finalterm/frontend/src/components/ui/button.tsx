import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { Spinner } from "./spinner";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium cursor-pointer transition-all duration-300 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/70",
        ghost: "bg-transparent text-primary hover:bg-primary/10",
        outline: "bg-transparent text-primary border border-primary hover:bg-primary/10",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/70",
      },
      size: {
        default: "h-10 px-4 py-2",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  loading?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, loading, children, variant, size, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      >
        {loading ? <Spinner size={size} /> : children}
      </button>
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };
