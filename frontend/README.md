# Social Media App - Frontend

A modern Twitter-style social media web application built with Next.js.

## Features

- **Authentication:** Login, registration with JWT token management
- **Feed:** Personalized feed (Following) and discovery feed (Popular)
- **Posts:** Create posts with hashtags, like/unlike
- **Profiles:** View user profiles, follow/unfollow
- **Explore:** Search posts by tags, discover users
- **View Tracking:** Intersection Observer tracks viewed posts (50% visibility)

## Tech Stack

- **Framework:** Next.js 16 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Icons:** Lucide React
- **State:** React Context (Auth)

## Pages

| Route                 | Description                          |
| --------------------- | ------------------------------------ |
| `/`                   | Home feed (Following / Popular tabs) |
| `/login`              | Login page                           |
| `/register`           | Registration page                    |
| `/explore`            | Search posts and users               |
| `/profile/[username]` | User profile page                    |
| `/notifications`      | Notifications (coming soon)          |
| `/chat`               | Messages (coming soon)               |

## Local Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── page.tsx           # Home feed
│   ├── login/             # Login page
│   ├── register/          # Registration page
│   ├── explore/           # Search & discover
│   ├── profile/[username] # User profiles
│   ├── layout.tsx         # Root layout with sidebar
│   └── globals.css        # Global styles
├── components/
│   ├── feed/              # Feed components
│   │   ├── FeedTabs.tsx
│   │   ├── PostCard.tsx
│   │   ├── PostComposer.tsx
│   │   ├── PostList.tsx
│   │   └── PostSkeleton.tsx
│   ├── sidebar/           # Navigation sidebar
│   │   ├── Sidebar.tsx
│   │   ├── UserAvatar.tsx
│   │   └── UserMenu.tsx
│   └── ui/                # Reusable UI components
│       └── Avatar.tsx
├── context/
│   └── AuthContext.tsx    # Authentication state
├── hooks/
│   └── useViewTracking.ts # View tracking hook
├── lib/
│   └── api.ts             # API client
├── types/
│   └── index.ts           # TypeScript types
├── Dockerfile
└── README.md
```

## Key Components

### PostCard

Displays a single post with author info, content, tags, and action buttons (like, comment, repost). Uses Intersection Observer to track when 50% of the card is visible.

### PostList

Fetches and displays posts with loading skeletons and error states. Supports "following" (personalized) and "popular" (all posts sorted by likes) modes.

### Sidebar

Collapsible navigation with expand-on-hover, user avatar with status indicator, and dropdown menu.

### AuthContext

Global authentication state with login, logout, and register functions. Persists tokens to localStorage.

## View Tracking

Posts are marked as "viewed" when 50% visible using Intersection Observer:

```tsx
// In PostCard
useEffect(() => {
    const observer = new IntersectionObserver(
        (entries) => {
            if (entry.isIntersecting && entry.intersectionRatio >= 0.5) {
                onView(post.id); // Mark as viewed
            }
        },
        { threshold: 0.5 },
    );
    // ...
}, []);
```

Views are debounced and sent to the API in batches to reduce network requests.
