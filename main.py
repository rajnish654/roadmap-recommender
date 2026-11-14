"""Command-line version of the roadmap planner. Run with: python3 main.py"""
from agent import Profile, RoadmapAgent
from skills import SKILLS, GOALS


def ask_choice(title, options):
    """Ask the user to choose one option from a numbered list."""
    print(f"\n{title}")
    for number, option in enumerate(options, 1):
        print(f"  {number}. {option}")

    while True:
        answer = input("Enter number: ").strip()
        if answer.isdigit():
            choice = int(answer)
            if 1 <= choice <= len(options):
                return options[choice - 1]
        print("  Invalid choice, try again.")


def ask_number(prompt, minimum, maximum=None, optional=False):
    """Ask for a number in the allowed range."""
    while True:
        answer = input(prompt).strip()
        if optional and answer == "":
            return None

        try:
            number = float(answer)
            is_large_enough = number >= minimum
            is_small_enough = maximum is None or number <= maximum
            if is_large_enough and is_small_enough:
                return number
        except ValueError:
            pass

        print("  Please enter a valid number.")


def ask_known():
    """Let the user choose skills they already know."""
    skill_ids = list(SKILLS)
    print("\nSkills you ALREADY know:")
    for number, skill_id in enumerate(skill_ids, 1):
        print(f"  {number:>2}. {SKILLS[skill_id]['name']}")

    answer = input("Enter numbers separated by commas (Enter = none): ")
    known = set()
    for part in answer.split(","):
        part = part.strip()
        if part.isdigit():
            choice = int(part)
            if 1 <= choice <= len(skill_ids):
                known.add(skill_ids[choice - 1])

    return known


def print_result(goal, res, show_trace):
    """Print the roadmap and, optionally, the planner's reasoning."""
    print(f"\n=== Your roadmap: {goal} ===")
    if res.skipped_known:
        print("Skipping (you already know): " + ", ".join(res.skipped_known))

    if not res.steps:
        print("You already have every skill needed. Build projects and apply for jobs!")
        return

    print(f"\n{'#':<3}{'Skill':<34}{'Hours':>6}  {'Weeks':<9}Why")
    print("-" * 95)
    for step in res.steps:
        if step.start_week == step.end_week:
            weeks = str(step.start_week)
        else:
            weeks = f"{step.start_week}-{step.end_week}"

        extra_tag = " (extra)" if step.optional else ""
        skill_name = step.name + extra_tag
        print(
            f"{step.number:<3}{skill_name:<34}{step.hours:>6}  "
            f"{weeks:<9}{step.reason}"
        )

    print("-" * 95)
    print(f"Total: {res.total_hours} hours, about {res.total_weeks:.1f} weeks ({res.total_weeks / 4.3:.1f} months)")
    for note in res.notes:
        print("NOTE:", note)

    if show_trace:
        print("\n--- How the agent reasoned ---")
        for message in res.trace:
            print(" *", message)


def save_markdown(goal, res, path="my_roadmap.md"):
    """Save the roadmap as a Markdown file."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Roadmap: {goal}\n\n| # | Skill | Hours | Weeks | Why |\n|---|---|---|---|---|\n")
        for step in res.steps:
            f.write(
                f"| {step.number} | {step.name} | {step.hours} | "
                f"{step.start_week}-{step.end_week} | {step.reason} |\n"
            )
        f.write(f"\n**Total:** {res.total_hours} hours (~{res.total_weeks:.1f} weeks)\n")
    print(f"Saved to {path}")


def main():
    """Collect the learner's details and create a roadmap."""
    print("=== AI Coding Roadmap Recommender ===")
    goal = ask_choice("Choose your goal:", list(GOALS))
    experience = ask_choice("Your experience level:", ["beginner", "intermediate", "advanced"])
    known = ask_known()
    hours = ask_number("\nHours you can study per day: ", 0.25, 16)
    days = int(ask_number("Study days per week (1-7): ", 1, 7))
    deadline = ask_number("Deadline in weeks (Enter to skip): ", 1, optional=True)

    profile = Profile(goal, known, hours, experience, days, deadline)
    roadmap_agent = RoadmapAgent(profile)
    result = roadmap_agent.make_plan()
    print_result(goal, result, show_trace=True)

    if result.steps and input("\nSave roadmap to my_roadmap.md? (y/n): ").strip().lower() == "y":
        save_markdown(goal, result)


if __name__ == "__main__":
    main()
