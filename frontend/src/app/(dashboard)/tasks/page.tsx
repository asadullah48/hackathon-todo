'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { getCurrentUser, signOut, getAuthToken } from '@/lib/auth'

interface User {
  id: string
  email: string
  name?: string
}

interface Task {
  id: number
  title: string
  description?: string
  completed: boolean
}

export default function TasksPage() {
  const [user, setUser] = useState<User | null>(null)
  const [tasks, setTasks] = useState<Task[]>([])
  const [newTask, setNewTask] = useState('')
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  const loadTasks = useCallback(async () => {
    try {
      const token = getAuthToken()
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/tasks`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (res.ok) {
        const data = await res.json()
        setTasks(data.tasks || data.data || data || [])
      }
    } catch (err) {
      console.error('Load tasks error:', err)
    }
  }, [])

  const loadUser = useCallback(async () => {
    const { data } = await getCurrentUser()

    if (!data) {
      router.push('/login')
      return
    }

    setUser(data)
    await loadTasks()
    setLoading(false)
  }, [router, loadTasks])

  useEffect(() => {
    loadUser()
  }, [loadUser])

  const handleAddTask = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newTask.trim()) return

    try {
      const token = getAuthToken()
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/tasks`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ title: newTask, description: '' })
      })

      if (res.ok) {
        setNewTask('')
        await loadTasks()
      }
    } catch (err) {
      console.error('Add task error:', err)
    }
  }

  const handleToggle = async (id: number) => {
    try {
      const token = getAuthToken()
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/tasks/${id}/toggle`, {
        method: 'PATCH',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      await loadTasks()
    } catch (err) {
      console.error('Toggle error:', err)
    }
  }

  const handleDelete = async (id: number) => {
    try {
      const token = getAuthToken()
      await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/tasks/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      await loadTasks()
    } catch (err) {
      console.error('Delete error:', err)
    }
  }

  const handleLogout = async () => {
    await signOut()
    router.push('/login')
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-gray-600">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-6">
            <h1 className="text-2xl font-bold">My Tasks</h1>
            <nav className="flex gap-4">
              <a
                href="/tasks"
                className="text-blue-600 font-medium"
              >
                Tasks
              </a>
              <a
                href="/chat"
                className="text-gray-600 hover:text-blue-600 transition-colors"
              >
                AI Chat
              </a>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">{user?.email}</span>
            <button
              onClick={handleLogout}
              className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 text-sm"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Add New Task</h2>
          <form onSubmit={handleAddTask} className="flex gap-2">
            <input
              type="text"
              value={newTask}
              onChange={(e) => setNewTask(e.target.value)}
              placeholder="What needs to be done?"
              className="flex-1 px-4 py-2 border rounded-md"
            />
            <button
              type="submit"
              className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700"
            >
              Add
            </button>
          </form>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Your Tasks</h2>
          
          {tasks.length === 0 ? (
            <p className="text-gray-500 text-center py-8">
              No tasks yet. Add one above!
            </p>
          ) : (
            <ul className="space-y-2">
              {tasks.map((task: Task) => (
                <li
                  key={task.id}
                  className="flex items-center gap-3 p-3 border rounded-md hover:bg-gray-50"
                >
                  <input
                    type="checkbox"
                    checked={task.completed || false}
                    onChange={() => handleToggle(task.id)}
                    className="w-5 h-5"
                  />
                  <span className={`flex-1 ${task.completed ? 'line-through text-gray-500' : ''}`}>
                    {task.title}
                  </span>
                  <button
                    onClick={() => handleDelete(task.id)}
                    className="text-red-600 hover:text-red-800 text-sm px-3"
                  >
                    Delete
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </main>
    </div>
  )
}
