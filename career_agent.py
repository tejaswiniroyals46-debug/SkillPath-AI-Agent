"""SkillPath AI's lightweight, evidence-aware career mission agent.

The controller selects a mission from student context, checks a submission
against an explicit rubric, records evidence and uses past mistakes to guide
its next recommendation. It does not claim that heuristic checks prove that
cheating did not occur.
"""
from __future__ import annotations

import re
from typing import Any


MISSION_LIBRARY = {
    "software": [
        {"skill": "Problem solving", "title": "Trace a small program", "instructions": "Write a short Python function that counts how many even numbers are in a list. Include the function, one example call, the expected output, and 2-3 sentences explaining how your loop works.", "rubric": ["def", "even", "return", "example", "because"]},
        {"skill": "Debugging", "title": "Find and explain a bug", "instructions": "A function should return the largest number in a list, but it starts with largest = 0. Explain why this fails for a list of negative numbers, provide a corrected version, and show a test case.", "rubric": ["negative", "first", "correct", "test", "return"]},
        {"skill": "Testing", "title": "Design edge-case tests", "instructions": "Imagine a function that accepts an age and returns whether a person is eligible for a student discount (age 18 or below). Give at least 3 test cases including a boundary case, expected results, and why each case matters.", "rubric": ["18", "boundary", "expected", "below", "above"]},
    ],
    "web": [
        {"skill": "HTML and CSS", "title": "Build an accessible profile card", "instructions": "Write a small HTML profile card with a heading, description, and link, then add CSS to space it clearly. Explain one accessibility choice and show the main code.", "rubric": ["html", "css", "heading", "link", "accessibility"]},
        {"skill": "JavaScript", "title": "Validate a form field", "instructions": "Describe or write a JavaScript function that checks whether an email field is empty before submission. Include one valid case, one invalid case, and explain the condition.", "rubric": ["javascript", "empty", "if", "valid", "invalid"]},
        {"skill": "Debugging", "title": "Diagnose a layout issue", "instructions": "A card looks too wide on a phone. Suggest a CSS fix using a responsive rule, show a short example, and explain why it helps small screens.", "rubric": ["media", "width", "responsive", "screen", "css"]},
    ],
    "data": [
        {"skill": "Data cleaning", "title": "Plan a data-cleaning pass", "instructions": "A student dataset has missing ages, duplicate rows, and inconsistent branch names. Explain the order you would handle these issues and give one example for each.", "rubric": ["missing", "duplicate", "consistent", "example", "validate"]},
        {"skill": "Statistics", "title": "Explain a useful summary", "instructions": "For values 2, 3, 3, 4, 20, calculate the mean and median, then explain which better represents a typical value and why.", "rubric": ["mean", "median", "32", "3", "outlier"]},
        {"skill": "Model evaluation", "title": "Avoid misleading accuracy", "instructions": "A model predicts 95% of a dataset correctly, but 95% of rows belong to one class. Explain why accuracy may mislead and name two additional evaluation checks.", "rubric": ["imbalance", "precision", "recall", "class", "baseline"]},
    ],
    "cyber": [
        {"skill": "Security awareness", "title": "Assess a suspicious message", "instructions": "A message asks you to urgently sign in through an unfamiliar link. List safe verification steps, explain two warning signs, and state what you would do before clicking.", "rubric": ["sender", "link", "verify", "password", "report"]},
        {"skill": "Access control", "title": "Apply least privilege", "instructions": "A student project app has admin, teacher, and student roles. Propose what each role should be allowed to do and explain least privilege.", "rubric": ["least privilege", "admin", "student", "permission", "minimum"]},
        {"skill": "Incident response", "title": "Respond to an exposed key", "instructions": "A developer accidentally pushes an API key to a public repository. Describe the first safe response steps and how to prevent recurrence.", "rubric": ["revoke", "rotate", "secret", "environment", "history"]},
    ],
    "general": [
        {"skill": "Communication", "title": "Explain a project clearly", "instructions": "Choose a project you have worked on. Explain the problem, your contribution, one challenge, how you tested the result, and what you would improve next.", "rubric": ["problem", "contribution", "challenge", "tested", "improve"]},
        {"skill": "Learning strategy", "title": "Turn a gap into a plan", "instructions": "Choose one skill you want to improve. Give a small practice task, a way to check the result, and what you will do if the first attempt fails.", "rubric": ["skill", "practice", "check", "feedback", "retry"]},
        {"skill": "Problem solving", "title": "Compare two solutions", "instructions": "Describe a simple problem and two ways to solve it. Compare correctness, time or effort, and explain which solution you would choose and why.", "rubric": ["problem", "solution", "compare", "trade-off", "because"]},
    ],
}


def category_for_goal(goal: str | None) -> str:
    text = (goal or "").lower()
    if any(x in text for x in ("web", "frontend", "full stack")):
        return "web"
    if any(x in text for x in ("data", "machine learning", "ml engineer", "ai engineer")):
        return "data"
    if any(x in text for x in ("cyber", "security")):
        return "cyber"
    if any(x in text for x in ("software", "developer", "program")):
        return "software"
    return "general"


def select_mission(goal: str | None, summary: dict[str, Any]) -> dict[str, Any]:
    """Pick a mission, preferring skills with weaker or missing evidence."""
    category = category_for_goal(goal)
    library = MISSION_LIBRARY[category]
    evidence = summary.get("evidence", [])
    recent_skills = [e.get("skill", "") for e in evidence[:8]]
    # Rotate toward a skill not seen recently; after the full set, cycle again.
    candidates = [m for m in library if m["skill"] not in recent_skills[:3]]
    chosen = (candidates or library)[len(summary.get("events", [])) % len(candidates or library)]
    return dict(chosen)


def verify_submission(mission: dict[str, Any], submission: str, prior_evidence: list[dict[str, Any]]) -> dict[str, Any]:
    """Transparent rubric-based check; it is not proof against copied work."""
    normalized = re.sub(r"\s+", " ", submission.lower()).strip()
    rubric = mission.get("rubric", [])
    matched = [term for term in rubric if term.lower() in normalized]
    score = round(100 * len(matched) / max(1, len(rubric)))
    has_explanation = len(normalized.split()) >= 35 and any(
        marker in normalized for marker in ("because", "therefore", "this means", "i chose", "the reason")
    )
    prior_success = any(
        e.get("skill") == mission.get("skill") and int(e.get("score", 0)) >= 60
        for e in prior_evidence
    )
    if score >= 75 and has_explanation and prior_success:
        level = "Demonstrated"
    elif score >= 45:
        level = "Initial evidence"
    else:
        level = "Needs more evidence"
    missing = [term for term in rubric if term not in matched]
    if level == "Demonstrated":
        feedback = "Good progress. Your response covered the rubric and included an explanation, with earlier evidence for this skill too. Try a new variation to check transfer to a different problem."
    elif level == "Initial evidence":
        feedback = "Some useful evidence is present, but this is not enough to confirm the skill yet. Add a clearer explanation of your choices and address the missing rubric points."
    else:
        feedback = "There is not enough evidence yet. Revisit the task requirements, write your own reasoning step by step, and include an example or test that supports your answer."
    if missing:
        feedback += " Points to review: " + ", ".join(missing[:5]) + "."
    if not has_explanation:
        feedback += " Include a short explanation in your own words; a final answer alone is not enough."
    return {"score": score, "level": level, "feedback": feedback, "matched": matched, "missing": missing}


def build_student_context(profile: dict | None, goal: str | None, history: list[dict], summary: dict) -> str:
    profile = profile or {}
    recent = history[:3]
    return (
        f"Student: {profile.get('full_name', 'Student')}; branch: {profile.get('branch', 'not set')}; "
        f"year: {profile.get('year', 'not set')}; interests: {profile.get('interests', 'not set')}; "
        f"self-reported skills: {profile.get('skills', 'not set')}; career goal: {goal or 'not selected'}. "
        f"Recent assessment history: {recent}. Mission count: {summary.get('missions_total', 0)}; "
        f"completed missions: {summary.get('missions_completed', 0)}. Recent skill evidence: {summary.get('evidence', [])[:8]}. "
        "Treat profile skills as self-reported, not verified. Clearly distinguish evidence from assumptions."
    )
