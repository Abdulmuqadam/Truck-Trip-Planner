import type { TripFormValues, TripPlanRequest, TripPlanResponse } from '../types/trip'

const apiUrl = `${import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1'}/trips/plan/`

export class TripPlannerApiError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'TripPlannerApiError'
  }
}

export async function planTrip(form: TripFormValues): Promise<TripPlanResponse> {
  const payload: TripPlanRequest = {
    ...form,
    departure_at: new Date(form.departure_at).toISOString(),
    current_cycle_used: Number(form.current_cycle_used),
  }

  const response = await fetch(apiUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  const data = await response.json().catch(() => null)

  if (!response.ok) {
    const message = data && typeof data === 'object' && 'detail' in data
      ? String(data.detail)
      : data && typeof data === 'object' && 'code' in data
        ? String(data.code)
        : 'Unable to plan this trip.'
    throw new TripPlannerApiError(message)
  }

  return data as TripPlanResponse
}
