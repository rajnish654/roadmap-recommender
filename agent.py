"""Build a learning roadmap from a student's goal and current skills."""
import heapq
import math
from dataclasses import dataclass, field
from typing import List, Optional, Set

from skills import EXPERIENCE_FACTOR, GOALS, SKILLS, TRACK_ORDER


@dataclass
class Profile:
    """The learner's goal, current skills, and available study time."""

    goal: str
    known: Set[str] = field(default_factory=set)
    hours_per_day: float = 2.0
    experience: str = "beginner"
    days_per_week: int = 5
    deadline_weeks: Optional[float] = None


@dataclass
class Step:
    """One skill in the roadmap."""

    number: int
    skill_id: str
    name: str
    hours: int
    start_week: int
    end_week: int
    reason: str
    optional: bool = False


@dataclass
class Result:
    """The roadmap and information about how it was created."""

    steps: List[Step]
    total_hours: int
    total_weeks: float
    feasible: bool
    notes: List[str]
    trace: List[str]
    skipped_known: List[str]


def expand_known(known: Set[str]) -> Set[str]:
    """Include the prerequisites of skills the learner already knows."""
    all_known: Set[str] = set()

    def add_prerequisites(skill_id):
        if skill_id in all_known:
            return

        all_known.add(skill_id)
        for prerequisite in SKILLS[skill_id]["needs"]:
            add_prerequisites(prerequisite)

    for skill_id in known:
        add_prerequisites(skill_id)

    return all_known


def required_skills(targets: List[str], known: Set[str]) -> Set[str]:
    """Find every skill needed for the goal that the learner does not know."""
    missing: Set[str] = set()

    def find_prerequisites(skill_id):
        if skill_id in known or skill_id in missing:
            return

        missing.add(skill_id)
        for prerequisite in SKILLS[skill_id]["needs"]:
            find_prerequisites(prerequisite)

    for target in targets:
        find_prerequisites(target)

    return missing


def downstream_count(skill: str, pool: Set[str]) -> int:
    """Count how many planned skills depend on this skill."""
    dependents_seen: Set[str] = set()

    def find_dependents(skill_id):
        for other_skill in pool:
            is_prerequisite = skill_id in SKILLS[other_skill]["needs"]
            if is_prerequisite and other_skill not in dependents_seen:
                dependents_seen.add(other_skill)
                find_dependents(other_skill)

    find_dependents(skill)
    return len(dependents_seen)


def priority(skill: str, pool: Set[str]):
    """Return sorting values so related and foundational skills come first."""
    track_position = TRACK_ORDER.index(SKILLS[skill]["track"])
    dependent_count = downstream_count(skill, pool)
    learning_hours = SKILLS[skill]["hours"]

    return (track_position, -dependent_count, learning_hours, skill)


def order_skills(pool: Set[str]) -> List[str]:
    """Order skills after their prerequisites, preferring higher-priority skills.

    The priority queue stores skills whose prerequisites have already been
    handled, so a skill can never be picked before its prerequisites.
    """
    prerequisite_count = {}
    for skill_id in pool:
        count = sum(
            1 for prerequisite in SKILLS[skill_id]["needs"]
            if prerequisite in pool
        )
        prerequisite_count[skill_id] = count

    ready_skills = [
        (priority(skill_id, pool), skill_id)
        for skill_id in pool
        if prerequisite_count[skill_id] == 0
    ]
    heapq.heapify(ready_skills)

    order: List[str] = []
    while ready_skills:
        _, skill_id = heapq.heappop(ready_skills)
        order.append(skill_id)

        for other_skill in pool:
            if skill_id in SKILLS[other_skill]["needs"]:
                prerequisite_count[other_skill] -= 1
                if prerequisite_count[other_skill] == 0:
                    heapq.heappush(
                        ready_skills,
                        (priority(other_skill, pool), other_skill),
                    )

    if len(order) != len(pool):
        raise ValueError("Cycle detected in the skill graph - check skills.py")

    return order


def adjusted_hours(skill: str, experience: str) -> int:
    """Estimate study hours based on the learner's experience."""
    return max(1, round(SKILLS[skill]["hours"] * EXPERIENCE_FACTOR[experience]))


def validate_plan(order: List[str], known: Set[str]) -> List[str]:
    """Return a message for each prerequisite that appears too late."""
    violations = []
    completed = set(known)

    for skill_id in order:
        for prerequisite in SKILLS[skill_id]["needs"]:
            if prerequisite not in completed:
                skill_name = SKILLS[skill_id]["name"]
                prerequisite_name = SKILLS[prerequisite]["name"]
                violations.append(
                    f"{skill_name} comes before its prerequisite "
                    f"{prerequisite_name}"
                )
        completed.add(skill_id)

    return violations


class RoadmapAgent:
    """Plan a sequence of skills for a learner."""

    def __init__(self, profile: Profile):
        if profile.goal not in GOALS:
            raise ValueError(f"Unknown goal: {profile.goal}")
        if profile.experience not in EXPERIENCE_FACTOR:
            raise ValueError(f"Unknown experience level: {profile.experience}")
        if profile.hours_per_day <= 0 or not (1 <= profile.days_per_week <= 7):
            raise ValueError("Hours per day must be > 0 and days per week between 1 and 7")
        self.p = profile
        self.trace: List[str] = []

    def log(self, msg: str):
        """Add a message to the explanation of the plan."""
        self.trace.append(msg)

    def _total(self, pool: Set[str]) -> int:
        return sum(adjusted_hours(skill_id, self.p.experience) for skill_id in pool)

    def make_plan(self) -> Result:
        """Find the missing skills, order them, and estimate a study schedule."""
        profile = self.p
        goal = GOALS[profile.goal]
        weekly_hours = profile.hours_per_day * profile.days_per_week
        notes: List[str] = []

        # Work out which skills the learner already knows.
        known = expand_known(profile.known)
        self.log(
            f"PERCEIVE: goal='{profile.goal}', "
            f"{profile.hours_per_day}h/day x {profile.days_per_week} days/week, "
            f"experience={profile.experience}"
        )
        self.log(f"INFER: student knows {len(known)} skills (including inferred prerequisites)")

        # Find the skills needed for the goal.
        pool = required_skills(goal["required"], known)
        self.log(f"SEARCH: backward chaining found {len(pool)} missing skills for the goal")

        # Keep the known skills that would otherwise have appeared in the plan.
        everything = required_skills(goal["required"], set())
        skipped = sorted(
            SKILLS[skill_id]["name"] for skill_id in everything & known
        )

        # Check whether the required and optional skills fit the deadline.
        feasible = True
        optional_ids: Set[str] = set()
        if profile.deadline_weeks:
            capacity = profile.deadline_weeks * weekly_hours
            needed_hours = self._total(pool)
            self.log(
                f"CONSTRAINT: deadline allows {capacity:.0f}h, "
                f"required skills need {needed_hours}h"
            )
            if needed_hours > capacity:
                feasible = False
                hours_per_day = (
                    needed_hours
                    / (profile.deadline_weeks * profile.days_per_week)
                )
                notes.append(
                    f"Deadline NOT achievable: required skills need {needed_hours}h "
                    f"but you have {capacity:.0f}h. Study ~{hours_per_day:.1f}h/day "
                    "or extend the deadline."
                )
            else:
                for optional_skill in goal["optional"]:
                    candidate = pool | required_skills(
                        [optional_skill], known | pool
                    )
                    if self._total(candidate) <= capacity:
                        optional_ids |= (candidate - pool)
                        pool = candidate
                        self.log(
                            f"CONSTRAINT: optional "
                            f"'{SKILLS[optional_skill]['name']}' fits, added"
                        )
                    else:
                        self.log(
                            f"CONSTRAINT: optional "
                            f"'{SKILLS[optional_skill]['name']}' does not fit, skipped"
                        )
        else:
            optional_names = [
                SKILLS[skill_id]["name"]
                for skill_id in goal["optional"]
                if skill_id not in known
            ]
            if optional_names:
                notes.append(
                    "Optional next steps after this roadmap: "
                    + ", ".join(optional_names)
                    + "."
                )

        # Put the skills in prerequisite order.
        order = order_skills(pool)
        violations = validate_plan(order, known)
        self.log(f"PLAN: ordered {len(order)} skills; constraint violations: {len(violations)}")
        if violations:
            raise RuntimeError("Invalid plan: " + "; ".join(violations))

        # Turn the ordered skills into a weekly schedule.
        steps: List[Step] = []
        cumulative = 0
        for number, skill_id in enumerate(order, 1):
            hours = adjusted_hours(skill_id, profile.experience)
            start_week = int(cumulative // weekly_hours) + 1
            cumulative += hours
            end_week = max(start_week, math.ceil(cumulative / weekly_hours))

            dependents = [
                SKILLS[other_skill]["name"]
                for other_skill in order
                if skill_id in SKILLS[other_skill]["needs"]
            ]
            if skill_id in goal["required"]:
                reason = "Core skill for your goal"
            elif dependents:
                reason = "Needed for: " + ", ".join(dependents)
            else:
                reason = "Recommended extra"

            steps.append(
                Step(
                    number,
                    skill_id,
                    SKILLS[skill_id]["name"],
                    hours,
                    start_week,
                    end_week,
                    reason,
                    skill_id in optional_ids,
                )
            )

        total_weeks = cumulative / weekly_hours if weekly_hours else 0
        if (
            profile.deadline_weeks
            and feasible
            and total_weeks > profile.deadline_weeks + 1e-9
        ):
            feasible = False

        return Result(
            steps,
            cumulative,
            total_weeks,
            feasible,
            notes,
            self.trace,
            skipped,
        )
