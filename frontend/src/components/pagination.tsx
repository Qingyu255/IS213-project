"use client";

import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight } from "lucide-react";

type PaginationProps = {
  hasMore?: boolean;
  total?: number;
  limit: number;
  currentPage: number;
  onPageChange: (page: number) => void;
};

export function Pagination({
  hasMore,
  total,
  limit,
  currentPage,
  onPageChange,
}: PaginationProps) {
  let totalPages;
  if (total != null) {
    totalPages = Math.ceil(total / limit);
  }

  return (
    <div className="flex justify-center items-center space-x-2 mt-8">
      <Button
        variant="outline"
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
      >
        <ChevronLeft className="h-4 w-4 mr-2" /> Previous
      </Button>
      <span className="text-muted-foreground">
        Page {currentPage}
        {totalPages && `of ${totalPages}`}
      </span>
      <Button
        variant="outline"
        onClick={() => onPageChange(currentPage + 1)}
        disabled={!hasMore || currentPage === totalPages}
      >
        Next <ChevronRight className="h-4 w-4 ml-2" />
      </Button>
    </div>
  );
}
