import json
import os
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from service.currency_service import CurrencyRatioResolver
from update.helper import rich_text_update, format_time
from update.update import Meeting, ToDo, Budget, Habit, Birthday, Weather, main


@pytest.fixture
def mock_notion_client():
    mock_client = MagicMock()
    return mock_client


@pytest.fixture
def mock_updates():
    with patch('update.update.Budget') as MockBudget, \
            patch('update.update.Meeting') as MockMeeting, \
            patch('update.update.ToDo') as MockToDo, \
            patch('update.update.Habit') as MockHabit, \
            patch('update.update.Weather') as MockWeather, \
            patch('update.update.Birthday') as MockBirthday, \
            patch('update.update.Headline') as MockHeadline:
        MockBudget.return_value.run = MagicMock()
        MockMeeting.return_value.run = MagicMock()
        MockToDo.return_value.run = MagicMock()
        MockHabit.return_value.run = MagicMock()
        MockWeather.return_value.run = MagicMock()
        MockBirthday.return_value.run = MagicMock()
        MockHeadline.return_value.run = MagicMock()

        yield {
            'Budget': MockBudget,
            'Meeting': MockMeeting,
            'ToDo': MockToDo,
            'Habit': MockHabit,
            'Weather': MockWeather,
            'Birthday': MockBirthday,
            'Headline': MockHeadline
        }


def test_meeting_run(mock_notion_client):
    mock_notion_client.blocks.update.return_value = None

    os.environ['MEETINGS'] = json.dumps([
        {
            'title': 'Meeting 1',
            'start_date': '2025-02-23T10:20:00+03:00',
            'end_date': '2025-02-23T11:20:00+03:00'
        },
        {
            'title': 'Meeting 2',
            'start_date': '2025-02-23T18:20:00+03:00',
            'end_date': '2025-02-23T20:00:00+03:00'
        }
    ])
    meeting_update = Meeting()
    meeting_update.client = mock_notion_client

    meeting_update.run()

    mock_notion_client.blocks.update.assert_called_once_with(
        block_id=meeting_update.meetings_block_id,
        code={'rich_text': [{'text': {'content': '\n# Meeting 1 #\n10:20 - 11:20\n\n# Meeting 2 #\n18:20 - 20:00'}}]}
    )


def test_meeting_run_with_no_meetings(mock_notion_client):
    mock_notion_client.blocks.update.return_value = None

    os.environ['MEETINGS'] = json.dumps([])
    meeting_update = Meeting()
    meeting_update.client = mock_notion_client

    meeting_update.run()

    mock_notion_client.blocks.update.assert_called_once_with(
        block_id=meeting_update.meetings_block_id,
        code={'rich_text': [{'text': {'content': '# 🤘 No meetings for today! Hooray! 🙂‍↕️ #'}}]}
    )


def test_todo_run(mock_notion_client):
    mock_notion_client.blocks.children.list.return_value = {'results': [{'id': 'mock-id'}]}
    mock_notion_client.blocks.children.append.return_value = None

    mock_to_do_data = ['Buy groceries']

    os.environ['TO_DOS'] = json.dumps(mock_to_do_data)
    todo_update = ToDo()
    todo_update.client = mock_notion_client

    todo_update.run()

    mock_notion_client.blocks.delete.assert_called_once_with(block_id='mock-id')
    mock_notion_client.blocks.children.append.assert_called_once_with(
        block_id=todo_update.to_dos_block_id,
        children=[{'object': 'block', 'type': 'to_do',
                   'to_do': {'rich_text': [{'type': 'text', 'text': {'content': 'Buy groceries'}}], 'checked': False}}]
    )


def test_budget_run(mock_notion_client):
    mock_notion_client.pages.update.return_value = None
    mock_notion_client.databases.query.return_value = {
        'results': [
            {
                'properties': {
                    'Total': {
                        'formula': {
                            'number': 1000.00
                        }
                    }
                }
            }
        ]
    }

    mock_currency_resolver = MagicMock(spec=CurrencyRatioResolver)
    mock_currency_resolver.resolve.return_value = 1.2

    budget_update = Budget()
    budget_update.client = mock_notion_client
    budget_update.currency_rate_resolver = mock_currency_resolver

    budget_update.run()

    mock_notion_client.pages.update.assert_any_call(
        page_id=budget_update.budget_page_id,
        properties={'PlnUsdRate': {'number': 1.2}}
    )
    mock_notion_client.blocks.update.assert_called_with(
        block_id=budget_update.budget_block_id,
        code={'rich_text': [{'text': {'content': '# $ 1,000.0 #'}}]}
    )


def test_habit_run(mock_notion_client):
    mock_notion_client.databases.query.return_value = {'results': [{'id': 'mock-id'}]}

    habit_update = Habit()
    habit_update.client = mock_notion_client

    habit_update.run()

    mock_notion_client.blocks.update.assert_called_once_with(
        block_id=habit_update.habits_block_id,
        callout={'rich_text': [{'mention': {'page': {'id': 'mock-id'}}}]}
    )


def test_birthday_today(mock_notion_client):
    today = datetime.today().isoformat()
    os.environ['BIRTHDAYS'] = json.dumps([{'start_date': today, 'title': 'Alice'}])

    birthday = Birthday()
    birthday.client = mock_notion_client
    birthday.run()

    expected_text = '# 🎉 Today 🎉 #\nAlice'
    mock_notion_client.blocks.update.assert_called_with(
        block_id=birthday.birthdays_block_id,
        code={'rich_text': [{'text': {'content': expected_text}}]}
    )


def test_birthday_future(mock_notion_client):
    future_date = (datetime.today().replace() + timedelta(days=5)).isoformat()
    os.environ['BIRTHDAYS'] = json.dumps([{'start_date': future_date, 'title': 'Bob'}])

    birthday = Birthday()
    birthday.client = mock_notion_client
    birthday.run()

    expected_text = '# ⏳ In 5 day(s) ⏳ #\nBob'
    mock_notion_client.blocks.update.assert_called_with(
        block_id=birthday.birthdays_block_id,
        code={'rich_text': [{'text': {'content': expected_text}}]}
    )


def test_weather_update(mock_notion_client):
    os.environ['WEATHER'] = json.dumps(
        {'max': 25, 'min': 15, 'sunrise': '2025-02-23T06:30:00+03:00', 'sunset': '2025-02-23T18:45:00+03:00'})
    weather = Weather()
    weather.client = mock_notion_client
    weather.run()

    mock_notion_client.blocks.update.assert_called_with(
        block_id='',
        table_row={
            'cells': [
                [{'text': {'content': '25'}}],
                [{'text': {'content': '15'}}],
                [{'text': {'content': '06:30'}}],
                [{'text': {'content': '18:45'}}]
            ]
        }
    )


def test_main_executes_updates(mock_updates):
    main()
    for name, mock_class in mock_updates.items():
        mock_class.return_value.run.assert_called_once()


def test_get_rich_text_update():
    data = 'Hello, Notion!'
    result = rich_text_update(data)
    expected_result = {'rich_text': [{'text': {'content': data}}]}
    assert result == expected_result


def test_get_formatted_time():
    date_str = '2023-02-16T12:30:00'
    result = format_time(date_str)
    expected_result = '12:30'
    assert result == expected_result


def test_get_formatted_time_invalid_date():
    invalid_date_str = '2023-02-31T12:30:00'
    with pytest.raises(ValueError):
        format_time(invalid_date_str)
