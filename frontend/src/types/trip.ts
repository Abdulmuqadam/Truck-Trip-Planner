export type TripFormValues = {
  current_location: string
  pickup_location: string
  dropoff_location: string
  departure_at: string
  current_cycle_used: string
}

export type TripPlanRequest = Omit<TripFormValues, 'current_cycle_used'> & {
  current_cycle_used: number
}

export type RouteGeometry = {
  coordinates?: Array<[number, number]>
  type?: string
}

export type Location = {
  display_name?: string
  latitude?: number
  longitude?: number
}

export type RouteStep = {
  instruction: string
  distance_miles: number
  duration_minutes: number
}

export type TripRoute = {
  distance_miles?: number
  duration_hours?: number
  duration_minutes?: number
  geometry?: RouteGeometry
  steps?: RouteStep[]
}

export type LogEvent = {
  start: string
  end: string
  status: string
  activity: string
  duration_minutes: number
  miles: number
}

export type DailyLog = {
  date: string
  events: LogEvent[]
}

export type HosSummary = {
  total_miles?: number
  total_hours?: number
  cycle_hours_used?: number
  hours_by_status?: Record<string, number>
}

export type TripPlanResponse = {
  status: string
  trip: TripFormValues & { departure_at: string }
  locations?: Record<string, Location>
  route?: TripRoute
  hos?: {
    summary?: HosSummary
    events?: Array<Record<string, unknown>>
    daily_logs?: DailyLog[]
  }
}
