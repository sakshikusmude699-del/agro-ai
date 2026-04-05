import React, { useState } from 'react'
import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import {
  LayoutDashboard, Sprout, CalendarDays, Bell,
  MessageCircle, LogOut, Menu, X, Leaf
} from 'lucide-react'

const NAV_ITEMS = [
  { to: '/dashboard',     icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/recommend',     icon: Sprout,           label: 'Crop Advisor' },
  { to: '/timeline',      icon: CalendarDays,     label: 'Timeline' },
  { to: '/notifications', icon: Bell,             label: 'Alerts' },
  { to: '/chat',          icon: MessageCircle,    label: 'AI Chat' },
]

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [mobileOpen, setMobileOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const NavItem = ({ to, icon: Icon, label }) => (
    <NavLink
      to={to}
      onClick={() => setMobileOpen(false)}
      className={({ isActive }) =>
        `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-150 ${
          isActive
            ? 'bg-leaf-600 text-white shadow-sm'
            : 'text-soil-600 hover:bg-soil-100 hover:text-soil-900'
        }`
      }
    >
      <Icon size={18} />
      {label}
    </NavLink>
  )

  const Sidebar = () => (
    <aside className="flex flex-col h-full bg-white border-r border-soil-100 w-64 py-6 px-4">
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-2 mb-8">
        <div className="w-9 h-9 bg-leaf-600 rounded-xl flex items-center justify-center shadow-sm">
          <Leaf size={20} className="text-white" />
        </div>
        <div>
          <div className="font-display font-bold text-soil-900 leading-tight">AgroSmart</div>
          <div className="text-xs text-leaf-600 font-semibold">AI Farming Assistant</div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex flex-col gap-1 flex-1">
        {NAV_ITEMS.map((item) => <NavItem key={item.to} {...item} />)}
      </nav>

      {/* User info + logout */}
      <div className="mt-4 border-t border-soil-100 pt-4">
        <div className="flex items-center gap-3 px-2 mb-3">
          <div className="w-8 h-8 rounded-full bg-harvest-200 flex items-center justify-center text-sm font-bold text-harvest-700">
            {user?.name?.[0]?.toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-sm font-semibold text-soil-800 truncate">{user?.name}</div>
            <div className="text-xs text-soil-500 truncate">{user?.location || 'No location'}</div>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center gap-2 w-full px-4 py-2.5 rounded-xl text-sm text-red-600 hover:bg-red-50 transition-colors"
        >
          <LogOut size={16} />
          Logout
        </button>
      </div>
    </aside>
  )

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Desktop Sidebar */}
      <div className="hidden md:flex flex-shrink-0">
        <Sidebar />
      </div>

      {/* Mobile Sidebar Overlay */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <div className="absolute inset-0 bg-black/40" onClick={() => setMobileOpen(false)} />
          <div className="absolute left-0 top-0 h-full">
            <Sidebar />
          </div>
        </div>
      )}

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Mobile header */}
        <header className="md:hidden flex items-center gap-3 px-4 py-4 bg-white border-b border-soil-100">
          <button onClick={() => setMobileOpen(true)} className="text-soil-600">
            <Menu size={22} />
          </button>
          <div className="flex items-center gap-2">
            <Leaf size={18} className="text-leaf-600" />
            <span className="font-display font-bold text-soil-900">AgroSmart AI</span>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-4 md:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
