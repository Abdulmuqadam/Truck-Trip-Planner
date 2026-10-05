import { RouteMap } from './RouteMap'
import type { TripPlanResponse } from '../types/trip'

type TripSummaryProps = {
  result: TripPlanResponse
}

export function TripSummary({ result }: TripSummaryProps) {
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
        <RouteMap geometry={result.route?.geometry} locations={locations} />
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
