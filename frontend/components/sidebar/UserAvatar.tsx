'use client';

import { Avatar } from '@/components/ui';
import { UserStatus, STATUS_COLORS } from './UserMenu';

interface UserAvatarProps {
    username?: string;
    profileImage?: string | null;
    status: UserStatus;
    size?: 'sm' | 'md' | 'lg';
}

const STATUS_SIZE_CLASSES = {
    sm: 'w-2.5 h-2.5',
    md: 'w-3 h-3',
    lg: 'w-3.5 h-3.5',
};

export function UserAvatar({ username, profileImage, status, size = 'md' }: UserAvatarProps) {
    return (
        <div className="relative">
            <Avatar username={username} src={profileImage} size={size} />

            {/* Status indicator */}
            <span
                className={`
          absolute bottom-0 right-0
          ${STATUS_SIZE_CLASSES[size]}
          rounded-full border-2 border-white
          ${STATUS_COLORS[status]}
        `}
            />
        </div>
    );
}
