'use client';

import { useState } from 'react';
import { FeedTabs, PostComposer, PostList } from '@/components/feed';
import { useAuth } from '@/context/AuthContext';
import { PostSkeleton } from '@/components/feed/PostSkeleton';

export default function HomePage() {
    const { user, loading: authLoading } = useAuth();
    const [activeTab, setActiveTab] = useState<'following' | 'popular'>('following');
    const [refreshKey, setRefreshKey] = useState(0);

    const handlePostCreated = () => {
        setRefreshKey((prev) => prev + 1);
    };

    // Show skeleton while auth is loading
    if (authLoading) {
        return (
            <div>
                <div className="sticky top-0 bg-white/80 backdrop-blur-sm border-b border-gray-200 z-10">
                    <h1 className="px-4 py-3 text-xl font-bold">Home</h1>
                </div>
                <PostSkeleton />
                <PostSkeleton />
                <PostSkeleton />
            </div>
        );
    }

    return (
        <div>
            {/* Sticky header */}
            <div className="sticky top-0 bg-white/80 backdrop-blur-sm border-b border-gray-200 z-10">
                <h1 className="px-4 py-3 text-xl font-bold">Home</h1>
                <FeedTabs activeTab={activeTab} onTabChange={setActiveTab} />
            </div>

            {/* Composer */}
            <PostComposer onPostCreated={handlePostCreated} />

            {/* Divider */}
            <div className="h-2 bg-gray-100" />

            {/* Posts */}
            <PostList key={`${activeTab}-${refreshKey}`} type={activeTab} />
        </div>
    );
}
