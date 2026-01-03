'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { sendChatMessage, listConversations, getConversation } from '@/lib/chat-api';
import type { Message, ToolCallInfo } from '@/types';

interface ChatMessage extends Omit<Message, 'id' | 'created_at'> {
  id?: string;
  toolCalls?: ToolCallInfo[];
  isLoading?: boolean;
  timestamp?: string;
  isFallback?: boolean;
}

interface ChatContainerProps {
  userId: string;
}

export default function ChatContainer({ userId }: ChatContainerProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Load most recent conversation or show welcome message
  useEffect(() => {
    const loadRecentConversation = async () => {
      try {
        const result = await listConversations(1, 1);
        if (result.success && result.data.conversations.length > 0) {
          const recentConv = result.data.conversations[0];
          const convResult = await getConversation(recentConv.id);
          if (convResult.success && convResult.data.messages.length > 0) {
            setConversationId(recentConv.id);
            setMessages(
              convResult.data.messages.map((m) => ({
                role: m.role as 'user' | 'assistant',
                content: m.content,
                timestamp: m.created_at,
                isFallback: m.content.includes('demo mode') || m.content.includes('mock'),
              }))
            );
            return;
          }
        }
      } catch {
        // Ignore errors, just show welcome
      }
      // Show welcome message if no conversation found
      setMessages([
        {
          role: 'assistant',
          content:
            "Hi! I'm your AI todo assistant. I can help you manage your tasks. Try saying:\n\n" +
            '- "Add buy groceries"\n' +
            '- "Show my tasks"\n' +
            '- "Complete the groceries task"\n' +
            '- "Delete task about meeting"\n\n' +
            'How can I help you today?',
        },
      ]);
    };
    loadRecentConversation();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');

    // Add user message to UI
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);

    // Add loading indicator
    setMessages((prev) => [
      ...prev,
      { role: 'assistant', content: '', isLoading: true },
    ]);
    setIsLoading(true);

    try {
      const result = await sendChatMessage({
        conversation_id: conversationId || undefined,
        message: userMessage,
      });

      // Remove loading indicator
      setMessages((prev) => prev.filter((m) => !m.isLoading));

      if (result.success) {
        setConversationId(result.data.conversation_id);
        const isFallback = result.data.response.includes('demo mode') ||
                          result.data.response.includes('quota exceeded');
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: result.data.response,
            toolCalls: result.data.tool_calls,
            timestamp: new Date().toISOString(),
            isFallback,
          },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: `Error: ${result.error.message}`,
          },
        ]);
      }
    } catch {
      setMessages((prev) => prev.filter((m) => !m.isLoading));
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewConversation = () => {
    setConversationId(null);
    setMessages([
      {
        role: 'assistant',
        content: 'Started a new conversation. How can I help you?',
      },
    ]);
  };

  // Avoid unused variable warning for userId - it's used for future features
  void userId;

  return (
    <div className="flex flex-col h-full max-h-[calc(100vh-200px)] bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b bg-blue-600 text-white rounded-t-lg">
        <div>
          <h2 className="text-lg font-semibold">AI Todo Assistant</h2>
          <p className="text-sm text-blue-100">
            {conversationId ? 'Conversation active' : 'New conversation'}
          </p>
        </div>
        <button
          onClick={handleNewConversation}
          className="px-3 py-1.5 text-sm bg-blue-500 hover:bg-blue-400 rounded-md transition-colors"
        >
          New Chat
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-2 ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {message.isLoading ? (
                <div className="flex items-center space-x-2">
                  <div className="animate-pulse flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                    <div
                      className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: '0.1s' }}
                    />
                    <div
                      className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: '0.2s' }}
                    />
                  </div>
                  <span className="text-sm text-gray-500">Thinking...</span>
                </div>
              ) : (
                <>
                  {message.isFallback && (
                    <div className="mb-2 text-xs text-amber-600 bg-amber-50 px-2 py-1 rounded flex items-center gap-1">
                      <span>⚠️</span>
                      <span>Demo Mode</span>
                    </div>
                  )}
                  <p className="whitespace-pre-wrap">{message.content}</p>
                  {message.toolCalls && message.toolCalls.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-gray-200">
                      <p className="text-xs text-gray-500 mb-1">Tools used:</p>
                      <div className="flex flex-wrap gap-1">
                        {message.toolCalls.map((tc, i) => (
                          <span
                            key={i}
                            className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded"
                          >
                            {tc.tool_name}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  {message.timestamp && (
                    <p className="text-xs text-gray-400 mt-1">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </p>
                  )}
                </>
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a message... (e.g., 'Add buy groceries')"
            className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </div>
        <div className="mt-2 flex gap-2 flex-wrap">
          <button
            type="button"
            onClick={() => setInput('Show my tasks')}
            className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded hover:bg-gray-200"
          >
            Show tasks
          </button>
          <button
            type="button"
            onClick={() => setInput('Add ')}
            className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded hover:bg-gray-200"
          >
            Add task
          </button>
          <button
            type="button"
            onClick={() => setInput('Show pending tasks')}
            className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded hover:bg-gray-200"
          >
            Pending only
          </button>
        </div>
      </form>
    </div>
  );
}
