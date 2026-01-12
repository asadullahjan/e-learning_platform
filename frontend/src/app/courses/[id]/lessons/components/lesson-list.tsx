"use client";
import { useLoadMore } from "@/components/hooks/useLoadMore";
import { LoadMoreButton } from "@/components/ui/load-more-button";
import { LessonListItem } from "./lesson-list-item";
import { CourseLesson } from "@/lib/types";
import { lessonService } from "@/services/lessonService";
import Typography from "@/components/ui/Typography";
import { useEffect, useState, useCallback } from "react";
import { LessonFormDialog } from "./lesson-form-dialog";

interface LessonListProps {
  courseId: number;
  initialLessons?: CourseLesson[];
  initialHasNextPage?: boolean;
  isTeacher?: boolean;
}

export function LessonList({
  courseId,
  initialLessons = [],
  initialHasNextPage = false,
  isTeacher = false,
}: LessonListProps) {
  const [page, setPage] = useState(1);
  const pageSize = 12;

  const loadMoreLessons = useCallback(
    async (isInitialLoad = false) => {
      // For initial load, use page 1, for load more use page + 1
      const currentPage = isInitialLoad ? 1 : page + 1;

      const response = await lessonService.getCourseLessons(courseId, {
        page: String(currentPage),
        page_size: String(pageSize),
      });

      if (isInitialLoad) {
        // Initial load
        setPage(1);
      } else {
        // Load more
        setPage((prev) => prev + 1);
      }

      return {
        data: response.results,
        hasNextPage: !!response.next,
      };
    },
    [courseId, page, pageSize]
  );

  const {
    data: lessons,
    isLoading,
    hasNextPage,
    loadMore,
    error,
  } = useLoadMore({
    initialData: initialLessons,
    hasNextPage: initialHasNextPage,
    onLoadMore: loadMoreLessons,
    pageSize,
  });

  if (error) {
    return (
      <div className="text-center py-8">
        <Typography
          variant="p"
          color="error"
        >
          Error loading lessons: {error}
        </Typography>
      </div>
    );
  }

  if (lessons.length === 0 && !isLoading) {
    return (
      <div className="text-center py-8">
        <Typography
          variant="p"
          color="muted"
        >
          No lessons available for this course yet.
        </Typography>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Add Lesson Button for Teachers */}
      {isTeacher && (
        <div className="flex justify-between items-center">
          <Typography variant="h3">Course Lessons</Typography>
          <LessonFormDialog courseId={courseId} />
        </div>
      )}

      <div className="flex flex-col space-y-4">
        {lessons.map((lesson) => (
          <LessonListItem
            key={lesson.id}
            lesson={lesson}
            courseId={courseId}
            isTeacher={isTeacher}
          />
        ))}
      </div>

      <LoadMoreButton
        onClick={loadMore}
        isLoading={isLoading}
        hasNextPage={hasNextPage}
      />
    </div>
  );
}
