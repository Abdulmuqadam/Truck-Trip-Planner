from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, time, timedelta


class HOSPlanningError(Exception):
    """Raised when a route cannot be scheduled under the configured HOS rules."""


@dataclass
class DutyEvent:
    start: datetime
    end: datetime
    status: str
    activity: str
    miles: float = 0.0

    def as_dict(self):
        return {
            'start': self.start.isoformat(),
            'end': self.end.isoformat(),
            'status': self.status,
            'activity': self.activity,
            'duration_minutes': round((self.end - self.start).total_seconds() / 60),
            'miles': round(self.miles, 1),
        }


@dataclass
class PlannerState:
    current_time: datetime
    cycle_used: float
    shift_elapsed_hours: float = 0.0
    shift_driving_hours: float = 0.0
    driving_since_break_hours: float = 0.0
    miles_since_fuel: float = 0.0


class HOSPlanner:
    MAX_DRIVING_HOURS = 11.0
    MAX_WINDOW_HOURS = 14.0
    BREAK_AFTER_DRIVING_HOURS = 8.0
    BREAK_DURATION_HOURS = 0.5
    DAILY_REST_HOURS = 10.0
    RESTART_HOURS = 34.0
    MAX_CYCLE_HOURS = 70.0
    FUEL_INTERVAL_MILES = 1000.0
    FUEL_DURATION_HOURS = 0.5
    PICKUP_DURATION_HOURS = 1.0
    DROPOFF_DURATION_HOURS = 1.0
    EPSILON = 0.000001

    def plan(self, trip, route):
        legs = route.get('legs', [])
        if len(legs) != 2:
            raise HOSPlanningError('A route with current, pickup, and drop-off legs is required.')

        start = trip['departure_at']
        if start.tzinfo is None:
            raise HOSPlanningError('Departure time must include a timezone.')

        state = PlannerState(
            current_time=start,
            cycle_used=float(trip['current_cycle_used']),
        )
        events = []

        self._drive_leg(state, events, legs[0])
        self._add_on_duty_event(
            state,
            events,
            self.PICKUP_DURATION_HOURS,
            'pickup',
        )
        self._drive_leg(state, events, legs[1])
        self._add_on_duty_event(
            state,
            events,
            self.DROPOFF_DURATION_HOURS,
            'dropoff',
        )

        return self._build_result(events, state, route)

    def _drive_leg(self, state, events, leg):
        remaining_hours = float(leg['duration_hours'])
        remaining_miles = float(leg['distance_miles'])
        if remaining_hours <= self.EPSILON:
            return

        speed = remaining_miles / remaining_hours
        while remaining_hours > self.EPSILON:
            self._prepare_for_driving(state, events)
            available_hours = min(
                self.MAX_DRIVING_HOURS - state.shift_driving_hours,
                self.BREAK_AFTER_DRIVING_HOURS - state.driving_since_break_hours,
                self.MAX_WINDOW_HOURS - state.shift_elapsed_hours,
                self.MAX_CYCLE_HOURS - state.cycle_used,
            )
            if available_hours <= self.EPSILON:
                continue

            drive_hours = min(remaining_hours, available_hours)
            fuel_limit_miles = self.FUEL_INTERVAL_MILES - state.miles_since_fuel
            if speed > self.EPSILON:
                drive_hours = min(drive_hours, fuel_limit_miles / speed)

            if drive_hours <= self.EPSILON:
                self._add_on_duty_event(
                    state,
                    events,
                    self.FUEL_DURATION_HOURS,
                    'fuel',
                )
                state.miles_since_fuel = 0.0
                continue

            miles = speed * drive_hours
            self._add_event(
                state,
                events,
                drive_hours,
                'driving',
                'driving',
                miles,
            )
            state.shift_driving_hours += drive_hours
            state.driving_since_break_hours += drive_hours
            state.cycle_used += drive_hours
            state.miles_since_fuel += miles
            remaining_hours -= drive_hours
            remaining_miles -= miles

    def _prepare_for_driving(self, state, events):
        if state.cycle_used >= self.MAX_CYCLE_HOURS - self.EPSILON:
            self._add_off_duty_event(state, events, self.RESTART_HOURS, '34_hour_restart')
            state.cycle_used = 0.0
            return

        if state.driving_since_break_hours >= self.BREAK_AFTER_DRIVING_HOURS - self.EPSILON:
            self._add_off_duty_event(state, events, self.BREAK_DURATION_HOURS, '30_minute_break')
            state.driving_since_break_hours = 0.0
            return

        if (
            state.shift_driving_hours >= self.MAX_DRIVING_HOURS - self.EPSILON
            or state.shift_elapsed_hours >= self.MAX_WINDOW_HOURS - self.EPSILON
        ):
            self._add_off_duty_event(state, events, self.DAILY_REST_HOURS, 'daily_rest')
            state.shift_elapsed_hours = 0.0
            state.shift_driving_hours = 0.0
            state.driving_since_break_hours = 0.0

    def _add_on_duty_event(self, state, events, duration_hours, activity):
        self._prepare_for_on_duty(state, events, duration_hours)
        self._add_event(
            state,
            events,
            duration_hours,
            'on_duty_not_driving',
            activity,
        )
        state.cycle_used += duration_hours

    def _prepare_for_on_duty(self, state, events, duration_hours):
        if state.cycle_used + duration_hours > self.MAX_CYCLE_HOURS + self.EPSILON:
            self._add_off_duty_event(state, events, self.RESTART_HOURS, '34_hour_restart')
            state.cycle_used = 0.0

        if state.shift_elapsed_hours + duration_hours > self.MAX_WINDOW_HOURS + self.EPSILON:
            self._add_off_duty_event(state, events, self.DAILY_REST_HOURS, 'daily_rest')
            state.shift_elapsed_hours = 0.0
            state.shift_driving_hours = 0.0
            state.driving_since_break_hours = 0.0

    def _add_off_duty_event(self, state, events, duration_hours, activity):
        self._add_event(state, events, duration_hours, 'off_duty', activity)

    def _add_event(self, state, events, duration_hours, status, activity, miles=0.0):
        end_time = state.current_time + timedelta(hours=duration_hours)
        events.append(DutyEvent(state.current_time, end_time, status, activity, miles))
        state.current_time = end_time
        if activity not in ('daily_rest', '34_hour_restart'):
            state.shift_elapsed_hours += duration_hours

    def _build_result(self, events, state, route):
        daily_logs = defaultdict(list)
        for event in events:
            self._split_event_by_day(event, daily_logs)

        status_hours = defaultdict(float)
        for event in events:
            status_hours[event.status] += (event.end - event.start).total_seconds() / 3600

        return {
            'summary': {
                'total_miles': round(sum(event.miles for event in events), 1),
                'total_hours': round(
                    (events[-1].end - events[0].start).total_seconds() / 3600, 1
                ),
                'cycle_hours_used': round(state.cycle_used, 1),
                'hours_by_status': {
                    status: round(hours, 2) for status, hours in status_hours.items()
                },
            },
            'events': [event.as_dict() for event in events],
            'daily_logs': [
                {'date': date, 'events': day_events}
                for date, day_events in sorted(daily_logs.items())
            ],
            'route_distance_miles': route.get('distance_miles'),
        }

    @staticmethod
    def _split_event_by_day(event, daily_logs):
        current = event.start
        total_seconds = (event.end - event.start).total_seconds()
        while current < event.end:
            next_day = datetime.combine(
                current.date() + timedelta(days=1),
                time.min,
                tzinfo=current.tzinfo,
            )
            end = min(event.end, next_day)
            seconds = (end - current).total_seconds()
            miles = event.miles * seconds / total_seconds if total_seconds else 0.0
            daily_logs[current.date().isoformat()].append({
                'start': current.isoformat(),
                'end': end.isoformat(),
                'status': event.status,
                'activity': event.activity,
                'duration_minutes': round(seconds / 60),
                'miles': round(miles, 1),
            })
            current = end