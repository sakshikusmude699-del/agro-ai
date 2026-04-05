import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { predictionAPI } from '../services/api'
import { Sprout, Cloud, Thermometer, Droplets, ChevronRight, CheckCircle, RotateCcw } from 'lucide-react'

// ─── Step 1: Farm Input Form ──────────────────────────────────────────────────

function FarmInputForm({ onResult }) {
  const [form, setForm] = useState({
    nitrogen: '', phosphorus: '', potassium: '',
    ph: '', moisture: '', location: '', previous_crop: '',
    avoid_previous: true,
  })
  const [loading, setLoading] = useState(false)

  const set = (k) => (e) => setForm(p => ({ ...p, [k]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const payload = {
        soil: {
          nitrogen:   parseFloat(form.nitrogen),
          phosphorus: parseFloat(form.phosphorus),
          potassium:  parseFloat(form.potassium),
          ph:         parseFloat(form.ph),
          moisture:   parseFloat(form.moisture),
        },
        location:       form.location,
        previous_crop:  form.previous_crop || null,
        avoid_previous: form.avoid_previous,
      }
      const { data } = await predictionAPI.predict(payload)
      onResult(data)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Prediction failed. Check your inputs.')
    } finally {
      setLoading(false)
    }
  }

  const fields = [
    { key: 'nitrogen',   label: 'Nitrogen (N)',    unit: 'kg/ha', min: 0,   max: 140, hint: '0–140' },
    { key: 'phosphorus', label: 'Phosphorus (P)',  unit: 'kg/ha', min: 5,   max: 145, hint: '5–145' },
    { key: 'potassium',  label: 'Potassium (K)',   unit: 'kg/ha', min: 5,   max: 205, hint: '5–205' },
    { key: 'ph',         label: 'Soil pH',         unit: '',       min: 3.5, max: 10,  hint: '3.5–10' },
    { key: 'moisture',   label: 'Soil Moisture',   unit: '%',      min: 0,   max: 100, hint: '0–100' },
  ]

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Soil Parameters */}
      <div className="card">
        <h3 className="font-semibold text-soil-800 flex items-center gap-2 mb-5">
          <span className="text-xl">🧪</span> Soil Parameters
        </h3>
        <div className="grid sm:grid-cols-2 gap-4">
          {fields.map(({ key, label, unit, min, max, hint }) => (
            <div key={key}>
              <label className="label">
                {label} {unit && <span className="text-soil-400 font-normal text-xs">({unit})</span>}
              </label>
              <input
                type="number" step="0.1" required
                min={min} max={max}
                className="input-field"
                placeholder={hint}
                value={form[key]}
                onChange={set(key)}
              />
            </div>
          ))}
        </div>
      </div>

      {/* Location */}
      <div className="card">
        <h3 className="font-semibold text-soil-800 flex items-center gap-2 mb-5">
          <span className="text-xl">📍</span> Location & Weather
        </h3>
        <div>
          <label className="label">City / Town Name</label>
          <input type="text" required className="input-field"
            placeholder="e.g. Pune, Nagpur, Nashik, Aurangabad"
            value={form.location} onChange={set('location')} />
          <p className="text-xs text-soil-400 mt-1.5">
            Weather data (temperature, humidity, rainfall) is auto-fetched for this location.
          </p>
        </div>
      </div>

      {/* Crop Rotation */}
      <div className="card">
        <h3 className="font-semibold text-soil-800 flex items-center gap-2 mb-5">
          <RotateCcw size={18} className="text-leaf-600" /> Crop Rotation
        </h3>
        <div>
          <label className="label">Previous Crop <span className="text-soil-400 font-normal">(optional)</span></label>
          <input type="text" className="input-field"
            placeholder="e.g. wheat, rice, cotton"
            value={form.previous_crop} onChange={set('previous_crop')} />
        </div>
        {form.previous_crop && (
          <label className="flex items-center gap-2.5 mt-3 cursor-pointer">
            <input
              type="checkbox"
              checked={form.avoid_previous}
              onChange={e => setForm(p => ({ ...p, avoid_previous: e.target.checked }))}
              className="w-4 h-4 accent-leaf-600"
            />
            <span className="text-sm text-soil-700">
              Suggest rotation-friendly crops (avoid same crop)
            </span>
          </label>
        )}
      </div>

      <button type="submit" disabled={loading} className="btn-primary w-full text-base py-3">
        {loading ? (
          <span className="flex items-center justify-center gap-2">
            <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            Analyzing soil & fetching weather…
          </span>
        ) : (
          <span className="flex items-center justify-center gap-2">
            <Sprout size={18} /> Get Crop Recommendations
          </span>
        )}
      </button>
    </form>
  )
}

// ─── Step 2: Results ──────────────────────────────────────────────────────────

function PredictionResults({ data, onSelect, onBack }) {
  const [selected, setSelected] = useState(null)
  const [sowingDate, setSowingDate] = useState(new Date().toISOString().split('T')[0])
  const [confirming, setConfirming] = useState(false)
  const navigate = useNavigate()

  const allCrops = [
    ...data.recommendations,
    ...(data.previous_crop_option ? [data.previous_crop_option] : []),
  ]

  const handleConfirm = async () => {
    if (!selected) return
    setConfirming(true)
    try {
      await predictionAPI.selectCrop({
        prediction_id: data.prediction_id,
        selected_crop: selected.crop,
        sowing_date: sowingDate,
      })
      toast.success(`${selected.crop} selected! Your crop timeline is ready. 🌱`)
      navigate('/timeline')
    } catch (err) {
      toast.error('Failed to select crop. Try again.')
    } finally {
      setConfirming(false)
    }
  }

  return (
    <div className="space-y-6 animate-fade-in-up">
      {/* Weather summary */}
      <div className="card bg-gradient-to-r from-blue-50 to-sky-50 border-blue-100">
        <h3 className="font-semibold text-blue-800 mb-3 flex items-center gap-2">
          <Cloud size={18} /> Weather at {data.weather?.description || 'your location'}
        </h3>
        <div className="grid grid-cols-3 gap-3 text-center">
          <WeatherStat icon={<Thermometer size={16} />} label="Temp" value={`${data.weather.temperature}°C`} />
          <WeatherStat icon={<Droplets size={16} />}    label="Humidity" value={`${data.weather.humidity}%`} />
          <WeatherStat icon={<Cloud size={16} />}       label="Rainfall" value={`${data.weather.rainfall}mm`} />
        </div>
      </div>

      {/* Crop cards */}
      <div>
        <h3 className="font-semibold text-soil-800 mb-3">Recommended Crops — tap to select</h3>
        <div className="space-y-3">
          {allCrops.map((crop, i) => (
            <CropCard
              key={crop.crop}
              crop={crop}
              rank={i + 1}
              selected={selected?.crop === crop.crop}
              onClick={() => setSelected(crop)}
              isPrevious={!!data.previous_crop_option && crop.crop === data.previous_crop_option?.crop}
            />
          ))}
        </div>
      </div>

      {/* Sowing date */}
      {selected && (
        <div className="card border-leaf-200 bg-leaf-50 animate-fade-in-up">
          <label className="label text-leaf-800">Planned Sowing Date</label>
          <input type="date" className="input-field bg-white"
            value={sowingDate}
            min={new Date().toISOString().split('T')[0]}
            onChange={e => setSowingDate(e.target.value)} />
        </div>
      )}

      <div className="flex gap-3">
        <button onClick={onBack} className="btn-secondary flex-1">← Back</button>
        <button
          onClick={handleConfirm}
          disabled={!selected || confirming}
          className="btn-primary flex-1 flex items-center justify-center gap-2"
        >
          {confirming ? 'Saving…' : <>Confirm <ChevronRight size={16} /></>}
        </button>
      </div>
    </div>
  )
}

function CropCard({ crop, rank, selected, onClick, isPrevious }) {
  const MEDAL = ['🥇', '🥈', '🥉', '🔄']
  return (
    <button
      onClick={onClick}
      className={`w-full text-left p-4 rounded-xl border-2 transition-all duration-150 ${
        selected
          ? 'border-leaf-500 bg-leaf-50 shadow-md'
          : 'border-soil-200 bg-white hover:border-leaf-300 hover:bg-leaf-50/30'
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          <span className="text-xl mt-0.5">{MEDAL[rank - 1] || '🌿'}</span>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-semibold text-soil-900 capitalize">{crop.crop}</span>
              {isPrevious && (
                <span className="badge bg-amber-100 text-amber-700">Previous crop</span>
              )}
              {crop.is_rotation_friendly && (
                <span className="badge bg-leaf-100 text-leaf-700">✓ Rotation friendly</span>
              )}
            </div>
            <p className="text-sm text-soil-500 mt-1">{crop.reason}</p>
          </div>
        </div>
        <div className="flex flex-col items-end gap-1.5 flex-shrink-0">
          <span className={`text-sm font-bold ${crop.confidence > 70 ? 'text-leaf-600' : 'text-harvest-600'}`}>
            {crop.confidence}%
          </span>
          {selected && <CheckCircle size={18} className="text-leaf-600" />}
        </div>
      </div>
    </button>
  )
}

function WeatherStat({ icon, label, value }) {
  return (
    <div className="bg-white rounded-lg p-2.5">
      <div className="flex items-center justify-center gap-1 text-blue-400 text-xs mb-1">{icon}{label}</div>
      <p className="font-bold text-blue-800 text-sm">{value}</p>
    </div>
  )
}

// ─── Page Shell ───────────────────────────────────────────────────────────────

export default function RecommendPage() {
  const [result, setResult] = useState(null)

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6">
        <h1 className="font-display text-2xl font-bold text-soil-900">Crop Advisor</h1>
        <p className="text-soil-500 text-sm mt-1">
          Enter your soil data to get AI-powered crop recommendations
        </p>
      </div>

      {/* Step indicator */}
      <div className="flex items-center gap-2 mb-6">
        <StepBadge n={1} active={!result} done={!!result} label="Soil Input" />
        <div className={`flex-1 h-0.5 ${result ? 'bg-leaf-400' : 'bg-soil-200'}`} />
        <StepBadge n={2} active={!!result} done={false} label="Choose Crop" />
      </div>

      {!result
        ? <FarmInputForm onResult={setResult} />
        : <PredictionResults data={result} onBack={() => setResult(null)} />
      }
    </div>
  )
}

function StepBadge({ n, active, done, label }) {
  return (
    <div className="flex items-center gap-1.5">
      <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-colors ${
        done ? 'bg-leaf-500 text-white' : active ? 'bg-leaf-600 text-white' : 'bg-soil-200 text-soil-500'
      }`}>
        {done ? '✓' : n}
      </div>
      <span className={`text-xs font-medium ${active ? 'text-soil-800' : 'text-soil-400'}`}>{label}</span>
    </div>
  )
}
