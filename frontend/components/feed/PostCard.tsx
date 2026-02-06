'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { Heart, MessageCircle, Repeat2 } from 'lucide-react';
import { Avatar } from '@/components/ui';
import { api } from '@/lib/api';
import { Post } from '@/types';

const TIMES = {
    MINUTE: 60,
    HOUR: 3600,
    DAY: 86400,
    WEEK: 604800,
};

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

interface PostCardProps {
    post: Post;
    onView?: (postId: number) => void;
}

export function PostCard({ post, onView }: PostCardProps) {
    const [liked, setLiked] = useState(post.is_liked);
    const [likeCount, setLikeCount] = useState(post.like_count);
    const cardRef = useRef<HTMLElement>(null);
    const hasTrackedView = useRef(false);

    // Intersection Observer for view tracking
    useEffect(() => {
        if (!onView || hasTrackedView.current) return;

        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    // 50% visible = viewed
                    if (entry.isIntersecting && entry.intersectionRatio >= 0.5) {
                        if (!hasTrackedView.current) {
                            hasTrackedView.current = true;
                            onView(post.id);
                        }
                    }
                });
            },
            { threshold: 0.5 },
        );

        if (cardRef.current) {
            observer.observe(cardRef.current);
        }

        return () => observer.disconnect();
    }, [post.id, onView]);

    const handleLike = async () => {
        setLiked(!liked);
        setLikeCount(liked ? likeCount - 1 : likeCount + 1);

        try {
            await api.toggleLike(post.id);
        } catch {
            setLiked(liked);
            setLikeCount(post.like_count);
        }
    };

    return (
        <article
            ref={cardRef}
            className="p-4 border-b border-gray-200 hover:bg-gray-50 transition-colors"
        >
            <div className="flex gap-3">
                {/* Avatar */}
                <Link href={`/profile/${post.author.username}`} className="flex-shrink-0">
                    <Avatar
                        username={post.author.username}
                        src={post.author.profile_image}
                        size="md"
                    />
                </Link>

                {/* Content */}
                <div className="flex-1 min-w-0">
                    {/* Header */}
                    <div className="flex items-start justify-between">
                        <Link href={`/profile/${post.author.username}`} className="min-w-0 group">
                            <p className="font-semibold truncate group-hover:underline">
                                {post.author.display_name || post.author.username}
                            </p>
                            <p className="text-gray-500 text-sm truncate">
                                @{post.author.username}
                            </p>
                        </Link>

                        <Link
                            href={`/post/${post.id}`}
                            className="text-gray-500 text-sm hover:underline flex-shrink-0 ml-2"
                        >
                            {formatTimeAgo(post.created_at)}
                        </Link>
                    </div>

                    {/* Body */}
                    <p className="mt-2 text-gray-900">{post.body}</p>

                    {/* Tags */}
                    {post.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2">
                            {post.tags.map((tag) => (
                                <Link
                                    key={tag.id}
                                    href={`/explore?tag=${tag.name}`}
                                    className="text-blue-500 text-sm hover:underline"
                                >
                                    #{tag.name}
                                </Link>
                            ))}
                        </div>
                    )}

                    {/* Actions */}
                    <div className="flex gap-6 mt-3 text-gray-500">
                        <button
                            onClick={handleLike}
                            className={`flex items-center gap-1 text-sm hover:text-red-500 transition-colors ${
                                liked ? 'text-red-500' : ''
                            }`}
                        >
                            <Heart size={18} fill={liked ? 'currentColor' : 'none'} />
                            <span>{likeCount}</span>
                        </button>

                        <button className="flex items-center gap-1 text-sm hover:text-blue-500 transition-colors">
                            <MessageCircle size={18} />
                            <span>{post.reply_count}</span>
                        </button>

                        <button className="flex items-center gap-1 text-sm hover:text-green-500 transition-colors">
                            <Repeat2 size={18} />
                            <span>{post.repost_count}</span>
                        </button>
                    </div>
                </div>
            </div>
        </article>
    );
}
