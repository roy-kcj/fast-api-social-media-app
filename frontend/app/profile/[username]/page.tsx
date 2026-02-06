'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { Avatar } from '@/components/ui';
import { PostCard } from '@/components/feed/PostCard';
import { PostSkeleton } from '@/components/feed/PostSkeleton';
import { useAuth } from '@/context/AuthContext';
import { api } from '@/lib/api';
import { UserOut, Post } from '@/types';

export default function ProfilePage() {
    const params = useParams();
    const username = params.username as string;
    const { user: currentUser } = useAuth();

    const [user, setUser] = useState<UserOut | null>(null);
    const [posts, setPosts] = useState<Post[] | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [followLoading, setFollowLoading] = useState(false);

    const isOwnProfile = currentUser?.username === username;

    useEffect(() => {
        let cancelled = false;

        const fetchProfile = async () => {
            try {
                const [userData, postsData] = await Promise.all([
                    api.getUser(username),
                    api.getUserPosts(username),
                ]);

                if (!cancelled) {
                    setUser(userData);
                    setPosts(postsData.items);
                }
            } catch (err) {
                if (!cancelled) {
                    setError(err instanceof Error ? err.message : 'Failed to load profile');
                }
            } finally {
                if (!cancelled) setLoading(false);
            }
        };

        fetchProfile();

        return () => {
            cancelled = true;
        };
    }, [username]);

    const handleFollow = async () => {
        if (!user || followLoading) return;

        setFollowLoading(true);

        try {
            if (user.is_following) {
                const result = await api.unfollowUser(username);
                setUser({
                    ...user,
                    is_following: false,
                    follower_count: result.follower_count,
                });
            } else {
                const result = await api.followUser(username);
                setUser({
                    ...user,
                    is_following: true,
                    follower_count: result.follower_count,
                });
            }
        } catch (err) {
            console.error('Follow error:', err);
        } finally {
            setFollowLoading(false);
        }
    };

    if (loading) {
        return (
            <div>
                {/* Profile skeleton */}
                <div className="p-4 border-b border-gray-200">
                    <div className="w-20 h-20 rounded-full bg-gray-200 animate-pulse" />
                    <div className="mt-4 h-6 w-32 bg-gray-200 rounded animate-pulse" />
                    <div className="mt-2 h-4 w-24 bg-gray-200 rounded animate-pulse" />
                </div>
                <PostSkeleton />
                <PostSkeleton />
            </div>
        );
    }

    if (error || !user) {
        return (
            <div className="p-8 text-center">
                <p className="text-red-500">{error || 'User not found'}</p>
            </div>
        );
    }

    return (
        <div>
            {/* Header */}
            <div className="sticky top-0 bg-white/80 backdrop-blur-sm border-b border-gray-200 z-10 px-4 py-3">
                <h1 className="text-xl font-bold">{user.display_name || user.username}</h1>
                <p className="text-sm text-gray-500">{user.post_count} posts</p>
            </div>

            {/* Profile Info */}
            <div className="p-4 border-b border-gray-200">
                <div className="flex justify-between items-start">
                    <Avatar username={user.username} src={user.profile_image} size="xl" />

                    {!isOwnProfile && currentUser && (
                        <button
                            onClick={handleFollow}
                            disabled={followLoading}
                            className={`
                px-4 py-2 rounded-full font-semibold
                ${
                    user.is_following
                        ? 'bg-white border border-gray-300 hover:border-red-300 hover:text-red-500'
                        : 'bg-black text-white hover:bg-gray-800'
                }
              `}
                        >
                            {followLoading ? '...' : user.is_following ? 'Following' : 'Follow'}
                        </button>
                    )}

                    {isOwnProfile && (
                        <button className="px-4 py-2 rounded-full font-semibold border border-gray-300 hover:bg-gray-50">
                            Edit Profile
                        </button>
                    )}
                </div>

                <div className="mt-4">
                    <h2 className="text-xl font-bold">{user.display_name || user.username}</h2>
                    <p className="text-gray-500">@{user.username}</p>
                </div>

                {user.bio && <p className="mt-3">{user.bio}</p>}

                <div className="flex gap-4 mt-3 text-sm">
                    <span>
                        <strong>{user.following_count}</strong>{' '}
                        <span className="text-gray-500">Following</span>
                    </span>
                    <span>
                        <strong>{user.follower_count}</strong>{' '}
                        <span className="text-gray-500">Followers</span>
                    </span>
                </div>
            </div>

            {/* Posts */}
            <div>
                {posts === null ? (
                    <>
                        <PostSkeleton />
                        <PostSkeleton />
                    </>
                ) : posts.length === 0 ? (
                    <div className="p-8 text-center text-gray-500">No posts yet</div>
                ) : (
                    posts.map((post) => <PostCard key={post.id} post={post} />)
                )}
            </div>
        </div>
    );
}
