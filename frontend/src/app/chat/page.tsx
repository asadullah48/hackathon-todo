'use client';

import { useCallback, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { getCurrentUser, signOut } from '@/lib/auth';
import ChatContainer from '@/components/chat/chat-container';

interface User {
  id: string;
  email: string;
}

export default function ChatPage() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const loadUser = useCallback(async () => {
    const { data } = await getCurrentUser();
    if (!data) {
      router.push('/login');
      return;
    }
    setUser(data);
    setLoading(false);
  }, [router]);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  const handleLogout = async () => {
    await signOut();
    router.push('/login');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-6">
            <h1 className="text-2xl font-bold text-blue-600">Todo AI Chat</h1>
            <nav className="flex gap-4">
              <Link
                href="/tasks"
                className="text-gray-600 hover:text-blue-600 transition-colors"
              >
                Tasks
              </Link>
              <Link
                href="/chat"
                className="text-blue-600 font-medium"
              >
                AI Chat
              </Link>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">{user.email}</span>
            <button
              onClick={handleLogout}
              className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 text-sm"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-800">
            AI-Powered Task Management
          </h2>
          <p className="text-gray-600 mt-1">
            Chat with your AI assistant to manage tasks using natural language.
          </p>
        </div>

        <div className="h-[600px]">
          <ChatContainer userId={user.id} />
        </div>

        {/* Info Card */}
        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="font-medium text-blue-800 mb-2">How to use</h3>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>
              <strong>Add tasks:</strong> &quot;Add buy milk&quot; or &quot;Create a task to call mom&quot;
            </li>
            <li>
              <strong>View tasks:</strong> &quot;Show my tasks&quot; or &quot;What&apos;s on my list?&quot;
            </li>
            <li>
              <strong>Complete tasks:</strong> &quot;Mark the milk task as done&quot;
            </li>
            <li>
              <strong>Delete tasks:</strong> &quot;Remove the meeting task&quot;
            </li>
            <li>
              <strong>Filter:</strong> &quot;Show pending tasks&quot; or &quot;Show completed tasks&quot;
            </li>
          </ul>
        </div>
      </main>
    </div>
  );
}
