'use client';

import { useState, useEffect } from 'react';
import { Post } from '@/types';
import { api } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';
import { useViewTracking } from '@/hooks/useViewTracking';
import { PostCard } from './PostCard';
import { PostSkeleton } from './PostSkeleton';
import Link from 'next/link';

interface PostListProps {
    type: 'following' | 'popular';
}

export function PostList({ type }: PostListProps) {
    const { user } = useAuth();
    const { markViewed } = useViewTracking();
    const [posts, setPosts] = useState<Post[] | null>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        let cancelled = false;

        const fetchPosts = async () => {
            try {
                if (type === 'following' && !user) {
                    setPosts([]);
                    return;
                }

                const data =
                    type === 'following'
                        ? await api.getFeed()
                        : await api.getPosts({ sort_by: 'popular' });

                if (!cancelled) {
                    setPosts(data.items);
                }
            } catch (err) {
                if (!cancelled) {
                    setError(err instanceof Error ? err.message : 'Failed to load');
                }
            }
        };

        fetchPosts();

        return () => {
            cancelled = true;
        };
    }, [type, user]);

    if (posts === null && !error) {
        return (
            <>
                <PostSkeleton />
                <PostSkeleton />
                <PostSkeleton />
                <PostSkeleton />
            </>
        );
    }

    if (error) {
        return (
            <div className="p-8 text-center">
                <p className="text-red-500 mb-2">Failed to load posts</p>
                <p className="text-gray-500 text-sm">{error}</p>
            </div>
        );
    }

    if (type === 'following' && !user) {
        return (
            <div className="p-8 text-center text-gray-500">
                <p className="mb-2">Log in to see posts from people you follow</p>
                <Link href="/login" className="text-blue-500 hover:underline">
                    Log in
                </Link>
            </div>
        );
    }

    if (posts && posts.length === 0) {
        return (
            <div className="p-8 text-center text-gray-500">
                {type === 'following'
                    ? 'No posts yet. Follow some users to see their posts!'
                    : 'No posts yet. Be the first to post!'}
            </div>
        );
    }

    return (
        <>
            {posts?.map((post) => (
                <PostCard
                    key={post.id}
                    post={post}
                    onView={type === 'following' ? markViewed : undefined}
                />
            ))}
        </>
    );
}
