import { Button } from "./button";
import { Spinner } from "./spinner";
import Typography from "./Typography";

interface LoadMoreButtonProps {
  onClick: () => void;
  isLoading: boolean;
  hasNextPage: boolean;
  className?: string;
}

export function LoadMoreButton({
  onClick,
  isLoading,
  hasNextPage,
  className = "",
}: LoadMoreButtonProps) {
  if (!hasNextPage) {
    return null;
  }

  return (
    <div className={`flex justify-center mt-6 ${className}`}>
      <Button
        onClick={onClick}
        disabled={isLoading}
        variant="outline"
        className="min-w-[120px]"
      >
        {isLoading ? (
          <>
            <Spinner size="sm" />
            <Typography variant="span">Loading...</Typography>
          </>
        ) : (
          <Typography variant="span">Load More</Typography>
        )}
      </Button>
    </div>
  );
}
