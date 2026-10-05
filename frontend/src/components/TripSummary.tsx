import { useMemo } from 'react'
import type { TripPlanResponse } from '../types/trip'

type TripSummaryProps = {
  result: TripPlanResponse
}

export function TripSummary({ result }: TripSummaryProps) {
  const routePoints = useRoutePoints(result)
  const locations = result.locations

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
      <div className="mb-5 flex items-end justify-between gap-3">
        <div><p className="mb-1 text-xs font-bold uppercase tracking-[0.16em] text-emerald-600">At a glance</p><h2 className="text-xl font-bold text-slate-900">Trip summary</h2></div>
        <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-bold text-emerald-700">Ready to drive</span>
      </div>
      <div className="grid grid-cols-2 gap-3 xl:grid-cols-4">
        <Stat label="Total distance" value={`${result.route?.distance_miles ?? 0} mi`} />
        <Stat label="Driving time" value={`${result.route?.duration_hours ?? 0} hrs`} />
        <Stat label="Cycle used" value={`${result.hos?.summary?.cycle_hours_used ?? 0} hrs`} />
        <Stat label="Daily logs" value={String(result.hos?.daily_logs?.length ?? 0)} />
      </div>
      <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
        <h3 className="mb-3 text-sm font-bold text-slate-900">Route overview</h3>
        {routePoints ? (
          <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="route-map">
            <defs><linearGradient id="route-grid" x1="0" x2="0" y1="0" y2="1"><stop stopColor="#ecfdf5" /><stop offset="1" stopColor="#d1fae5" /></linearGradient></defs>
            <rect x="0" y="0" width="100" height="100" rx="4" fill="url(#route-grid)" />
            <path d="M0 25H100M0 50H100M0 75H100M25 0V100M50 0V100M75 0V100" stroke="#a7f3d0" strokeWidth=".35" />
            <polyline points={routePoints} fill="none" stroke="#059669" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        ) : <div className="empty-map">No route geometry available.</div>}
        <div className="mt-4 grid gap-2 text-sm text-slate-600 sm:grid-cols-3">
          <RouteStop color="bg-slate-400" label="Current" value={locations?.current?.display_name ?? 'Current location'} />
          <RouteStop color="bg-amber-400" label="Pickup" value={locations?.pickup?.display_name ?? 'Pickup location'} />
          <RouteStop color="bg-emerald-500" label="Dropoff" value={locations?.dropoff?.display_name ?? 'Dropoff location'} />
        </div>
      </div>
    </section>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return <div className="rounded-xl border border-slate-200 bg-white px-4 py-3"><span className="block text-[11px] font-bold uppercase tracking-wider text-slate-400">{label}</span><strong className="mt-1 block text-xl font-bold text-slate-900">{value}</strong></div>
}

function RouteStop({ color, label, value }: { color: string; label: string; value: string }) {
  return <div className="flex min-w-0 items-start gap-2"><span className={`mt-1.5 h-2.5 w-2.5 shrink-0 rounded-full ${color}`} /><span className="min-w-0"><span className="block text-xs font-semibold text-slate-400">{label}</span><span className="block truncate font-medium text-slate-700">{value}</span></span></div>
}

function useRoutePoints(result: TripPlanResponse) {
  return useMemo(() => {
    const coordinates = result.route?.geometry?.coordinates ?? []
    if (!coordinates.length) return ''
    const xs = coordinates.map(([longitude]) => longitude)
    const ys = coordinates.map(([, latitude]) => latitude)
    const minX = Math.min(...xs)
    const maxX = Math.max(...xs)
    const minY = Math.min(...ys)
    const maxY = Math.max(...ys)
    return coordinates.map(([longitude, latitude]) => {
      const x = ((longitude - minX) / (maxX - minX || 1)) * 100
      const y = 100 - ((latitude - minY) / (maxY - minY || 1)) * 100
      return `${x},${y}`
    }).join(' ')
  }, [result])
}
