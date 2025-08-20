import { useState, useCallback, useEffect, useRef } from "react";

interface UseLoadMoreOptions<T> {
  initialData?: T[];
  hasNextPage?: boolean;
  onLoadMore: (isInitialLoad?: boolean) => Promise<{ data: T[]; hasNextPage: boolean }>;
  pageSize?: number;
}

interface UseLoadMoreReturn<T> {
  data: T[];
  isLoading: boolean;
  hasNextPage: boolean;
  loadMore: () => Promise<void>;
  refresh: () => Promise<void>;
  error: string | null;
}

export function useLoadMore<T>({
  initialData = [],
  hasNextPage: initialHasNextPage = false,
  onLoadMore,
  pageSize = 10,
}: UseLoadMoreOptions<T>): UseLoadMoreReturn<T> {
  const [data, setData] = useState<T[]>(initialData);
  const [isLoading, setIsLoading] = useState(false);
  const [hasNextPage, setHasNextPage] = useState(initialHasNextPage);
  const [error, setError] = useState<string | null>(null);
  const isInitialized = useRef(false);

  const loadMore = useCallback(async () => {
    if (isLoading || !hasNextPage) return;

    setIsLoading(true);
    setError(null);

    try {
      const result = await onLoadMore();
      setData((prev) => [...prev, ...result.data]);
      setHasNextPage(result.hasNextPage);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load more data");
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, hasNextPage, onLoadMore]);

  const refresh = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await onLoadMore();
      setData(result.data);
      setHasNextPage(result.hasNextPage);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to refresh data");
    } finally {
      setIsLoading(false);
    }
  }, [onLoadMore]);

  // Set initial data and fetch if needed
  useEffect(() => {
    if (!isInitialized.current) {
      isInitialized.current = true;
      setData(initialData);
      setHasNextPage(initialHasNextPage);
      
      // If no initial data, fetch the first page
      if (initialData.length === 0 && onLoadMore) {
        const fetchInitial = async () => {
          setIsLoading(true);
          try {
            // Pass isInitialLoad=true for the first fetch
            const result = await onLoadMore(true);
            setData(result.data);
            setHasNextPage(result.hasNextPage);
          } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to load initial data");
          } finally {
            setIsLoading(false);
          }
        };
        fetchInitial();
      }
    }
  }, [initialData, onLoadMore]);

  return {
    data,
    isLoading,
    hasNextPage,
    loadMore,
    refresh,
    error,
  };
}
