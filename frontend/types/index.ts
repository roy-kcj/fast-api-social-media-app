// User Types
export interface UserBrief {
  id: number;
  username: string;
  display_name: string | null;
  profile_image: string;
  is_verified: boolean;
}

export interface UserOut {
  id: number;
  username: string;
  display_name: string | null;
  bio: string | null;
  profile_image: string;
  banner_image: string | null;
  is_verified: boolean;
  created_at: string;
  follower_count: number;
  following_count: number;
  post_count: number;
  is_following: boolean;
  is_followed_by: boolean;
}

export interface UserPrivate extends UserOut {
  email: string;
  is_active: boolean;
  is_admin: boolean;
  updated_at: string;
}

// Post Types
export interface Tag {
  id: number;
  name: string;
}

export interface Post {
  id: number;
  title: string | null;
  body: string;
  author: UserBrief;
  tags: Tag[];
  like_count: number;
  reply_count: number;
  repost_count: number;
  is_liked: boolean;
  parent_id: number | null;
  repost_of_id: number | null;
  created_at: string;
  updated_at: string;
}

export interface PostList {
  items: Post[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}


export interface FollowResponse {
  following: boolean;
  follower_count: number;
}

// Auth Types
export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}