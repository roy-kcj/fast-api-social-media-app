'use client';

import { api } from '@/lib/api';
import { Post } from '@/types';
import Link from 'next/link';
import { useState } from 'react';
import { Avatar } from '../ui';

export const TIMES = {
    MINUTE: 60,
    HOUR: 3600,
    DAY: 86400,
    WEEK: 604800,
};

interface PostCardProps {
    post: Post;
}

function formatTimeAgo(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (seconds < TIMES.MINUTE) return 'just now';
    if (seconds < TIMES.HOUR) return `${Math.floor(seconds / TIMES.MINUTE)}m`;
    if (seconds < TIMES.DAY) return `${Math.floor(seconds / TIMES.HOUR)}h`;
    if (seconds < TIMES.WEEK) return `${Math.floor(seconds / TIMES.DAY)}d`;

    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

export function PostCard({ post }: PostCardProps) {
    const [liked, setLiked] = useState(post.is_liked);
    const [likeCount, setLikeCount] = useState(post.like_count);

    const handleLike = async () => {
        // Optimistic update
        setLiked(!liked);
        setLikeCount(liked ? likeCount - 1 : likeCount + 1);

        try {
            await api.toggleLike(post.id);
        } catch {
            // Revert on error
            setLiked(liked);
            setLikeCount(post.like_count);
        }
    };

    return (
        <article className="p-4 border-b border-gray-200 hover:bg-gray-50 transition-colors">
            {/* Header: Avatar + Info */}
            <div className="flex gap-3">
                {/* Avatar */}
                <Link href={`/profile/${post.author.username}`} className="shrink-0">
                    <Avatar
                        username={post.author.username}
                        src={post.author.profile_image}
                        size="md"
                    />
                </Link>

                <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between">
                        {/* Left: name + username */}
                        <Link
                            href={`/profile/${post.author.username}`}
                            className="flex flex-col text-sm min-w-0 group"
                        >
                            <span className="font-semibold truncate group-hover:underline">
                                {post.author.display_name || post.author.username}
                            </span>
                            <span className="text-gray-500 truncate">@{post.author.username}</span>
                        </Link>

                        {/* Right: time */}
                        <Link
                            href={`/post/${post.id}`}
                            className="text-gray-500 text-sm hover:underline shrink-0 ml-2"
                        >
                            {formatTimeAgo(post.created_at)}
                        </Link>
                    </div>

                    {/* Content Body */}
                    <div className="flex-1 min-w-0">
                        {/* Body */}
                        {/* Actions */}
                    </div>
                </div>
            </div>
        </article>
    );
}
