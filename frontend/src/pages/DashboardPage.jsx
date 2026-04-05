import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { timelineAPI, notifAPI } from '../services/api'
import { Sprout, CalendarDays, Bell, MessageCircle, TrendingUp, CheckCircle2, Clock } from 'lucide-react'

export default function DashboardPage() {
  const { user } = useAuth()
  const [timeline, setTimeline]   = useState(null)
  const [notifCount, setNotifCount] = useState(0)
  const [loading, setLoading]     = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const [tl, notifs] = await Promise.allSettled([
          timelineAPI.getActive(),
          notifAPI.getHistory(),
        ])
        if (tl.status === 'fulfilled') setTimeline(tl.value.data)
        if (notifs.status === 'fulfilled') setNotifCount(notifs.value.data.length)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const hour = new Date().getHours()
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening'

  const todayTasks = timeline?.tasks?.filter(t =>
    t.scheduled_date === new Date().toISOString().split('T')[0] && !t.completed
  ) || []

  const completedTasks = timeline?.tasks?.filter(t => t.completed).length || 0
  const totalTasks     = timeline?.tasks?.length || 0
  const progress       = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8 animate-fade-in-up">
        <h1 className="font-display text-3xl font-bold text-soil-900">
          {greeting}, {user?.name?.split(' ')[0]} 👋
        </h1>
        <p className="text-soil-500 mt-1">
          {new Date().toLocaleDateString('en-IN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
        </p>
      </div>

      {/* Active crop card */}
      {loading ? (
        <div className="card mb-6 animate-pulse h-32 bg-soil-100" />
      ) : timeline ? (
        <div className="card mb-6 bg-gradient-to-br from-leaf-700 to-leaf-600 text-white border-0 animate-fade-in-up">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-leaf-200 text-sm font-medium mb-1">Active Crop</p>
              <h2 className="font-display text-2xl font-bold capitalize">{timeline.crop}</h2>
              <p className="text-leaf-100 text-sm mt-1">
                Day {timeline.current_day} of {timeline.total_days} · Sown {timeline.sowing_date}
              </p>
            </div>
            <div className="bg-white/20 rounded-2xl p-3 backdrop-blur-sm">
              <Sprout size={28} className="text-white" />
            </div>
          </div>
          {/* Progress bar */}
          <div className="mt-5">
            <div className="flex justify-between text-xs text-leaf-200 mb-1.5">
              <span>{completedTasks} tasks done</span>
              <span>{progress}% complete</span>
            </div>
            <div className="h-2 bg-white/20 rounded-full overflow-hidden">
              <div
                className="h-full bg-white rounded-full transition-all duration-700"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        </div>
      ) : (
        <div className="card mb-6 border-dashed border-2 border-soil-200 flex flex-col items-center justify-center py-10 animate-fade-in-up">
          <Sprout size={40} className="text-soil-300 mb-3" />
          <p className="text-soil-500 font-medium mb-4">No active crop yet</p>
          <Link to="/recommend" className="btn-primary text-sm">Get Crop Recommendations →</Link>
        </div>
      )}

      {/* Quick stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8 stagger">
        <StatCard icon={<Sprout size={20} className="text-leaf-600" />}
          label="Active Crop" value={timeline?.crop ? timeline.crop.charAt(0).toUpperCase() + timeline.crop.slice(1) : '—'} bg="bg-leaf-50" />
        <StatCard icon={<CalendarDays size={20} className="text-harvest-600" />}
          label="Day" value={timeline ? `${timeline.current_day} / ${timeline.total_days}` : '—'} bg="bg-harvest-50" />
        <StatCard icon={<CheckCircle2 size={20} className="text-blue-600" />}
          label="Tasks Done" value={timeline ? `${completedTasks} / ${totalTasks}` : '—'} bg="bg-blue-50" />
        <StatCard icon={<Bell size={20} className="text-purple-600" />}
          label="Alerts Sent" value={notifCount} bg="bg-purple-50" />
      </div>

      {/* Today's tasks */}
      {todayTasks.length > 0 && (
        <div className="card mb-6 animate-fade-in-up">
          <h3 className="font-semibold text-soil-800 flex items-center gap-2 mb-4">
            <Clock size={18} className="text-harvest-500" />
            Today's Tasks
          </h3>
          <div className="space-y-3">
            {todayTasks.map((task) => (
              <div key={task.day} className="flex items-start gap-3 p-3 bg-harvest-50 rounded-xl border border-harvest-100">
                <div className="w-8 h-8 bg-harvest-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <span className="text-lg">{TASK_EMOJI[task.task_type] || '📋'}</span>
                </div>
                <div>
                  <p className="font-medium text-soil-800 text-sm">{task.title}</p>
                  <p className="text-xs text-soil-500 mt-0.5">{task.description.slice(0, 80)}…</p>
                </div>
              </div>
            ))}
          </div>
          <Link to="/timeline" className="text-leaf-600 text-sm font-semibold hover:underline mt-3 inline-block">
            View full timeline →
          </Link>
        </div>
      )}

      {/* Quick actions */}
      <div className="grid sm:grid-cols-2 gap-4 stagger">
        <QuickAction to="/recommend" icon="🌾" title="Get Crop Advice" desc="Enter soil data and get AI recommendations" color="leaf" />
        <QuickAction to="/chat" icon="🤖" title="Ask AI Assistant" desc="Get instant answers to your farming questions" color="harvest" />
        <QuickAction to="/timeline" icon="📅" title="View Timeline" desc="Track your crop's day-wise activities" color="blue" />
        <QuickAction to="/notifications" icon="🔔" title="Notification History" desc="Review all alerts and reminders sent" color="purple" />
      </div>
    </div>
  )
}

const TASK_EMOJI = {
  sowing: '🌱', irrigation: '💧', fertilizer: '🌿',
  pest_check: '🐛', harvest: '🌾',
}

function StatCard({ icon, label, value, bg }) {
  return (
    <div className={`card ${bg} p-4`}>
      <div className="flex items-center gap-2 mb-2">{icon}<span className="text-xs text-soil-500 font-medium">{label}</span></div>
      <p className="font-bold text-soil-900 text-lg capitalize">{value}</p>
    </div>
  )
}

function QuickAction({ to, icon, title, desc, color }) {
  const colors = {
    leaf:    'hover:border-leaf-300 hover:bg-leaf-50',
    harvest: 'hover:border-harvest-300 hover:bg-harvest-50',
    blue:    'hover:border-blue-300 hover:bg-blue-50',
    purple:  'hover:border-purple-300 hover:bg-purple-50',
  }
  return (
    <Link to={to} className={`card flex items-start gap-4 transition-all duration-150 ${colors[color]} group`}>
      <span className="text-2xl mt-0.5">{icon}</span>
      <div>
        <p className="font-semibold text-soil-800 group-hover:text-soil-900">{title}</p>
        <p className="text-sm text-soil-500 mt-0.5">{desc}</p>
      </div>
    </Link>
  )
}
