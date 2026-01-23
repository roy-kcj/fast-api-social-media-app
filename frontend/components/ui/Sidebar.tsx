"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

const navItems = [
    { label: "Home", href: "/" },
    { label: "Search", href: "/search" },
    { label: "Notifications", href: "/notifications" },
    { label: "Messages", href: "/messages" },
    { label: "Profile", href: "/profile" }
];

export function Sidebar() {
    const pathname = usePathname();
    const { user, loading, logout } = useAuth();

     return (
       <aside className="...">
         {/* Logo */}
         {/* Nav Links */}

         <nav>
            {navItems.map((item) => (
                <Link key={item.href} href={item.href}>
                    {item.label}
                </Link>
            ))}
         </nav>

         {/* Post Button */}
         {/* User Info */}
       </aside>
     );
}