"use client";

import { Button } from "@/components/ui/button";
import Input from "@/components/ui/Input";
import {
  Select,
  SelectContent,
  SelectTrigger,
  SelectItem,
  SelectValue,
} from "@/components/ui/select";
import { SearchIcon, XIcon } from "lucide-react";
import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

const orderingOptions = {
  "-published_at": "Newest",
  published_at: "Oldest",
} as const;

type OrderingKey = keyof typeof orderingOptions;
type OrderingLabel = (typeof orderingOptions)[OrderingKey];

export default function Filter() {
  const [search, setSearch] = useState("");
  const [ordering, setOrdering] = useState<OrderingLabel>(orderingOptions["-published_at"]);
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const search = searchParams.get("search");
    const orderingParam = searchParams.get("ordering") as OrderingKey;
    const ordering = orderingOptions[orderingParam] || orderingOptions["-published_at"];

    setSearch(search || "");
    setOrdering(ordering);
  }, [searchParams]);

  const updateUrl = (key: string, value: string) => {
    const params = new URLSearchParams(searchParams);
    if (value) {
      params.set(key, value);
    } else {
      params.delete(key);
    }
    router.push(`?${params.toString()}`);
  };

  return (
    <div className="flex flex-row justify-between gap-2">
      <div className="flex flex-row gap-2">
        <label
          htmlFor="search"
          className="sr-only"
        >
          Search
        </label>
        <Input
          id="search"
          placeholder="Search"
          className="max-w-xs"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              updateUrl("search", search);
            }
          }}
          onBlur={() => {
            updateUrl("search", search);
          }}
        />
        {search && (
          <Button
            variant="outline"
            className="max-w-xs"
            onClick={() => {
              updateUrl("search", search);
            }}
          >
            <SearchIcon className="w-4 h-4" />
          </Button>
        )}
      </div>
      <div>
        <Select
          value={ordering}
          onValueChange={(value) => {
            const newOrdering = orderingOptions[value as OrderingKey];
            setOrdering(newOrdering);
            updateUrl("ordering", value);
          }}
        >
          <SelectTrigger className="max-w-xs text-sm">
            <SelectValue>{ordering}</SelectValue>
          </SelectTrigger>
          <SelectContent className="max-w-xs">
            {Object.entries(orderingOptions).map(([key, label]) => (
              <SelectItem
                key={key}
                value={key}
              >
                {label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}
