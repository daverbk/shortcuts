from update.update import Budget, Meeting, ToDo, Habit, Weather, Birthday, Headline


def main():
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


if __name__ == "__main__":
    main()
