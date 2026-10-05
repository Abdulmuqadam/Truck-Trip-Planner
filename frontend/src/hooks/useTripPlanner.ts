import { useState } from 'react'
import { planTrip } from '../services/tripPlannerApi'
import type { TripFormValues, TripPlanResponse } from '../types/trip'

export function useTripPlanner() {
  const [result, setResult] = useState<TripPlanResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const submitTrip = async (form: TripFormValues) => {
    setLoading(true)
    setError('')

    try {
      const tripPlan = await planTrip(form)
      setResult(tripPlan)
    } catch (submitError) {
      setError(
        submitError instanceof Error
          ? submitError.message
          : 'Something went wrong while planning the trip.',
      )
    } finally {
      setLoading(false)
    }
  }

  return { result, loading, error, submitTrip }
}
