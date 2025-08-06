import { cn } from "@/lib/utils";

const Input = ({ className, ...props }: React.InputHTMLAttributes<HTMLInputElement>) => {
  return (
    <input
      className={cn(
        " disabled:cursor-not-allowed disabled:opacity-50",
        "w-full px-4 py-2 border border-gray-300 rounded-md bg-white outline-primary/40 focus:outline-1",
        className
      )}
      {...props}
    />
  );
};

export default Input;
