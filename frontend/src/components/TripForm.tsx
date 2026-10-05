import { useState } from 'react'
import type { ChangeEvent, FormEvent, ReactNode } from 'react'
import type { TripFormValues } from '../types/trip'

type TripFormProps = {
  initialValues: TripFormValues
  loading: boolean
  error: string
  onSubmit: (values: TripFormValues) => Promise<void>
}

export function TripForm({ initialValues, loading, error, onSubmit }: TripFormProps) {
  const [form, setForm] = useFormValues(initialValues)

  const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = event.target
    setForm((previous) => ({ ...previous, [name]: value }))
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    await onSubmit(form)
  }

  return (
    <section className="sticky top-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
      <div className="mb-6">
        <p className="mb-1 text-xs font-bold uppercase tracking-[0.16em] text-emerald-600">New itinerary</p>
        <h2 className="text-xl font-bold text-slate-900">Trip details</h2>
        <p className="mt-1 text-sm text-slate-500">Tell us where you’re headed.</p>
      </div>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Field label="Current location">
          <input className="field-input" name="current_location" value={form.current_location} onChange={handleChange} placeholder="Current city or address" required />
        </Field>
        <Field label="Pickup location">
          <input className="field-input" name="pickup_location" value={form.pickup_location} onChange={handleChange} placeholder="Pickup city or address" required />
        </Field>
        <Field label="Dropoff location">
          <input className="field-input" name="dropoff_location" value={form.dropoff_location} onChange={handleChange} placeholder="Dropoff city or address" required />
        </Field>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2">
          <Field label="Departure time">
            <input className="field-input" type="datetime-local" name="departure_at" value={form.departure_at} onChange={handleChange} required />
          </Field>
          <Field label="Cycle used (hrs)">
            <input className="field-input" type="number" min="0" max="70" step="0.1" name="current_cycle_used" value={form.current_cycle_used} onChange={handleChange} required />
          </Field>
        </div>
        <button className="flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-600 px-4 py-3 text-sm font-bold text-white shadow-lg shadow-emerald-200 transition hover:bg-emerald-700 focus:outline-none focus:ring-4 focus:ring-emerald-100 disabled:cursor-wait disabled:opacity-60" type="submit" disabled={loading}>
          {loading ? <><span className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" /> Planning route...</> : <>Plan trip <span aria-hidden="true">→</span></>}
        </button>
      </form>
      {error ? <div className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm leading-5 text-red-700">{error}</div> : null}
    </section>
  )
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="block text-sm font-semibold text-slate-700">
      {label}
      <span className="mt-2 block">{children}</span>
    </label>
  )
}

function useFormValues(initialValues: TripFormValues) {
  const [form, setForm] = useState(initialValues)
  return [form, setForm] as const
}
