import Image from 'next/image';
import { User } from 'lucide-react';

interface AvatarProps {
    username?: string;
    src?: string | null;
    size?: 'sm' | 'md' | 'lg' | 'xl';
    className?: string;
}

const SIZES = {
    sm: { class: 'w-8 h-8 text-xs', pixels: 32 },
    md: { class: 'w-10 h-10 text-sm', pixels: 40 },
    lg: { class: 'w-12 h-12 text-base', pixels: 48 },
    xl: { class: 'w-16 h-16 text-lg', pixels: 64 },
};

export function Avatar({ username, src, size = 'md', className = '' }: AvatarProps) {
    const { class: sizeClass, pixels } = SIZES[size];

    return (
        <div
            className={`
            ${sizeClass}
            rounded-full bg-gray-200
            flex-shrink-0 overflow-hidden
            flex items-center justify-center
            relative
            ${className}
            `}
        >
            {src ? (
                <Image
                    src={src}
                    alt={username || 'User'}
                    fill
                    className="object-cover"
                    sizes={`${pixels}px`}
                />
            ) : username ? (
                <span className="font-semibold text-gray-600">{username[0].toUpperCase()}</span>
            ) : (
                <User className="w-1/2 h-1/2 text-gray-500" />
            )}
        </div>
    );
}
