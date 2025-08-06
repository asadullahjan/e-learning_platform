import { cn } from "@/lib/utils";
import { cva, VariantProps } from "class-variance-authority";

const typographyVariants = cva("text", {
  variants: {
    variant: {
      default: "",
      p: "text-sm",
      span: "text-sm",
      label: "text-sm",
      h1: "lg:text-4xl text-2xl font-bold",
      h2: "lg:text-3xl text-2xl font-bold",
      h3: "lg:text-2xl text-xl font-bold",
      h4: "lg:text-xl text-lg font-bold",
      h5: "lg:text-lg text-base font-bold",
      h6: "lg:text-base text-sm font-bold",
    },
    color: {
      default: "",
      primary: "text-primary",
      secondary: "text-secondary",
      muted: "text-muted",
      accent: "text-accent",
      destructive: "text-destructive",
      success: "text-success",
      warning: "text-warning",
      info: "text-info",
    },
    size: {
      default: "",
      xs: "text-xs",
      sm: "text-sm",
      md: "text-md",
      lg: "text-lg",
      xl: "text-xl",
      "2xl": "text-2xl",
    },
    defaultVariants: {
      variant: "default",
      color: "default",
      size: "default",
    },
  },
});

const Typography = ({
  className,
  variant,
  color,
  size,
  ...props
}: React.HTMLAttributes<HTMLDivElement> & VariantProps<typeof typographyVariants>) => {
  return (
    <div
      className={cn(typographyVariants({ variant, color, size, className }))}
      {...props}
    />
  );
};

export default Typography;
