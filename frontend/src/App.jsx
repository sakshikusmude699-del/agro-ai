import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'

import LoginPage        from './pages/LoginPage'
import RegisterPage     from './pages/RegisterPage'
import DashboardPage    from './pages/DashboardPage'
import RecommendPage    from './pages/RecommendPage'
import TimelinePage     from './pages/TimelinePage'
import NotificationsPage from './pages/NotificationsPage'
import ChatPage         from './pages/ChatPage'
import Layout           from './components/Layout'

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="min-h-screen flex items-center justify-center"><Spinner /></div>
  return user ? children : <Navigate to="/login" replace />
}

function Spinner() {
  return (
    <div className="w-10 h-10 border-4 border-leaf-200 border-t-leaf-600 rounded-full animate-spin" />
  )
}

function AppRoutes() {
  const { user } = useAuth()
  return (
    <Routes>
      <Route path="/login"    element={user ? <Navigate to="/dashboard" /> : <LoginPage />} />
      <Route path="/register" element={user ? <Navigate to="/dashboard" /> : <RegisterPage />} />

      <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route index          element={<Navigate to="/dashboard" />} />
        <Route path="dashboard"     element={<DashboardPage />} />
        <Route path="recommend"     element={<RecommendPage />} />
        <Route path="timeline"      element={<TimelinePage />} />
        <Route path="notifications" element={<NotificationsPage />} />
        <Route path="chat"          element={<ChatPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/dashboard" />} />
    </Routes>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  )
}
