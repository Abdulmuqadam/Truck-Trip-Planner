import type { DailyLog, LogEvent } from '../types/trip'

type DailyLogsProps = {
  logs: DailyLog[]
}

export function DailyLogs({ logs }: DailyLogsProps) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
      <div className="mb-5 flex items-center justify-between gap-3">
        <div><p className="mb-1 text-xs font-bold uppercase tracking-[0.16em] text-emerald-600">Compliance</p><h2 className="text-xl font-bold text-slate-900">ELD logs</h2></div>
        <button type="button" className="rounded-lg border border-slate-200 px-3 py-2 text-xs font-bold text-slate-600 transition hover:border-emerald-300 hover:text-emerald-700" onClick={() => window.print()}>Print logs</button>
      </div>
      {logs.length ? logs.map((log) => <LogSheet key={log.date} log={log} />) : <div className="empty-state">No daily logs generated yet.</div>}
    </section>
  )
}

function LogSheet({ log }: { log: DailyLog }) {
  return (
    <article className="mb-4 overflow-hidden rounded-xl border border-slate-200 last:mb-0">
      <div className="flex flex-col justify-between gap-3 border-b border-slate-200 bg-slate-50 px-4 py-4 sm:flex-row sm:items-center">
        <div><p className="text-xs font-bold uppercase tracking-wider text-emerald-600">Daily log</p><h3 className="mt-1 text-base font-bold text-slate-900">{log.date}</h3></div>
        <div className="text-xs text-slate-500 sm:text-right"><span className="block">Driver: <strong className="text-slate-700">John Doe</strong></span><span className="block">Carrier: <strong className="text-slate-700">Transport Ai</strong></span></div>
      </div>
      <div className="overflow-x-auto"><table className="w-full min-w-[620px] text-left text-sm">
        <thead className="bg-white text-[11px] uppercase tracking-wider text-slate-400"><tr><th className="px-4 py-3 font-bold">Start</th><th className="px-4 py-3 font-bold">End</th><th className="px-4 py-3 font-bold">Status</th><th className="px-4 py-3 font-bold">Activity</th><th className="px-4 py-3 font-bold">Minutes</th><th className="px-4 py-3 font-bold">Miles</th></tr></thead>
        <tbody className="divide-y divide-slate-100">{log.events.map((event, index) => <LogRow key={`${log.date}-${index}`} event={event} />)}</tbody>
      </table>
      </div>
    </article>
  )
}

function LogRow({ event }: { event: LogEvent }) {
  return <tr className="text-slate-600 transition hover:bg-emerald-50/40"><td className="whitespace-nowrap px-4 py-3">{formatTime(event.start)}</td><td className="whitespace-nowrap px-4 py-3">{formatTime(event.end)}</td><td className="px-4 py-3 font-medium text-slate-800">{formatStatus(event.status)}</td><td className="px-4 py-3">{event.activity}</td><td className="px-4 py-3">{event.duration_minutes}</td><td className="px-4 py-3">{event.miles}</td></tr>
}

function formatStatus(status: string) {
  return status.split('_').map((part) => part.charAt(0).toUpperCase() + part.slice(1)).join(' ')
}

function formatTime(value: string) {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString([], { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })
}
