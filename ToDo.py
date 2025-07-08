import pandas as pd
import pickle
import datetime
import calendar
from sklearn.ensemble import RandomForestClassifier
from tabulate import tabulate
from collections import Counter

# ---------- Train ML Model (Run once) ----------
def train_model():
    data = {
        'estimated_time': [30, 120, 15, 60, 45],
        'days_left': [1, 5, 2, 3, 0],
        'importance': [3, 1, 2, 3, 1],
        'priority': ['High', 'Low', 'Medium', 'High', 'Low']
    }
    df = pd.DataFrame(data)
    X = df[['estimated_time', 'days_left', 'importance']]
    y = df['priority']
    model = RandomForestClassifier()
    model.fit(X, y)
    with open('task_priority_model.pkl', 'wb') as f:
        pickle.dump(model, f)

# ---------- Load ML Model ----------
def load_model():
    with open('task_priority_model.pkl', 'rb') as f:
        return pickle.load(f)

# ---------- Task Storage ----------
tasks = []
completed_tasks = []

# ---------- Add Task ----------
def add_task(model):
    title = input("Task Title: ").strip()
    description = input("Description: ").strip()

    while True:
        due_str = input("Due Date (YYYY-MM-DD): ").strip()
        try:
            due_date = datetime.datetime.strptime(due_str, "%Y-%m-%d").date()
            break
        except ValueError:
            print("❌ Please enter the proper date format (YYYY-MM-DD)")

    today = datetime.date.today()
    days_left = (due_date - today).days

    while True:
        try:
            estimated_time = int(input("Estimated time (in minutes): ").strip())
            break
        except ValueError:
            print("❌ Please enter a valid number for estimated time.")

    while True:
        importance_input = input("Importance (Low/Medium/High): ").strip().lower()
        if importance_input in ["low", "medium", "high"]:
            break
        else:
            print("❌ Please choose between: Low, Medium, High")

    importance_map = {"low": 1, "medium": 2, "high": 3}
    importance = importance_map[importance_input]

    predicted_priority = model.predict([[estimated_time, days_left, importance]])[0]

    category = input("Category (Work/Study/Fitness/etc): ").strip().capitalize()
    recurrence_input = input("Recurring? (none/daily/weekly): ").strip().lower()
    recurrence = recurrence_input if recurrence_input in ["daily", "weekly"] else "none"

    tasks.append({
        "title": title,
        "description": description,
        "due_date": due_date,
        "estimated_time": estimated_time,
        "importance": importance_input.capitalize(),
        "priority": predicted_priority,
        "category": category,
        "recurrence": recurrence
    })

    print(f"\n✅ Task '{title}' added with {predicted_priority} priority.\n")

# ---------- View All Tasks ----------
def view_tasks():
    if not tasks:
        print("No tasks added.")
        return
    df = pd.DataFrame(tasks)
    df['due_date'] = df['due_date'].astype(str)
    print(tabulate(df, headers='keys', tablefmt='grid'))

# ---------- Suggest Task ----------
def suggest_task():
    if not tasks:
        print("No tasks available to suggest.")
        return
    priority_order = {"High": 1, "Medium": 2, "Low": 3}
    sorted_tasks = sorted(tasks, key=lambda x: (priority_order[x['priority']], x['due_date']))
    task = sorted_tasks[0]
    print("\n📌 Suggested Task:")
    print(tabulate([task], headers="keys", tablefmt="grid"))

# ---------- Calendar View ----------
def calendar_view():
    if not tasks:
        print("No tasks to display in calendar.")
        return
    today = datetime.date.today()
    cal = calendar.TextCalendar()
    month = today.month
    year = today.year

    task_days = {task['due_date'].day for task in tasks if task['due_date'].month == month and task['due_date'].year == year}

    print(f"\n📅 {calendar.month_name[month]} {year} Calendar:")
    for week in cal.monthdayscalendar(year, month):
        line = ""
        for day in week:
            if day == 0:
                line += "    "
            elif day in task_days:
                line += f" *{day:2}"
            else:
                line += f"  {day:2}"
        print(line)

# ---------- Mark Task as Completed ----------
def mark_task_completed():
    if not tasks:
        print("No tasks to mark as completed.")
        return

    print("\n📝 Tasks:")
    for idx, task in enumerate(tasks, 1):
        print(f"{idx}. {task['title']} (Due: {task['due_date']})")
    try:
        choice = int(input("Enter the task number to mark as completed: "))
        if 1 <= choice <= len(tasks):
            completed_task = tasks.pop(choice - 1)
            completed_tasks.append(completed_task)
            print(f"\n✅ Task '{completed_task['title']}' marked as completed.")
        else:
            print("Invalid task number.")
    except ValueError:
        print("Please enter a valid number.")

# ---------- Productivity Insights ----------
def productivity_insights():
    if not completed_tasks:
        print("No tasks completed yet.")
        return

    day_counter = Counter([task['due_date'].strftime('%A') for task in completed_tasks])
    category_counter = Counter([task['category'] for task in completed_tasks])

    print("\n📊 Productivity Insights:")
    print(f"Total Completed Tasks: {len(completed_tasks)}")
    print(f"Most Productive Day: {day_counter.most_common(1)[0][0]}")
    print("Tasks by Category:")
    for category, count in category_counter.items():
        print(f"- {category}: {count}")

# ---------- Main App ----------
def main():
    try:
        model = load_model()
    except:
        train_model()
        model = load_model()

    while True:
        print("\n--- SMART TO-DO ---")
        print("1. Add Task")
        print("2. Show Tasks")
        print("3. Suggest Task")
        print("4. Calendar View")
        print("5. Productivity Insights")
        print("6. Mark Task as Completed")
        print("7. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_task(model)
        elif choice == "2":
            view_tasks()
        elif choice == "3":
            suggest_task()
        elif choice == "4":
            calendar_view()
        elif choice == "5":
            productivity_insights()
        elif choice == "6":
            mark_task_completed()
        elif choice == "7":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
