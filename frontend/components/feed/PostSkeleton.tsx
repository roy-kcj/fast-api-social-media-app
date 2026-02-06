export function PostSkeleton() {
    return (
        <div className="p-4 border-b border-gray-200">
            {/* User Section */}
            <div className="flex items-center gap-3 mb-3">
                {/* Avatar */}
                <div className="w-10 h-10 rounded-full bg-gray-200 animate-pulse" />
                {/* Name and Username */}
                <div className="space-y-2">
                    <div className="h-4 w-24 bg-gray-200 rounded animate-pulse" />
                    <div className="h-3 w-16 bg-gray-200 rounded animate-pulse" />
                </div>
            </div>

            {/* Content Body */}
            <div className="space-y-2 pl-13">
                <div className="h-3 w-3/4 bg-gray-200 rounded animate-pulse" />
                <div className="h-3 w-1/2 bg-gray-200 rounded animate-pulse" />
                <div className="h-3 w-1/3 bg-gray-200 rounded animate-pulse" />
                <div className="h-3 w-5/6 bg-gray-200 rounded animate-pulse" />
            </div>

            {/* Action Buttons */}
            <div className="flex gap-8 mt-4 pl-13">
                <div className="h-4 w-12 bg-gray-200 rounded animate-pulse" />
                <div className="h-4 w-12 bg-gray-200 rounded animate-pulse" />
                <div className="h-4 w-12 bg-gray-200 rounded animate-pulse" />
            </div>
        </div>
    );
}
