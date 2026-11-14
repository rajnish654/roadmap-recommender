# AI Coding Roadmap Recommender

This program makes a coding study plan based on a learner's career goal,
current skills, experience, and available study time.

## Run the program

Open a terminal in this folder and choose one of these commands:

```bash
python3 main.py
```

This runs the terminal version. It asks questions and prints the roadmap.

```bash
python3 app.py
```

This starts the web version at http://127.0.0.1:8000.

To run the tests:

```bash
python3 -m unittest discover -s tests -v
```

No extra packages are needed. The project uses Python's built-in modules.

## Project files

| File | What it does |
|---|---|
| `skills.py` | Stores the skills, prerequisites, goals, and estimated study hours. |
| `agent.py` | Finds missing skills, orders them, and estimates a schedule. |
| `main.py` | Asks questions and displays a roadmap in the terminal. |
| `app.py` | Shows a form and roadmap in a web browser. |
| `tests/test_agent.py` | Checks that the roadmap planner works as expected. |

## How a roadmap is made

```mermaid
flowchart TD
    A([Start]) --> B[Enter goal, known skills, experience,<br/>and study time]
    B --> C[Add prerequisites of known skills]
    C --> D[Find missing skills for the goal]
    D --> E{Deadline entered?}
    E -- No --> H
    E -- Yes --> F{Do required skills fit?}
    F -- No --> G[Show a deadline warning]
    G --> H
    F -- Yes --> I[Add optional skills if there is time]
    I --> H[Order skills after their prerequisites]
    H --> J[Estimate hours and weeks]
    J --> K[Show the roadmap]
    K --> L([End])
```
