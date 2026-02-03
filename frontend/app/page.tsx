'use client';

import { useState } from 'react';
import { FeedTabs } from '@/components/feed/FeedTabs';
import { PostCard } from '@/components/feed/PostCard';
import { PostSkeleton } from '@/components/feed/PostSkeleton';
import { Post } from '@/types';

const MOCK_POSTS: Post[] = [
    {
        id: 1,
        title: null,
        body: "Just finished building my first FastAPI project! 🚀 The developer experience is amazing compared to other frameworks I've used.",
        author: {
            id: 1,
            username: 'johndoe',
            display_name: 'John Doe',
            profile_image: '',
            is_verified: false,
        },
        tags: [
            { id: 1, name: 'python' },
            { id: 2, name: 'fastapi' },
        ],
        like_count: 42,
        reply_count: 5,
        repost_count: 3,
        is_liked: false,
        parent_id: null,
        repost_of_id: null,
        created_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(), // 30 min ago
        updated_at: new Date().toISOString(),
    },
    {
        id: 2,
        title: null,
        body: 'Hot take: Tailwind CSS is the best thing to happen to frontend development in years. Fight me. 😤',
        author: {
            id: 2,
            username: 'janedeveloper',
            display_name: 'Jane Developer',
            profile_image: 'https://i.pravatar.cc/150?u=jane', // Fake avatar
            is_verified: true,
        },
        tags: [
            { id: 3, name: 'tailwind' },
            { id: 4, name: 'css' },
        ],
        like_count: 128,
        reply_count: 24,
        repost_count: 12,
        is_liked: true,
        parent_id: null,
        repost_of_id: null,
        created_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(), // 2 hours ago
        updated_at: new Date().toISOString(),
    },
    {
        id: 3,
        title: null,
        body: "Learning Next.js App Router and it's changing how I think about React applications. Server components are a game changer for performance.",
        author: {
            id: 3,
            username: 'reactfan',
            display_name: null, // No display name - should show username
            profile_image: '',
            is_verified: false,
        },
        tags: [],
        like_count: 8,
        reply_count: 2,
        repost_count: 0,
        is_liked: false,
        parent_id: null,
        repost_of_id: null,
        created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3).toISOString(), // 3 days ago
        updated_at: new Date().toISOString(),
    },
];

export default function HomePage() {
    const [activeTab, setActiveTab] = useState<'following' | 'popular'>('following');
    const [showSkeleton, setShowSkeleton] = useState(false);

    return (
        <div>
            <div className="sticky top-0 bg-white/80 backdrop-blur-sm border-b border-gray-200 z-10">
                <FeedTabs activeTab={activeTab} onTabChange={setActiveTab} />
            </div>

            {/* Toggle skeleton for testing */}
            <div className="p-4 border-b border-gray-200 bg-gray-50">
                <button
                    onClick={() => setShowSkeleton(!showSkeleton)}
                    className="text-sm text-blue-500 hover:underline"
                >
                    Toggle skeleton: {showSkeleton ? 'ON' : 'OFF'}
                </button>
            </div>

            {showSkeleton ? (
                <>
                    <PostSkeleton />
                    <PostSkeleton />
                    <PostSkeleton />
                </>
            ) : (
                <>
                    {MOCK_POSTS.map((post) => (
                        <PostCard key={post.id} post={post} />
                    ))}
                </>
            )}
        </div>
    );
}
