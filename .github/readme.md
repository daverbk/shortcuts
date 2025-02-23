# Shortcuts

[![CI](https://github.com/daverbk/shortcuts/actions/workflows/dashboard_update.yml/badge.svg)](https://github.com/daverbk/shortcuts/actions/workflows/dashboard_update.yml)
[![CI](https://github.com/daverbk/shortcuts/actions/workflows/test.yml/badge.svg)](https://github.com/daverbk/shortcuts/actions/workflows/test.yml)
[![Coverage Status](https://coveralls.io/repos/github/daverbk/shortcuts/badge.svg?branch=main)](https://coveralls.io/github/daverbk/shortcuts?branch=main)

This repo is just about playing with Apple shortcuts. I've created a couple to update & open a so-called "daily dashboard" every
morning. Here's its high-level diagram 🧜‍ 

```mermaid
sequenceDiagram
  box white shorcut 1
  participant Shortcut1 as Update Dashboard Shortcut
  participant CalendarApp as Calendar App
  participant RemindersApp as Reminders App
  participant WeatherApp as Weather App
  end
  
  participant GitHubActions as GitHub Actions
  
  box grey python script 
  participant PythonScript as Python Script
  participant RSSFeeds as RSS Feeds
  participant CurrencyAPIs as Currency APIs
  participant NotionAPI as Notion API 
  end
  
  box white shorcut 2
  participant Shortcut2 as Open Dashboard Shortcut
  actor Dave
  end
  
  Shortcut1 ->> CalendarApp: 
  activate CalendarApp
  CalendarApp -->> Shortcut1: Upcoming birthdays and meetings
  deactivate CalendarApp
  Shortcut1 ->> RemindersApp: 
  activate RemindersApp
  RemindersApp -->> Shortcut1: Regular uncompleted tasks 
  deactivate RemindersApp
  Shortcut1 ->> WeatherApp: 
  activate WeatherApp
  WeatherApp -->> Shortcut1: Weather forcast
  deactivate WeatherApp
  
  Shortcut1 ->> GitHubActions: Trigger workflow
  activate GitHubActions
  
  GitHubActions ->> PythonScript: 
  activate PythonScript
  PythonScript ->> RSSFeeds: 
  activate RSSFeeds
  RSSFeeds -->> PythonScript: Some latest news
  deactivate RSSFeeds
  PythonScript ->> CurrencyAPIs: 
  activate CurrencyAPIs
  CurrencyAPIs -->> PythonScript: Actual exchange rates
  deactivate CurrencyAPIs
  PythonScript ->> NotionAPI: Update budget, todos, habits, weather, birthdays, meetings, headlines panels
  deactivate PythonScript
  PythonScript --x GitHubActions: 
  deactivate GitHubActions
  
  Shortcut2->>Dave: Open dashboard at wakeup
```

Here is a couple of others I found useful myself

* [Toggle VPN](/exports/toggle-vpn.shortcut) is used in pair with an extra focus mode (activated when some apps are
  opened) and an automation based on the focus mode. It toggles Tunnel Bear automatically when an app used with a VPN is
  opened or closed. It requires an additional [app](https://apps.apple.com/by/app/actions/id1586435171) for extra
  actions.
* [Block Doomscrolling](/exports/block-doomscrolling.shortcut) is technically used in a similar way as the previous. It
  exits an app when it is being use for longer than 3 minutes. Found it really useful in pair with Screen Time.
