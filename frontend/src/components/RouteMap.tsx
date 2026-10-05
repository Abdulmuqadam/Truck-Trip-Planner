import { useEffect, useMemo } from 'react'
import { divIcon, latLngBounds, type LatLngExpression } from 'leaflet'
import { MapContainer, Marker, Polyline, Popup, TileLayer, useMap } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import type { Location, RouteGeometry } from '../types/trip'

type RouteMapProps = {
  geometry?: RouteGeometry
  locations?: Record<string, Location>
}

type Stop = {
  key: string
  label: string
  location?: Location
  color: string
}

const defaultCenter: LatLngExpression = [39.8283, -98.5795]

export function RouteMap({ geometry, locations }: RouteMapProps) {
  const route = useMemo(() => toLeafletCoordinates(geometry?.coordinates), [geometry])
  const stops = useMemo(() => [
    { key: 'current', label: 'Current location', location: locations?.current, color: '#64748b' },
    { key: 'pickup', label: 'Pickup', location: locations?.pickup, color: '#f59e0b' },
    { key: 'dropoff', label: 'Dropoff', location: locations?.dropoff, color: '#059669' },
  ].filter((stop): stop is Stop & { location: Location } => stop.location?.latitude != null && stop.location.longitude != null), [locations])
  const markerPositions = stops.map(({ location }) => [location.latitude!, location.longitude!] as LatLngExpression)
  const center = route[0] ?? markerPositions[0] ?? defaultCenter
  const bounds = route.length > 0 ? route : markerPositions

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-slate-100">
      <MapContainer className="h-[360px] w-full sm:h-[440px]" center={center} zoom={5} scrollWheelZoom>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {route.length > 1 ? <Polyline positions={route} pathOptions={{ color: '#059669', weight: 5, opacity: 0.85 }} /> : null}
        {stops.map(({ key, label, location, color }) => {
          const position: LatLngExpression = [location.latitude!, location.longitude!]
          return (
            <Marker key={key} position={position} icon={createStopIcon(color)}>
              <Popup>
                <strong>{label}</strong>
                <br />
                {location.display_name ?? 'Location'}
              </Popup>
            </Marker>
          )
        })}
        {bounds.length > 1 ? <FitBounds positions={bounds} /> : null}
      </MapContainer>
      {!route.length && !stops.length ? (
        <p className="px-4 py-3 text-sm text-slate-500">Map coordinates are unavailable for this route.</p>
      ) : null}
    </div>
  )
}

function FitBounds({ positions }: { positions: LatLngExpression[] }) {
  const map = useMap()

  useEffect(() => {
    map.fitBounds(latLngBounds(positions), { padding: [32, 32] })
  }, [map, positions])

  return null
}

function toLeafletCoordinates(coordinates?: Array<[number, number]>): LatLngExpression[] {
  return coordinates?.map(([longitude, latitude]) => [latitude, longitude]) ?? []
}

function createStopIcon(color: string) {
  return divIcon({
    className: 'route-stop-marker',
    html: `<span style="background-color: ${color}"></span>`,
    iconSize: [18, 18],
    iconAnchor: [9, 9],
  })
}
