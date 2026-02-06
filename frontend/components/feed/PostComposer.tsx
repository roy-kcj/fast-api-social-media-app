'use client';

import { useState } from 'react';
import { Avatar } from '@/components/ui';
import { useAuth } from '@/context/AuthContext';
import { api } from '@/lib/api';

interface PostComposerProps {
    onPostCreated?: () => void;
}

export function PostComposer({ onPostCreated }: PostComposerProps) {
    const { user } = useAuth();
    const [body, setBody] = useState('');
    const [isPosting, setIsPosting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    if (!user) {
        return (
            <div className="p-4 border-b border-gray-200 text-center text-gray-500">
                <a href="/login" className="text-blue-500 hover:underline">
                    Log in
                </a>{' '}
                to create a post
            </div>
        );
    }

    const handleSubmit = async () => {
        if (!body.trim() || isPosting) return;

        setIsPosting(true);
        setError(null);

        try {
            await api.createPost(body.trim());
            setBody('');
            onPostCreated?.();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to create post');
        } finally {
            setIsPosting(false);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
            handleSubmit();
        }
    };

    return (
        <div className="p-4 border-b border-gray-200">
            <div className="flex gap-3">
                <Avatar username={user.username} src={user.profile_image} size="md" />

                <div className="flex-1">
                    <textarea
                        value={body}
                        onChange={(e) => setBody(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="What's happening?"
                        rows={3}
                        className="w-full resize-none border-none outline-none text-lg placeholder:text-gray-500"
                    />

                    {error && <p className="text-red-500 text-sm mb-2">{error}</p>}

                    <div className="flex justify-between items-center mt-2">
                        <span className="text-sm text-gray-500">{body.length}/280</span>

                        <button
                            onClick={handleSubmit}
                            disabled={!body.trim() || isPosting}
                            className={`
                px-4 py-2 rounded-full font-semibold text-white
                ${
                    body.trim() && !isPosting
                        ? 'bg-blue-500 hover:bg-blue-600'
                        : 'bg-blue-300 cursor-not-allowed'
                }
              `}
                        >
                            {isPosting ? 'Posting...' : 'Post'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
