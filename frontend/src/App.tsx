import { DailyLogs } from './components/DailyLogs'
import { TripForm } from './components/TripForm'
import { TripSummary } from './components/TripSummary'

import { useTripPlanner } from './hooks/useTripPlanner'
import type { TripFormValues } from './types/trip'

const initialForm: TripFormValues = {
  current_location: 'Chicago, IL',
  pickup_location: 'Dallas, TX',
  dropoff_location: 'Phoenix, AZ',
  departure_at: '2026-10-05T08:00',
  current_cycle_used: '12',
}

function App() {
  const { result, loading, error, submitTrip, startNewTrip } = useTripPlanner()

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-5 sm:px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-600 text-lg font-black text-white shadow-lg shadow-emerald-200">S</div>
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.18em] text-emerald-600">Driver operations</p>
              <h1 className="text-lg font-bold tracking-tight text-slate-900 sm:text-xl">Trip planner</h1>
            </div>
          </div>
          {result ? (
            <button type="button" onClick={startNewTrip} className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-bold text-white shadow-sm transition hover:bg-emerald-700 focus:outline-none focus:ring-4 focus:ring-emerald-100">
              New trip
            </button>
          ) : (
            <div className="hidden items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-700 sm:flex">
              <span className="h-2 w-2 rounded-full bg-emerald-500" />
              HOS compliant
            </div>
          )}
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-5 py-8 sm:px-8 lg:py-10">
        <div className="mb-8 max-w-2xl">
          <p className="mb-2 text-sm font-semibold text-emerald-600">{result ? 'Trip workspace' : 'Plan with confidence'}</p>
          <h2 className="text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl">{result ? 'Your route is ready.' : 'Build a safer route in seconds.'}</h2>
          <p className="mt-3 text-base leading-7 text-slate-500">{result ? 'Review the route, stops, and daily logs below.' : 'Enter your trip details and get a clear route, driving estimate, and compliant daily logs.'}</p>
        </div>
        {result ? (
          <div className="space-y-6">
            <TripSummary result={result} />
            <DailyLogs logs={result.hos?.daily_logs ?? []} />
          </div>
        ) : (
          <div className="grid items-start gap-6 lg:grid-cols-[360px_minmax(0,1fr)]">
            <TripForm initialValues={initialForm} loading={loading} error={error} onSubmit={submitTrip} />
            <div className="flex min-h-[420px] flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center shadow-sm">
              <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-50 text-2xl">✦</div>
              <h2 className="text-lg font-bold text-slate-900">Your trip plan will appear here</h2>
              <p className="mt-2 max-w-sm text-sm leading-6 text-slate-500">Complete the trip details to see your route overview, HOS summary, and ELD logs.</p>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
