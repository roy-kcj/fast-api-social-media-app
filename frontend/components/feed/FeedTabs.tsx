'use client';

type Tab = 'following' | 'popular';

interface FeedTabsProps {
    activeTab: Tab;
    onTabChange: (tab: Tab) => void;
}

export function FeedTabs({ activeTab, onTabChange }: FeedTabsProps) {
    const tabs: { value: Tab; label: string }[] = [
        { value: 'following', label: 'Following' },
        { value: 'popular', label: 'Popular' },
    ];
    return (
        <div className="flex border-b border-gray-200">
            {tabs.map((tab) => (
                <button
                    key={tab.value}
                    onClick={() => onTabChange(tab.value)}
                    className={`
                        flex-1 py-3 text-center
                        transition-colors
                        ${
                            activeTab === tab.value
                                ? 'font-semibold text-black border-b-2 border-blue-500'
                                : 'text-gray-500 hover:bg-gray-50 hover:text-gray-700'
                        }
                    `}
                >
                    {tab.label}
                </button>
            ))}
        </div>
    );
}
