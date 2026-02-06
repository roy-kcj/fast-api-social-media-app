import {
  Post,
  PostList,
  UserOut,
  UserPrivate,
  TokenResponse,
} from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClient {
  private accessToken: string | null = null;

  setToken(token: string | null) {
    this.accessToken = token;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers: HeadersInit = {
      "Content-Type": "application/json",
      ...options.headers,
    };

    if (this.accessToken) {
      (headers as Record<string, string>)["Authorization"] = `Bearer ${this.accessToken}`;
    }

    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Request failed" }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    if (response.status === 204) return {} as T;
    return response.json();
  }

  // Auth
  async login(email: string, password: string): Promise<TokenResponse> {
    return this.request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  }

  async register(username: string, email: string, password: string): Promise<UserPrivate> {
    return this.request("/auth/register", {
      method: "POST",
      body: JSON.stringify({ username, email, password }),
    });
  }

  async getMe(): Promise<UserPrivate> {
    return this.request("/auth/me");
  }

  // Posts
  async getPosts(params?: {
    tags?: string[];
    author_id?: number;
    sort_by?: "recent" | "popular";
    limit?: number;
    offset?: number;
  }): Promise<PostList> {
    const searchParams = new URLSearchParams();
    
    if (params?.tags) {
      params.tags.forEach(tag => searchParams.append("tags", tag));
    }
    if (params?.author_id) searchParams.set("author_id", params.author_id.toString());
    if (params?.sort_by) searchParams.set("sort_by", params.sort_by);
    if (params?.limit) searchParams.set("limit", params.limit.toString());
    if (params?.offset) searchParams.set("offset", params.offset.toString());

    const query = searchParams.toString();
    return this.request<PostList>(`/posts/${query ? `?${query}` : ""}`);
  }

  async getPost(id: number): Promise<Post> {
    return this.request(`/posts/${id}`);
  }

  async createPost(body: string): Promise<Post> {
    return this.request("/posts/", {
      method: "POST",
      body: JSON.stringify({ body }),
    });
  }

  async deletePost(id: number): Promise<void> {
    await this.request(`/posts/${id}`, { method: "DELETE" });
  }

  async toggleLike(postId: number): Promise<{ liked: boolean; like_count: number }> {
    return this.request(`/posts/${postId}/like/toggle`, { method: "POST" });
  }

  async getFeed(limit = 20, offset = 0): Promise<PostList> {
    return this.request(`/posts/feed?limit=${limit}&offset=${offset}`);
  }

  async getUserPosts(username: string, limit = 20, offset = 0): Promise<PostList> {
    return this.request(`/posts/user/${username}?limit=${limit}&offset=${offset}`);
  }

  async trackViews(postIds: number[]): Promise<void> {
    if (postIds.length === 0) return;
    
    await this.request("/posts/views", {
      method: "POST",
      body: JSON.stringify(postIds),
    });
  }

  // Users
  async getUser(username: string): Promise<UserOut> {
    return this.request(`/users/${username}`);
  }

  async followUser(username: string): Promise<{ following: boolean; follower_count: number }> {
    return this.request(`/users/${username}/follow`, { method: "POST" });
  }

  async unfollowUser(username: string): Promise<{ following: boolean; follower_count: number }> {
    return this.request(`/users/${username}/follow`, { method: "DELETE" });
  }

  async getFollowers(username: string, limit = 20, offset = 0) {
    return this.request(`/users/${username}/followers?limit=${limit}&offset=${offset}`);
  }

  async getFollowing(username: string, limit = 20, offset = 0) {
    return this.request(`/users/${username}/following?limit=${limit}&offset=${offset}`);
  }

  async searchUsers(query: string, limit = 20): Promise<UserOut[]> {
    return this.request(`/users/search?q=${encodeURIComponent(query)}&limit=${limit}`);
  }

}

export const api = new ApiClient();