"""Browser version of the roadmap planner. Run with: python3 app.py"""
import html
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

from agent import Profile, RoadmapAgent
from skills import SKILLS, GOALS

CSS = """
body {
    font-family: -apple-system, Segoe UI, Arial, sans-serif;
    background: #f4f6fb;
    margin: 0;
    color: #222;
}
.wrap {
    max-width: 860px;
    margin: 30px auto;
    padding: 0 16px;
}
.card {
    background: #fff;
    border-radius: 12px;
    padding: 22px;
    box-shadow: 0 2px 8px #0001;
    margin-bottom: 20px;
}
h1 { margin: 0 0 4px; }
label {
    display: block;
    font-weight: 600;
    margin: 14px 0 4px;
}
select, input[type=number] {
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 6px;
    width: 220px;
}
.skills {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 4px 16px;
}
.skills label { font-weight: 400; margin: 2px 0; }
button {
    background: #4f46e5;
    color: #fff;
    border: 0;
    padding: 11px 22px;
    border-radius: 8px;
    font-size: 15px;
    margin-top: 18px;
    cursor: pointer;
}
table { width: 100%; border-collapse: collapse; }
th, td {
    text-align: left;
    padding: 8px;
    border-bottom: 1px solid #eee;
    font-size: 14px;
}
th { background: #f0f0fa; }
.extra { color: #888; }
.warn {
    background: #fff3cd;
    padding: 10px;
    border-radius: 8px;
    margin-top: 10px;
}
.muted { color: #666; font-size: 14px; }
"""


def page(body):
    """Put page content inside the shared HTML layout."""
    return f"""<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>Roadmap Recommender</title>
    <style>{CSS}</style>
</head>
<body>
    <div class="wrap">{body}</div>
</body>
</html>"""


def form_html():
    """Create the form where the learner enters their details."""
    goal_options = ""
    for goal in GOALS:
        goal_options += f"<option>{html.escape(goal)}</option>"

    skill_options = ""
    for skill_id, skill in SKILLS.items():
        skill_name = html.escape(skill["name"])
        skill_options += (
            f"<label><input type='checkbox' name='known' value='{skill_id}'> "
            f"{skill_name}</label>"
        )

    return page(f"""
<div class="card">
    <h1>AI Coding Roadmap Recommender</h1>
    <p class="muted">Tell the agent your goal, skills and time. It plans a valid learning path.</p>
    <form method="post" action="/plan">
        <label>Goal</label>
        <select name="goal">{goal_options}</select>
        <label>Experience</label>
        <select name="experience">
            <option>beginner</option>
            <option>intermediate</option>
            <option>advanced</option>
        </select>
        <label>Hours per day</label>
        <input type="number" step="0.25" min="0.25" max="16" name="hours" value="2">
        <label>Study days per week</label>
        <input type="number" min="1" max="7" name="days" value="5">
        <label>Deadline in weeks (optional)</label>
        <input type="number" min="1" name="deadline">
        <label>Skills you already know</label>
        <div class="skills">{skill_options}</div>
        <button type="submit">Generate roadmap</button>
    </form>
</div>""")


def result_html(form):
    """Build the results page from the submitted form."""
    try:
        goal = form["goal"][0]
        known_skills = set(form.get("known", []))
        known_skills = {
            skill_id for skill_id in known_skills if skill_id in SKILLS
        }
        deadline = form.get("deadline", [""])[0].strip()
        profile = Profile(
            goal,
            known_skills,
            float(form["hours"][0]),
            form["experience"][0],
            int(form["days"][0]),
            float(deadline) if deadline else None,
        )
        result = RoadmapAgent(profile).make_plan()
    except (ValueError, KeyError) as error:
        message = html.escape(str(error))
        return page(
            "<div class='card'><h1>Invalid input</h1>"
            f"<p>{message}</p><a href='/'>Back</a></div>"
        )

    rows = ""
    for step in result.steps:
        if step.start_week == step.end_week:
            weeks = step.start_week
        else:
            weeks = f"{step.start_week}-{step.end_week}"

        if step.optional:
            extra_tag = " <span class='extra'>(extra)</span>"
        else:
            extra_tag = ""

        rows += (
            f"<tr><td>{step.number}</td>"
            f"<td>{html.escape(step.name)}{extra_tag}</td>"
            f"<td>{step.hours}</td><td>{weeks}</td>"
            f"<td>{html.escape(step.reason)}</td></tr>"
        )

    notes = ""
    for note in result.notes:
        notes += f"<div class='warn'>{html.escape(note)}</div>"

    if result.skipped_known:
        known_names = html.escape(", ".join(result.skipped_known))
        skipped = f"<p class='muted'>Skipped (already known): {known_names}</p>"
    else:
        skipped = ""

    trace = ""
    for message in result.trace:
        trace += f"<li>{html.escape(message)}</li>"

    if rows:
        table = (
            "<table><tr><th>#</th><th>Skill</th><th>Hours</th>"
            f"<th>Week</th><th>Why</th></tr>{rows}</table>"
        )
    else:
        table = "<p>You already know everything needed.</p>"

    return page(f"""
<div class="card">
    <h1>Roadmap: {html.escape(goal)}</h1>
    {skipped}
    {table}
    <p><b>Total:</b> {result.total_hours} hours, about {result.total_weeks:.1f} weeks
    ({result.total_weeks / 4.3:.1f} months)</p>
    {notes}
</div>
<div class="card">
    <h3>How the agent reasoned</h3>
    <ul>{trace}</ul>
    <a href="/">Plan another roadmap</a>
</div>""")


class Handler(BaseHTTPRequestHandler):
    def _send(self, content, code=200):
        """Send an HTML response to the browser."""
        data = content.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        """Show the input form."""
        self._send(form_html())

    def do_POST(self):
        """Read the submitted form and show a roadmap."""
        length = int(self.headers.get("Content-Length", 0))
        form = parse_qs(self.rfile.read(length).decode("utf-8"))
        self._send(result_html(form))

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Server running on port {port}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped.")
    finally:
        server.server_close()
