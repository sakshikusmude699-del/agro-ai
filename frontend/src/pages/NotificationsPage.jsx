import React, { useEffect, useState } from 'react'

import toast from 'react-hot-toast'
import { notifAPI } from '../services/api'
import { Bell, CheckCircle, XCircle, SkipForward, RefreshCw } from 'lucide-react'

const STATUS_CONFIG = {
  sent:    { icon: <CheckCircle size={16} />, color: 'text-leaf-600 bg-leaf-50',  label: 'Sent' },
  failed:  { icon: <XCircle size={16} />,    color: 'text-red-500 bg-red-50',    label: 'Failed' },
  skipped: { icon: <SkipForward size={16} />, color: 'text-amber-600 bg-amber-50', label: 'Skipped' },
}

const TYPE_EMOJI = {
  irrigation: '💧', fertilizer: '🌿', pest_check: '🐛',
  harvest: '🌾', sowing: '🌱', rain_alert: '🌧️', general: '📬',
}

export default function NotificationsPage() {
  const [notifs, setNotifs]   = useState([])
  const [loading, setLoading] = useState(true)
  const [triggering, setTriggering] = useState(false)

  const load = async () => {
    try {
      const { data } = await notifAPI.getHistory()
      setNotifs(data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleTrigger = async () => {
    setTriggering(true)
    try {
      const { data } = await notifAPI.triggerCheck()
      toast.success(data.message)
      await load()
    } catch {
      toast.error('Failed to trigger notification check')
    } finally {
      setTriggering(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="font-display text-2xl font-bold text-soil-900">Notification History</h1>
          <p className="text-soil-500 text-sm mt-1">All alerts and reminders sent to you</p>
        </div>
        <button
          onClick={handleTrigger}
          disabled={triggering}
          className="btn-secondary flex items-center gap-2 text-sm"
        >
          <RefreshCw size={15} className={triggering ? 'animate-spin' : ''} />
          {triggering ? 'Checking…' : 'Test Alerts'}
        </button>
      </div>

      {loading ? (
        <div className="space-y-3">
          {[1,2,3].map(i => <div key={i} className="h-20 bg-soil-100 rounded-xl animate-pulse" />)}
        </div>
      ) : notifs.length === 0 ? (
        <div className="text-center py-20">
          <Bell size={48} className="text-soil-200 mx-auto mb-4" />
          <p className="text-soil-500 font-medium">No notifications yet</p>
          <p className="text-soil-400 text-sm mt-1">
            Alerts are sent daily at 7:00 AM when you have an active crop.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {notifs.map((n) => {
            const status = STATUS_CONFIG[n.status] || STATUS_CONFIG.sent
            return (
              <div key={n._id} className="card hover:shadow-md transition-shadow">
                <div className="flex items-start gap-3">
                  <span className="text-2xl mt-0.5 flex-shrink-0">
                    {TYPE_EMOJI[n.task_type] || '📬'}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap mb-1">
                      <span className="font-semibold text-soil-800 capitalize">
                        {n.task_type?.replace('_', ' ') || 'Alert'}
                      </span>
                      <span className={`badge ${status.color} flex items-center gap-1`}>
                        {status.icon}{status.label}
                      </span>
                      {n.crop && (
                        <span className="badge bg-leaf-50 text-leaf-700 capitalize">
                          {n.crop}
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-soil-600">{n.message}</p>
                    <p className="text-xs text-soil-400 mt-1.5">{n.date}</p>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
