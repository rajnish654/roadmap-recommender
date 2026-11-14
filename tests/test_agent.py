import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import (
    Profile,
    RoadmapAgent,
    expand_known,
    order_skills,
    required_skills,
    validate_plan,
)
from skills import SKILLS, GOALS


class TestAgent(unittest.TestCase):
    def test_graph_has_no_cycle(self):
        # A cycle makes order_skills raise ValueError.
        order_skills(set(SKILLS))

    def test_prerequisites_always_first(self):
        for goal in GOALS:
            result = RoadmapAgent(Profile(goal)).make_plan()
            skill_ids = [step.skill_id for step in result.steps]
            self.assertEqual(validate_plan(skill_ids, set()), [])

    def test_known_skills_are_skipped(self):
        profile = Profile("Full-Stack Developer", {"python", "html"})
        result = RoadmapAgent(profile).make_plan()
        skill_ids = [step.skill_id for step in result.steps]
        self.assertNotIn("html", skill_ids)
        self.assertNotIn("python", skill_ids)

    def test_inference(self):
        self.assertIn("javascript", expand_known({"react"}))

    def test_deadline_infeasible(self):
        profile = Profile("Full-Stack Developer", deadline_weeks=4)
        result = RoadmapAgent(profile).make_plan()
        self.assertFalse(result.feasible)

    def test_deadline_adds_optional(self):
        profile = Profile(
            "Frontend Developer",
            hours_per_day=4,
            days_per_week=7,
            deadline_weeks=40,
        )
        result = RoadmapAgent(profile).make_plan()
        self.assertTrue(result.feasible)
        self.assertTrue(any(step.optional for step in result.steps))

    def test_fully_skilled_student(self):
        everything = required_skills(GOALS["Frontend Developer"]["required"], set())
        result = RoadmapAgent(Profile("Frontend Developer", everything)).make_plan()
        self.assertEqual(result.steps, [])

    def test_experience_changes_time(self):
        beginner = RoadmapAgent(
            Profile("Frontend Developer", experience="beginner")
        ).make_plan()
        advanced = RoadmapAgent(
            Profile("Frontend Developer", experience="advanced")
        ).make_plan()
        self.assertGreater(beginner.total_hours, advanced.total_hours)

    def test_bad_input(self):
        with self.assertRaises(ValueError):
            RoadmapAgent(Profile("Full-Stack Developer", hours_per_day=0))


if __name__ == "__main__":
    unittest.main()
