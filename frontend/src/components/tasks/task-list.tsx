"use client";

import { useCallback, useEffect, useState } from "react";
import type { Task, TaskListResponse } from "@/types";
import { api } from "@/lib/api";
import { TaskItem } from "./task-item";
import { TaskForm } from "./task-form";

export function TaskList() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    const result = await api.get<TaskListResponse>("/tasks");

    if (result.success) {
      setTasks(result.data.tasks);
    } else {
      setError(result.error.message);
    }

    setIsLoading(false);
  }, []);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  async function handleCreate(title: string, description?: string) {
    const result = await api.post<Task>("/tasks", { title, description });

    if (result.success) {
      // Optimistic update: add to beginning of list
      setTasks((prev) => [result.data, ...prev]);
    } else {
      setError(result.error.message);
    }
  }

  async function handleToggle(id: string) {
    // Optimistic update
    setTasks((prev) =>
      prev.map((t) => (t.id === id ? { ...t, isCompleted: !t.isCompleted } : t))
    );

    const result = await api.patch<Task>(`/tasks/${id}/toggle`);

    if (!result.success) {
      // Revert on error
      setTasks((prev) =>
        prev.map((t) => (t.id === id ? { ...t, isCompleted: !t.isCompleted } : t))
      );
      setError(result.error.message);
    }
  }

  async function handleDelete(id: string) {
    // Store task for potential revert
    const taskToDelete = tasks.find((t) => t.id === id);

    // Optimistic update
    setTasks((prev) => prev.filter((t) => t.id !== id));

    const result = await api.delete(`/tasks/${id}`);

    if (!result.success) {
      // Revert on error
      if (taskToDelete) {
        setTasks((prev) => [...prev, taskToDelete]);
      }
      setError(result.error.message);
    }
  }

  async function handleUpdate(id: string, title: string, description?: string) {
    const result = await api.put<Task>(`/tasks/${id}`, { title, description });

    if (result.success) {
      setTasks((prev) => prev.map((t) => (t.id === id ? result.data : t)));
    } else {
      setError(result.error.message);
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="h-16 bg-gray-100 rounded-lg animate-pulse" />
        <div className="h-20 bg-gray-100 rounded-lg animate-pulse" />
        <div className="h-20 bg-gray-100 rounded-lg animate-pulse" />
        <div className="h-20 bg-gray-100 rounded-lg animate-pulse" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <TaskForm onSubmit={handleCreate} />

      {error && (
        <div className="p-3 text-sm text-red-600 bg-red-50 rounded-md">
          {error}
          <button
            onClick={() => setError(null)}
            className="ml-2 text-red-800 underline"
          >
            Dismiss
          </button>
        </div>
      )}

      {tasks.length === 0 ? (
        <div className="text-center py-12">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            />
          </svg>
          <h3 className="mt-4 text-lg font-medium text-gray-900">No tasks yet</h3>
          <p className="mt-2 text-sm text-gray-500">
            Get started by creating your first task above.
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {tasks.map((task) => (
            <TaskItem
              key={task.id}
              task={task}
              onToggle={handleToggle}
              onDelete={handleDelete}
              onUpdate={handleUpdate}
            />
          ))}
        </div>
      )}
    </div>
  );
}
