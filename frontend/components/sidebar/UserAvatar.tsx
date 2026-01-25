"use client";

import { User } from "lucide-react";
import { UserStatus, STATUS_COLORS } from "./UserMenu";

interface UserAvatarProps {
  username?: string;
  profileImage?: string | null;
  status: UserStatus;
  size?: "sm" | "md" | "lg";
}

const SIZE_CLASSES = {
  sm: { avatar: "w-8 h-8", status: "w-2.5 h-2.5" },
  md: { avatar: "w-10 h-10", status: "w-3 h-3" },
  lg: { avatar: "w-12 h-12", status: "w-3.5 h-3.5" },
};

export function UserAvatar({ username, profileImage, status, size = "md" }: UserAvatarProps) {
  const sizes = SIZE_CLASSES[size];

  return (
    <div className="relative flex-shrink-0">
      <div
        className={`
          ${sizes.avatar}
          rounded-full bg-gray-200
          flex items-center justify-center
          overflow-hidden
        `}
      >
        {profileImage ? (
          <img
            src={profileImage}
            alt={username || "User"}
            className="w-full h-full object-cover"
          />
        ) : (
          <User className="w-1/2 h-1/2 text-gray-500" />
        )}
      </div>

      <span
        className={`
          absolute bottom-0 right-0
          ${sizes.status}
          rounded-full border-2 border-white
          ${STATUS_COLORS[status]}
        `}
      />
    </div>
  );
}