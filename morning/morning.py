from update import Budget, Meeting, ToDo, Habit, Weather, Birthday, Headline

updates = [
    Budget(),
    Meeting(),
    ToDo(),
    Habit(),
    Weather(),
    Birthday(),
    Headline()
]

for update in updates:
    update.run()
