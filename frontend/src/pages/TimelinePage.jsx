import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import { timelineAPI } from '../services/api'
import { CheckCircle2, Circle, Sprout, SkipForward } from 'lucide-react'
import { format } from 'date-fns'

const TASK_CONFIG = {
  sowing:     { emoji: '🌱', color: 'bg-emerald-50 border-emerald-200', badge: 'text-emerald-700 bg-emerald-100' },
  irrigation: { emoji: '💧', color: 'bg-blue-50 border-blue-200',      badge: 'text-blue-700 bg-blue-100' },
  fertilizer: { emoji: '🌿', color: 'bg-green-50 border-green-200',    badge: 'text-green-700 bg-green-100' },
  pest_check: { emoji: '🐛', color: 'bg-orange-50 border-orange-200',  badge: 'text-orange-700 bg-orange-100' },
  harvest:    { emoji: '🌾', color: 'bg-amber-50 border-amber-200',    badge: 'text-amber-700 bg-amber-100' },
}

export default function TimelinePage() {
  const [timeline, setTimeline] = useState(null)
  const [loading, setLoading]   = useState(true)
  const [filter, setFilter]     = useState('all')  // all | today | upcoming | done

  const load = async () => {
    try {
      const { data } = await timelineAPI.getActive()
      setTimeline(data)
    } catch {
      setTimeline(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleComplete = async (day) => {
    try {
      await timelineAPI.completeTask(timeline._id, day)
      toast.success('Task marked complete! ✅')
      load()
    } catch {
      toast.error('Failed to update task')
    }
  }

  if (loading) return <LoadingSkeleton />

  if (!timeline) return (
    <div className="max-w-2xl mx-auto text-center py-20">
      <Sprout size={48} className="text-soil-300 mx-auto mb-4" />
      <h2 className="font-display text-xl font-bold text-soil-700 mb-2">No active crop</h2>
      <p className="text-soil-500 mb-6">Get crop recommendations to start tracking your crop lifecycle.</p>
      <Link to="/recommend" className="btn-primary">Get Recommendations →</Link>
    </div>
  )

  const today = new Date().toISOString().split('T')[0]
  const filteredTasks = timeline.tasks.filter(t => {
    if (filter === 'today')    return t.scheduled_date === today
    if (filter === 'upcoming') return t.scheduled_date > today && !t.completed
    if (filter === 'done')     return t.completed || t.skipped
    return true
  })

  const done  = timeline.tasks.filter(t => t.completed).length
  const total = timeline.tasks.length
  const prog  = Math.round((done / total) * 100)

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-6">
        <h1 className="font-display text-2xl font-bold text-soil-900 capitalize">
          {timeline.crop} Timeline
        </h1>
        <p className="text-soil-500 text-sm mt-1">
          Day {timeline.current_day} of {timeline.total_days} · Sown on {timeline.sowing_date}
        </p>
      </div>

      {/* Progress */}
      <div className="card mb-6 bg-gradient-to-r from-leaf-700 to-leaf-600 text-white border-0">
        <div className="flex justify-between items-center mb-2">
          <span className="text-leaf-100 text-sm">Overall Progress</span>
          <span className="font-bold">{prog}%</span>
        </div>
        <div className="h-2.5 bg-white/20 rounded-full overflow-hidden">
          <div className="h-full bg-white rounded-full transition-all duration-700" style={{ width: `${prog}%` }} />
        </div>
        <p className="text-leaf-200 text-xs mt-2">{done} of {total} tasks completed</p>
      </div>

      {/* Filters */}
      <div className="flex gap-2 mb-5 overflow-x-auto pb-1">
        {[
          { key: 'all',      label: 'All Tasks' },
          { key: 'today',    label: "Today's" },
          { key: 'upcoming', label: 'Upcoming' },
          { key: 'done',     label: 'Completed' },
        ].map(f => (
          <button key={f.key}
            onClick={() => setFilter(f.key)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
              filter === f.key ? 'bg-leaf-600 text-white' : 'bg-white text-soil-600 border border-soil-200 hover:bg-soil-50'
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Task list */}
      <div className="space-y-3">
        {filteredTasks.length === 0 ? (
          <div className="text-center py-12 text-soil-400">
            <p className="text-4xl mb-2">🔍</p>
            <p>No tasks in this view</p>
          </div>
        ) : filteredTasks.map((task) => {
          const cfg = TASK_CONFIG[task.task_type] || TASK_CONFIG.sowing
          const isToday    = task.scheduled_date === today
          const isPast     = task.scheduled_date < today
          const isDone     = task.completed
          const isSkipped  = task.skipped

          return (
            <div key={task.day}
              className={`p-4 rounded-xl border-2 transition-all ${
                isDone || isSkipped ? 'opacity-60 bg-soil-50 border-soil-200' :
                isToday ? `${cfg.color} shadow-sm` : 'bg-white border-soil-100'
              }`}
            >
              <div className="flex items-start gap-3">
                {/* Status icon */}
                <button
                  disabled={isDone || isSkipped}
                  onClick={() => handleComplete(task.day)}
                  className={`mt-0.5 flex-shrink-0 ${isDone ? 'text-leaf-500' : isSkipped ? 'text-soil-300' : 'text-soil-300 hover:text-leaf-500 transition-colors'}`}
                >
                  {isDone ? <CheckCircle2 size={22} /> : isSkipped ? <SkipForward size={22} /> : <Circle size={22} />}
                </button>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-lg">{cfg.emoji}</span>
                    <span className={`font-semibold text-soil-800 ${isDone ? 'line-through' : ''}`}>
                      {task.title}
                    </span>
                    <span className={`badge ${cfg.badge} capitalize`}>{task.task_type.replace('_', ' ')}</span>
                    {isToday && !isDone && (
                      <span className="badge bg-red-100 text-red-600 animate-pulse-green">Today</span>
                    )}
                    {isSkipped && (
                      <span className="badge bg-soil-100 text-soil-500">Skipped</span>
                    )}
                  </div>
                  <p className="text-sm text-soil-500 mt-1">{task.description}</p>
                  <div className="flex items-center gap-3 mt-2 text-xs text-soil-400">
                    <span>Day {task.day}</span>
                    <span>·</span>
                    <span>{task.scheduled_date}</span>
                    {task.skip_reason && <span className="text-amber-600">· {task.skip_reason}</span>}
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function LoadingSkeleton() {
  return (
    <div className="max-w-3xl mx-auto animate-pulse">
      <div className="h-8 bg-soil-200 rounded-lg w-64 mb-2" />
      <div className="h-4 bg-soil-100 rounded w-48 mb-6" />
      <div className="h-20 bg-soil-200 rounded-2xl mb-6" />
      {[1,2,3,4].map(i => <div key={i} className="h-20 bg-soil-100 rounded-xl mb-3" />)}
    </div>
  )
}
