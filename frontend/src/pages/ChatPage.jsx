import React, { useState, useRef, useEffect } from 'react'
import toast from 'react-hot-toast'
import { chatAPI } from '../services/api'
import { Send, Leaf } from 'lucide-react'

const STARTER_QUESTIONS = [
  'Which crop should I grow this season?',
  'What fertilizer is best for wheat?',
  'How often should I irrigate rice?',
  'How to control bollworm in cotton?',
  'What is crop rotation and why is it important?',
]

const LANG_OPTIONS = [
  { code: 'en', label: '🇬🇧 English' },
  { code: 'hi', label: '🇮🇳 हिंदी' },
  { code: 'mr', label: '🌸 मराठी' },
]

export default function ChatPage() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: 'Namaste! 🌱 I am AgroSmart AI, your personal farming assistant. Ask me anything about crops, soil, fertilizers, or pest control. I can also answer in Hindi or Marathi!',
    },
  ])
  const [input, setInput]     = useState('')
  const [loading, setLoading] = useState(false)
  const [language, setLang]   = useState('en')
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async (text) => {
    const userMsg = text || input.trim()
    if (!userMsg) return

    setMessages(prev => [...prev, { role: 'user', text: userMsg }])
    setInput('')
    setLoading(true)

    try {
      const { data } = await chatAPI.send(userMsg, language)
      setMessages(prev => [...prev, { role: 'assistant', text: data.reply }])
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant',
        text: 'Sorry, I had trouble responding. Please try again.',
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto flex flex-col" style={{ height: 'calc(100vh - 8rem)' }}>
      {/* Header */}
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold text-soil-900">AI Farming Assistant</h1>
          <p className="text-soil-500 text-sm">Ask anything about farming, crops, and soil</p>
        </div>
        {/* Language selector */}
        <select
          value={language}
          onChange={e => setLang(e.target.value)}
          className="input-field w-auto text-sm py-2"
        >
          {LANG_OPTIONS.map(l => <option key={l.code} value={l.code}>{l.label}</option>)}
        </select>
      </div>

      {/* Chat window */}
      <div className="flex-1 overflow-y-auto card p-4 space-y-4 mb-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in-up`}>
            {msg.role === 'assistant' && (
              <div className="w-8 h-8 bg-leaf-600 rounded-full flex items-center justify-center mr-2.5 flex-shrink-0 mt-0.5">
                <Leaf size={14} className="text-white" />
              </div>
            )}
            <div className={`max-w-[85%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
              msg.role === 'user'
                ? 'bg-leaf-600 text-white rounded-tr-none'
                : 'bg-soil-100 text-soil-800 rounded-tl-none'
            }`}>
              {msg.text}
            </div>
          </div>
        ))}

        {/* Typing indicator */}
        {loading && (
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 bg-leaf-600 rounded-full flex items-center justify-center flex-shrink-0">
              <Leaf size={14} className="text-white" />
            </div>
            <div className="bg-soil-100 px-4 py-3 rounded-2xl rounded-tl-none flex gap-1">
              <span className="w-2 h-2 bg-soil-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <span className="w-2 h-2 bg-soil-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <span className="w-2 h-2 bg-soil-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Starter questions */}
      {messages.length <= 1 && (
        <div className="flex gap-2 mb-3 overflow-x-auto pb-1">
          {STARTER_QUESTIONS.map(q => (
            <button key={q} onClick={() => sendMessage(q)}
              className="px-3 py-2 bg-white border border-soil-200 rounded-xl text-xs text-soil-600 hover:bg-leaf-50 hover:border-leaf-300 whitespace-nowrap transition-colors flex-shrink-0">
              {q}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="flex gap-2">
        <input
          type="text"
          className="input-field flex-1"
          placeholder="Ask about crops, soil, pest control…"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
          disabled={loading}
        />
        <button
          onClick={() => sendMessage()}
          disabled={!input.trim() || loading}
          className="btn-primary px-4 flex-shrink-0"
        >
          <Send size={18} />
        </button>
      </div>
    </div>
  )
}
