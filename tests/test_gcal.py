"""
Tests for tools/gcal.py.
All Google API calls are mocked via the mock_calendar_service fixture.
"""

import json
import pytest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from unittest.mock import MagicMock, patch


@pytest.mark.unit
class TestListEvents:
    """Tests for the list_events function."""

    def test_list_events_returns_formatted_events(self, mock_calendar_service):
        """list_events should return a list of formatted event dicts."""
        from tools.gcal import list_events

        events = list_events(days=7)

        assert len(events) == 3
        assert events[0]['summary'] == 'Team standup'
        assert events[0]['id'] == 'evt001'
        assert 'date' in events[0]
        assert 'time' in events[0]

    def test_list_events_handles_empty_calendar(self):
        """When no events exist, list_events should return an empty list."""
        from tools.gcal import list_events

        service = MagicMock()
        list_mock = MagicMock()
        list_mock.execute.return_value = {'items': []}
        service.events().list.return_value = list_mock

        with patch('tools.gcal.get_calendar', return_value=service):
            result = list_events()

        assert result == []


@pytest.mark.unit
class TestCreateEvent:
    """Tests for the create_event function."""

    def test_create_event_with_duration(self, mock_calendar_service):
        """Creating an event with a duration (no explicit end) should work."""
        from tools.gcal import create_event

        with patch('tools.gcal.get_timezone', return_value='Europe/London'):
            event = create_event(
                summary='Quick sync',
                start='2026-03-10 10:00',
                duration=30,
            )

        assert event is not None
        mock_calendar_service.events().insert.assert_called_once()

        call_kwargs = mock_calendar_service.events().insert.call_args
        body = call_kwargs[1]['body'] if 'body' in call_kwargs[1] else call_kwargs[0][0]
        assert body['summary'] == 'Quick sync'

    def test_create_event_with_end_time(self, mock_calendar_service):
        """Creating an event with an explicit end time should work."""
        from tools.gcal import create_event

        with patch('tools.gcal.get_timezone', return_value='Europe/London'):
            event = create_event(
                summary='Workshop',
                start='2026-03-10 09:00',
                end='2026-03-10 12:00',
            )

        assert event is not None
        mock_calendar_service.events().insert.assert_called_once()

    def test_create_event_with_attendees(self, mock_calendar_service):
        """Attendees should be included in the event body."""
        from tools.gcal import create_event

        with patch('tools.gcal.get_timezone', return_value='Europe/London'):
            event = create_event(
                summary='Team call',
                start='2026-03-10 14:00',
                attendees=['alice@example.com', 'bob@example.com'],
            )

        assert event is not None
        call_kwargs = mock_calendar_service.events().insert.call_args
        body = call_kwargs[1]['body'] if 'body' in call_kwargs[1] else call_kwargs[0][0]
        assert len(body['attendees']) == 2
        assert body['attendees'][0]['email'] == 'alice@example.com'


@pytest.mark.unit
class TestCheckAvailability:
    """Tests for the check_availability function."""

    def test_check_availability_finds_free_slots(self):
        """When busy slots exist, free slots should be calculated around them."""
        from tools.gcal import check_availability

        tz = ZoneInfo('Europe/London')
        busy_start = datetime(2026, 3, 10, 10, 0, tzinfo=tz)
        busy_end = datetime(2026, 3, 10, 11, 0, tzinfo=tz)

        service = MagicMock()
        list_mock = MagicMock()
        list_mock.execute.return_value = {
            'items': [
                {
                    'start': {'dateTime': busy_start.isoformat()},
                    'end': {'dateTime': busy_end.isoformat()},
                    'summary': 'Meeting',
                }
            ]
        }
        service.events().list.return_value = list_mock

        with patch('tools.gcal.get_calendar', return_value=service), \
             patch('tools.gcal.get_timezone', return_value='Europe/London'):
            result = check_availability('2026-03-10', start_hour=9, end_hour=17)

        assert len(result['busy']) == 1
        assert len(result['free']) == 2  # 09:00-10:00 and 11:00-17:00

    def test_check_availability_no_events(self):
        """When no events exist, the entire working day should be free."""
        from tools.gcal import check_availability

        service = MagicMock()
        list_mock = MagicMock()
        list_mock.execute.return_value = {'items': []}
        service.events().list.return_value = list_mock

        with patch('tools.gcal.get_calendar', return_value=service), \
             patch('tools.gcal.get_timezone', return_value='Europe/London'):
            result = check_availability('2026-03-10', start_hour=9, end_hour=17)

        assert len(result['busy']) == 0
        assert len(result['free']) == 1
        # The single free slot should span the full working day
        slot = result['free'][0]
        assert slot['start'].hour == 9
        assert slot['end'].hour == 17


@pytest.mark.unit
class TestParseDatetime:
    """Tests for the parse_datetime helper function."""

    def test_parse_datetime_multiple_formats(self):
        """Various supported datetime formats should all parse correctly."""
        from tools.gcal import parse_datetime

        with patch('tools.gcal.get_timezone', return_value='Europe/London'):
            # YYYY-MM-DD HH:MM
            dt1 = parse_datetime('2026-03-10 14:30')
            assert dt1.hour == 14
            assert dt1.minute == 30

            # YYYY-MM-DDTHH:MM
            dt2 = parse_datetime('2026-03-10T14:30')
            assert dt2.hour == 14

            # DD/MM/YYYY HH:MM
            dt3 = parse_datetime('10/03/2026 14:30')
            assert dt3.day == 10
            assert dt3.month == 3

    def test_parse_datetime_raises_on_invalid(self):
        """An unrecognised format should raise ValueError."""
        from tools.gcal import parse_datetime

        with patch('tools.gcal.get_timezone', return_value='Europe/London'):
            with pytest.raises(ValueError, match="Could not parse"):
                parse_datetime('not-a-date')


@pytest.mark.unit
class TestFormatEvent:
    """Tests for the format_event helper function."""

    def test_format_event_timed(self):
        """A timed event should show start and end times."""
        from tools.gcal import format_event

        event = {
            'id': 'evt_t',
            'summary': 'Coffee chat',
            'start': {'dateTime': '2026-03-10T10:00:00+00:00'},
            'end': {'dateTime': '2026-03-10T10:30:00+00:00'},
            'htmlLink': 'https://calendar.google.com/event?eid=evt_t',
        }

        result = format_event(event)

        assert result['id'] == 'evt_t'
        assert result['summary'] == 'Coffee chat'
        assert result['date'] == '2026-03-10'
        assert '10:00' in result['time']
        assert '10:30' in result['time']

    def test_format_event_all_day(self):
        """An all-day event should show 'All day' for the time."""
        from tools.gcal import format_event

        event = {
            'id': 'evt_ad',
            'summary': 'Bank holiday',
            'start': {'date': '2026-03-10'},
            'end': {'date': '2026-03-11'},
            'htmlLink': 'https://calendar.google.com/event?eid=evt_ad',
        }

        result = format_event(event)

        assert result['time'] == 'All day'
        assert result['date'] == '2026-03-10'
