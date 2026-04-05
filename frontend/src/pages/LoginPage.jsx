import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Leaf, Mail, Lock, Eye, EyeOff } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuth } from '../context/AuthContext'
import { authAPI } from '../services/api'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate  = useNavigate()
  const [form, setForm]       = useState({ email: '', password: '' })
  const [loading, setLoading] = useState(false)
  const [showPass, setShowPass] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const { data } = await authAPI.login(form)
      login(data.access_token, data.user)
      toast.success(`Welcome back, ${data.user.name}! 🌱`)
      navigate('/dashboard')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex">
      {/* Left panel — decorative */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-leaf-800 to-leaf-600 relative overflow-hidden items-center justify-center">
        <div className="absolute inset-0 opacity-10">
          {/* Decorative field pattern */}
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="absolute border border-white/20 rounded-full"
              style={{ width: `${(i + 1) * 12}%`, height: `${(i + 1) * 12}%`,
                       top: '50%', left: '50%', transform: 'translate(-50%, -50%)' }} />
          ))}
        </div>
        <div className="relative z-10 text-center text-white px-12">
          <div className="w-20 h-20 bg-white/20 rounded-3xl flex items-center justify-center mx-auto mb-6 backdrop-blur-sm">
            <Leaf size={40} className="text-white" />
          </div>
          <h1 className="font-display text-4xl font-bold mb-3">AgroSmart AI</h1>
          <p className="text-leaf-100 text-lg">Your intelligent farming companion</p>
          <div className="mt-10 grid grid-cols-2 gap-4 text-sm">
            {['🌱 Smart crop selection','🌦️ Weather integration','📅 Crop lifecycle tracking','🔔 Smart notifications'].map(t => (
              <div key={t} className="bg-white/10 rounded-xl px-4 py-3 text-left backdrop-blur-sm">{t}</div>
            ))}
          </div>
        </div>
      </div>

      {/* Right panel — form */}
      <div className="flex-1 flex items-center justify-center p-6 bg-soil-50">
        <div className="w-full max-w-md animate-fade-in-up">
          {/* Mobile logo */}
          <div className="lg:hidden flex items-center gap-2 mb-8">
            <div className="w-10 h-10 bg-leaf-600 rounded-xl flex items-center justify-center">
              <Leaf size={22} className="text-white" />
            </div>
            <span className="font-display text-2xl font-bold text-soil-900">AgroSmart AI</span>
          </div>

          <h2 className="font-display text-3xl font-bold text-soil-900 mb-1">Welcome back</h2>
          <p className="text-soil-500 mb-8">Sign in to your farming dashboard</p>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="label">Email address</label>
              <div className="relative">
                <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-soil-400" />
                <input
                  type="email" required
                  className="input-field pl-10"
                  placeholder="you@example.com"
                  value={form.email}
                  onChange={e => setForm(p => ({ ...p, email: e.target.value }))}
                />
              </div>
            </div>

            <div>
              <label className="label">Password</label>
              <div className="relative">
                <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-soil-400" />
                <input
                  type={showPass ? 'text' : 'password'} required
                  className="input-field pl-10 pr-10"
                  placeholder="••••••••"
                  value={form.password}
                  onChange={e => setForm(p => ({ ...p, password: e.target.value }))}
                />
                <button type="button" onClick={() => setShowPass(p => !p)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-soil-400 hover:text-soil-600">
                  {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <button type="submit" disabled={loading} className="btn-primary w-full text-center">
              {loading ? 'Signing in…' : 'Sign In'}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-soil-500">
            Don't have an account?{' '}
            <Link to="/register" className="text-leaf-600 font-semibold hover:underline">
              Create one free
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
