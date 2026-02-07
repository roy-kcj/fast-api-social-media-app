'use client';

import { Suspense } from 'react';
import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { Search } from 'lucide-react';
import Link from 'next/link';
import { Avatar } from '@/components/ui';
import { PostCard } from '@/components/feed/PostCard';
import { PostSkeleton } from '@/components/feed/PostSkeleton';
import { api } from '@/lib/api';
import { Post, UserOut } from '@/types';

type SearchType = 'posts' | 'users';

// Main content component
function ExploreContent() {
    const searchParams = useSearchParams();
    const tagFromUrl = searchParams.get('tag');

    const [searchType, setSearchType] = useState<SearchType>('posts');
    const [posts, setPosts] = useState<Post[] | null>(null);
    const [users, setUsers] = useState<UserOut[] | null>(null);
    const [searchQuery, setSearchQuery] = useState(tagFromUrl || '');
    const [activeSearch, setActiveSearch] = useState(tagFromUrl || '');

    // Fetch posts
    useEffect(() => {
        if (searchType !== 'posts') return;

        let cancelled = false;

        const fetchPosts = async () => {
            try {
                const data = activeSearch
                    ? await api.getPosts({ tags: [activeSearch] })
                    : await api.getPosts();

                if (!cancelled) setPosts(data.items);
            } catch {
                if (!cancelled) setPosts([]);
            }
        };

        setPosts(null);
        fetchPosts();

        return () => {
            cancelled = true;
        };
    }, [activeSearch, searchType]);

    // Fetch users
    useEffect(() => {
        if (searchType !== 'users' || !activeSearch) {
            setUsers(null);
            return;
        }

        let cancelled = false;

        const fetchUsers = async () => {
            try {
                const data = await api.searchUsers(activeSearch);
                if (!cancelled) setUsers(data);
            } catch {
                if (!cancelled) setUsers([]);
            }
        };

        setUsers(null);
        fetchUsers();

        return () => {
            cancelled = true;
        };
    }, [activeSearch, searchType]);

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        setActiveSearch(searchQuery.trim());
    };

    return (
        <div>
            {/* Header */}
            <div className="sticky top-0 bg-white/80 backdrop-blur-sm border-b border-gray-200 z-10 px-4 py-3">
                <h1 className="text-xl font-bold">Explore</h1>
            </div>

            {/* Search */}
            <div className="p-4 border-b border-gray-200">
                <form onSubmit={handleSearch} className="relative">
                    <Search
                        size={18}
                        className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
                    />
                    <input
                        type="text"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder={
                            searchType === 'posts' ? 'Search by tag...' : 'Search users...'
                        }
                        className="w-full pl-10 pr-4 py-2 bg-gray-100 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                </form>

                {/* Tabs */}
                <div className="flex mt-3 border-b border-gray-200">
                    <button
                        onClick={() => setSearchType('posts')}
                        className={`flex-1 py-2 text-center ${
                            searchType === 'posts'
                                ? 'font-semibold border-b-2 border-blue-500'
                                : 'text-gray-500'
                        }`}
                    >
                        Posts
                    </button>
                    <button
                        onClick={() => setSearchType('users')}
                        className={`flex-1 py-2 text-center ${
                            searchType === 'users'
                                ? 'font-semibold border-b-2 border-blue-500'
                                : 'text-gray-500'
                        }`}
                    >
                        Users
                    </button>
                </div>
            </div>

            {/* Results */}
            {searchType === 'posts' ? (
                posts === null ? (
                    <>
                        <PostSkeleton />
                        <PostSkeleton />
                        <PostSkeleton />
                    </>
                ) : posts.length === 0 ? (
                    <div className="p-8 text-center text-gray-500">
                        {activeSearch ? `No posts found with tag #${activeSearch}` : 'No posts yet'}
                    </div>
                ) : (
                    posts.map((post) => <PostCard key={post.id} post={post} />)
                )
            ) : !activeSearch ? (
                <div className="p-8 text-center text-gray-500">Enter a username to search</div>
            ) : users === null ? (
                <div className="p-4 space-y-4">
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="flex items-center gap-3 animate-pulse">
                            <div className="w-12 h-12 rounded-full bg-gray-200" />
                            <div className="flex-1">
                                <div className="h-4 w-24 bg-gray-200 rounded" />
                                <div className="h-3 w-16 bg-gray-200 rounded mt-1" />
                            </div>
                        </div>
                    ))}
                </div>
            ) : users.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                    No users found matching &quot;{activeSearch}&quot;
                </div>
            ) : (
                <div className="divide-y divide-gray-200">
                    {users.map((user) => (
                        <UserCard key={user.id} user={user} />
                    ))}
                </div>
            )}
        </div>
    );
}

// User card component
function UserCard({ user }: { user: UserOut }) {
    return (
        <Link
            href={`/profile/${user.username}`}
            className="flex items-center gap-3 p-4 hover:bg-gray-50 transition-colors"
        >
            <Avatar username={user.username} src={user.profile_image} size="lg" />
            <div className="flex-1 min-w-0">
                <p className="font-semibold truncate">{user.display_name || user.username}</p>
                <p className="text-gray-500 text-sm truncate">@{user.username}</p>
                {user.bio && <p className="text-gray-600 text-sm truncate mt-1">{user.bio}</p>}
            </div>
            <div className="text-sm text-gray-500">{user.follower_count} followers</div>
        </Link>
    );
}

// Main page with Suspense wrapper
export default function ExplorePage() {
    return (
        <Suspense
            fallback={
                <div>
                    <div className="sticky top-0 bg-white/80 backdrop-blur-sm border-b border-gray-200 z-10 px-4 py-3">
                        <h1 className="text-xl font-bold">Explore</h1>
                    </div>
                    <PostSkeleton />
                    <PostSkeleton />
                    <PostSkeleton />
                </div>
            }
        >
            <ExploreContent />
        </Suspense>
    );
}
