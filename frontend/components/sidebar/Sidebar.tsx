"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, Search, Bell, MessageCircle, ChevronLeft, ChevronRight } from "lucide-react";
import { UserAvatar } from "./UserAvatar";
import { UserMenu, UserStatus } from "./UserMenu";
import { useAuth } from "@/context/AuthContext";

interface NavItem {
  icon: React.ReactNode;
  label: string;
  href: string;
}

const NAV_ITEMS: NavItem[] = [
  { icon: <Home size={22} />, label: "Home", href: "/" },
  { icon: <Search size={22} />, label: "Explore", href: "/explore" },
  { icon: <Bell size={22} />, label: "Notifications", href: "/notifications" },
  { icon: <MessageCircle size={22} />, label: "Chat", href: "/chat" },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  
  const [isExpanded, setIsExpanded] = useState(false);
  const [isPinned, setIsPinned] = useState(false);
  const [status, setStatus] = useState<UserStatus>("online");
  const [menuOpen, setMenuOpen] = useState(false);

  const handleMouseEnter = () => {
    if (!isPinned) setIsExpanded(true);
  };

  const handleMouseLeave = () => {
    if (!isPinned) setIsExpanded(false);
  };

  const handleToggle = () => {
    setIsPinned(!isPinned);
    setIsExpanded(!isExpanded);
  };

  return (
    <aside
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      className={`
        fixed left-0 top-0 h-screen
        bg-white border-r border-gray-200
        flex flex-col p-3 z-40
        transition-all duration-300 ease-in-out
        ${isExpanded ? "w-64" : "w-[72px]"}
      `}
    >
      <button
        onClick={handleToggle}
        className="p-2 rounded-lg hover:bg-gray-100 transition-colors ml-auto mb-4"
        aria-label={isExpanded ? "Collapse sidebar" : "Expand sidebar"}
      >
        {isExpanded ? (
          <ChevronLeft size={20} className="text-gray-500" />
        ) : (
          <ChevronRight size={20} className="text-gray-500" />
        )}
      </button>

      <nav className="flex-1 space-y-1">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href;
          
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`
                flex items-center p-3 rounded-lg
                transition-all duration-200
                hover:bg-gray-100
                ${isActive ? "bg-gray-100 font-semibold" : ""}
              `}
            >
              <span className="w-6 h-6 flex items-center justify-center flex-shrink-0">
                {item.icon}
              </span>
              <span
                className={`
                  ml-4 whitespace-nowrap
                  transition-all duration-300 ease-in-out
                  ${isExpanded ? "opacity-100 max-w-xs" : "opacity-0 max-w-0 overflow-hidden"}
                `}
              >
                {item.label}
              </span>
            </Link>
          );
        })}
      </nav>

      {/* User Section */}
      <div className="mt-auto pt-4 border-t border-gray-200">
        <div
          className={`
            flex items-center p-3 rounded-lg
            hover:bg-gray-100 transition-all duration-200
            ${isExpanded ? "justify-between" : "justify-center"}
          `}
        >
          {/* Avatar + Info */}
          <div className="flex items-center gap-3">
            <UserAvatar
              username={user?.username}
              profileImage={user?.profile_image}
              status={status}
            />

            {isExpanded && (
              <div className="transition-all duration-300">
                <p className="font-medium text-sm truncate">
                  {user?.display_name || user?.username || "Guest"}
                </p>
                <p className="text-xs text-gray-500 capitalize">{status}</p>
              </div>
            )}
          </div>

          {/* Menu */}
          {isExpanded && (
            <UserMenu
              isOpen={menuOpen}
              onClose={() => setMenuOpen(false)}
              onToggle={() => setMenuOpen(!menuOpen)}
              status={status}
              onStatusChange={setStatus}
              isLoggedIn={!!user}
              onLogout={logout}
            />
          )}
        </div>
      </div>
    </aside>
  );
}