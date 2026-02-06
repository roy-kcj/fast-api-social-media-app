'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { api } from '@/lib/api';
import { UserPrivate } from '@/types';

interface AuthContextType {
    user: UserPrivate | null;
    loading: boolean;
    login: (email: string, password: string) => Promise<void>;
    logout: () => void;
    register: (username: string, email: string, password: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<UserPrivate | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        let cancelled = false;

        const initAuth = async () => {
            const token =
                typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

            if (token) {
                api.setToken(token);
                try {
                    const userData = await api.getMe();
                    if (!cancelled) setUser(userData);
                } catch {
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    api.setToken(null);
                }
            }

            if (!cancelled) setLoading(false);
        };

        initAuth();

        return () => {
            cancelled = true;
        };
    }, []);

    const login = async (email: string, password: string) => {
        const tokens = await api.login(email, password);
        localStorage.setItem('access_token', tokens.access_token);
        localStorage.setItem('refresh_token', tokens.refresh_token);
        api.setToken(tokens.access_token);
        const userData = await api.getMe();
        setUser(userData);
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        api.setToken(null);
        setUser(null);
    };

    const register = async (username: string, email: string, password: string) => {
        await api.register(username, email, password);
        await login(email, password);
    };

    return (
        <AuthContext.Provider value={{ user, loading, login, logout, register }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) throw new Error('useAuth must be used within AuthProvider');
    return context;
}
