import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Leaf, Mail, Lock, User, MapPin } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuth } from '../context/AuthContext'
import { authAPI } from '../services/api'

export default function RegisterPage() {
  const { login } = useAuth()
  const navigate  = useNavigate()
  const [form, setForm]       = useState({ name: '', email: '', password: '', location: '' })
  const [loading, setLoading] = useState(false)

  const set = (k) => (e) => setForm(p => ({ ...p, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const { data } = await authAPI.register(form)
      login(data.access_token, data.user)
      toast.success(`Welcome to AgroSmart, ${data.user.name}! 🌱`)
      navigate('/dashboard')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-soil-50 p-6">
      <div className="w-full max-w-md animate-fade-in-up">
        <div className="flex items-center gap-2.5 mb-8">
          <div className="w-10 h-10 bg-leaf-600 rounded-xl flex items-center justify-center">
            <Leaf size={22} className="text-white" />
          </div>
          <span className="font-display text-2xl font-bold text-soil-900">AgroSmart AI</span>
        </div>

        <div className="card">
          <h2 className="font-display text-2xl font-bold text-soil-900 mb-1">Create your account</h2>
          <p className="text-soil-500 text-sm mb-6">Start making smarter farming decisions</p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="label">Full Name</label>
              <div className="relative">
                <User size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-soil-400" />
                <input type="text" required className="input-field pl-10"
                  placeholder="Rajesh Patil"
                  value={form.name} onChange={set('name')} />
              </div>
            </div>

            <div>
              <label className="label">Email address</label>
              <div className="relative">
                <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-soil-400" />
                <input type="email" required className="input-field pl-10"
                  placeholder="you@example.com"
                  value={form.email} onChange={set('email')} />
              </div>
            </div>

            <div>
              <label className="label">Password</label>
              <div className="relative">
                <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-soil-400" />
                <input type="password" required minLength={6} className="input-field pl-10"
                  placeholder="Min 6 characters"
                  value={form.password} onChange={set('password')} />
              </div>
            </div>

            <div>
              <label className="label">Location <span className="text-soil-400 font-normal">(city name)</span></label>
              <div className="relative">
                <MapPin size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-soil-400" />
                <input type="text" className="input-field pl-10"
                  placeholder="e.g. Pune, Nagpur, Nashik"
                  value={form.location} onChange={set('location')} />
              </div>
            </div>

            <button type="submit" disabled={loading} className="btn-primary w-full mt-2">
              {loading ? 'Creating account…' : 'Create Account'}
            </button>
          </form>

          <p className="mt-5 text-center text-sm text-soil-500">
            Already have an account?{' '}
            <Link to="/login" className="text-leaf-600 font-semibold hover:underline">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
