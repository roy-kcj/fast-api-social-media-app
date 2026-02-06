"use client";

import { useEffect, useRef, useCallback } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

// Debounce time before sending views to server
const FLUSH_DELAY_MS = 2000;

// Minimum visibility ratio to count as "viewed"
const VISIBILITY_THRESHOLD = 0.5;

export function useViewTracking() {
  const { user } = useAuth();
  const viewedPostIds = useRef<Set<number>>(new Set());
  const pendingPostIds = useRef<Set<number>>(new Set());
  const flushTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Flush pending views to server
  const flushViews = useCallback(async () => {
    if (pendingPostIds.current.size === 0 || !user) return;

    const postIds = Array.from(pendingPostIds.current);
    pendingPostIds.current.clear();

    try {
      await api.trackViews(postIds);
    } catch (err) {
      console.error("Failed to track views:", err);
      // Re-add failed views to pending
      postIds.forEach((id) => pendingPostIds.current.add(id));
    }
  }, [user]);

  // Schedule flush with debounce
  const scheduleFlush = useCallback(() => {
    if (flushTimeoutRef.current) {
      clearTimeout(flushTimeoutRef.current);
    }
    flushTimeoutRef.current = setTimeout(flushViews, FLUSH_DELAY_MS);
  }, [flushViews]);

  // Mark a post as viewed
  const markViewed = useCallback(
    (postId: number) => {
      if (!user) return;
      if (viewedPostIds.current.has(postId)) return;

      viewedPostIds.current.add(postId);
      pendingPostIds.current.add(postId);
      scheduleFlush();
    },
    [user, scheduleFlush]
  );

  // Flush on unmount or page change
  useEffect(() => {
    return () => {
      if (flushTimeoutRef.current) {
        clearTimeout(flushTimeoutRef.current);
      }
      // Immediate flush on cleanup
      if (pendingPostIds.current.size > 0 && user) {
        const postIds = Array.from(pendingPostIds.current);
        api.trackViews(postIds).catch(console.error);
      }
    };
  }, [user]);

  return { markViewed };
}