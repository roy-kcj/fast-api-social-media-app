"use client";

import { useRef, useEffect } from "react";
import Link from "next/link";
import { MoreVertical, LogOut, LogIn, Settings, UserPen } from "lucide-react";

export type UserStatus = "online" | "away" | "busy" | "invisible";

export const STATUS_COLORS: Record<UserStatus, string> = {
  online: "bg-green-500",
  away: "bg-yellow-500",
  busy: "bg-red-500",
  invisible: "bg-gray-400",
};

const STATUS_OPTIONS: { value: UserStatus; label: string }[] = [
  { value: "online", label: "Online" },
  { value: "away", label: "Away" },
  { value: "busy", label: "Busy" },
  { value: "invisible", label: "Invisible" },
];

interface UserMenuProps {
  isOpen: boolean;
  onClose: () => void;
  onToggle: () => void;
  status: UserStatus;
  onStatusChange: (status: UserStatus) => void;
  isLoggedIn: boolean;
  onLogout: () => void;
}

export function UserMenu({
  isOpen,
  onClose,
  onToggle,
  status,
  onStatusChange,
  isLoggedIn,
  onLogout,
}: UserMenuProps) {
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isOpen) return;

    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        onClose();
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [isOpen, onClose]);

  return (
    <div ref={menuRef} className="relative">
      <button
        onClick={onToggle}
        className="p-1.5 rounded-lg hover:bg-gray-200 transition-colors"
      >
        <MoreVertical size={18} className="text-gray-500" />
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div
          className="
            absolute bottom-full right-0 mb-2
            w-48 bg-white rounded-lg shadow-lg
            border border-gray-200 py-1 z-50
          "
        >
          {/* Status Section */}
          <div className="px-3 py-2 border-b border-gray-100">
            <p className="text-xs font-medium text-gray-500 mb-2">Status</p>
            <div className="space-y-1">
              {STATUS_OPTIONS.map((option) => (
                <button
                  key={option.value}
                  onClick={() => {
                    onStatusChange(option.value);
                    onClose();
                  }}
                  className={`
                    w-full flex items-center gap-2 px-2 py-1.5 rounded
                    text-sm text-left hover:bg-gray-100 transition-colors
                    ${status === option.value ? "bg-gray-100" : ""}
                  `}
                >
                  <span className={`w-2 h-2 rounded-full ${STATUS_COLORS[option.value]}`} />
                  <span>{option.label}</span>
                  {status === option.value && (
                    <span className="ml-auto text-blue-500 text-xs">✓</span>
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Actions Section */}
          <div className="py-1">
            {isLoggedIn ? (
              <>
                <MenuLink href="/settings/profile" icon={<UserPen size={16} />} label="Edit Profile" />
                <MenuLink href="/settings" icon={<Settings size={16} />} label="Settings" />
                <MenuButton
                  icon={<LogOut size={16} />}
                  label="Logout"
                  onClick={() => {
                    onLogout();
                    onClose();
                  }}
                  variant="danger"
                />
              </>
            ) : (
              <MenuLink href="/login" icon={<LogIn size={16} />} label="Login" />
            )}
          </div>
        </div>
      )}
    </div>
  );
}


function MenuLink({ href, icon, label }: { href: string; icon: React.ReactNode; label: string }) {
  return (
    <Link
      href={href}
      className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
    >
      {icon}
      <span>{label}</span>
    </Link>
  );
}

function MenuButton({
  icon,
  label,
  onClick,
  variant = "default",
}: {
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
  variant?: "default" | "danger";
}) {
  return (
    <button
      onClick={onClick}
      className={`
        w-full flex items-center gap-2 px-3 py-2 text-sm text-left
        hover:bg-gray-100 transition-colors
        ${variant === "danger" ? "text-red-600 hover:bg-red-50" : "text-gray-700"}
      `}
    >
      {icon}
      <span>{label}</span>
    </button>
  );
}