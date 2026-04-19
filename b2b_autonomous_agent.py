"""Autonomous B2B multi-agent pipeline using CrewAI.

This module implements the "Researcher & Executioner" architecture:
- Scout: discovers target leads.
- Analyst: enriches and identifies pain points.
- Writer: drafts personalized outreach.
- Manager: quality gate + CRM-ready payload.

Environment variables expected:
- OPENAI_API_KEY (or any model provider key configured with CrewAI)
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from textwrap import dedent

from crewai import Agent, Crew, Process, Task


@dataclass(frozen=True)
class PipelineConfig:
    """Configuration for the B2B outbound pipeline."""

    industry: str
    geography: str
    icp: str
    max_leads: int = 20


class AutonomousB2BAgentSystem:
    """Orchestrates a 4-agent outbound intelligence workflow."""

    def __init__(self, config: PipelineConfig) -> None:
        self.config = config
        self._validate_environment()

        self.scout = Agent(
            role="Lead Scout",
            goal=(
                "Discover high-intent B2B prospects matching our ICP from public web "
                "sources such as company websites, directories, and professional networks."
            ),
            backstory=(
                "You are an elite sales intelligence researcher. You always produce structured "
                "lead lists with evidence-backed qualification signals."
            ),
            verbose=True,
            allow_delegation=False,
            memory=True,
        )

        self.analyst = Agent(
            role="Pain-Point Analyst",
            goal=(
                "Analyze each lead's product, hiring signals, and GTM posture to infer "
                "business pain points and purchase triggers."
            ),
            backstory=(
                "You are a strategic consultant who can infer hidden operational bottlenecks "
                "from weak signals in public data."
            ),
            verbose=True,
            allow_delegation=False,
            memory=True,
        )

        self.writer = Agent(
            role="Personalized Outreach Writer",
            goal=(
                "Write concise, human-sounding outbound messages tailored to the lead's "
                "context, pain, and expected outcomes."
            ),
            backstory=(
                "You are a top-performing SDR + copywriter hybrid. Your messages feel native, "
                "specific, and never templated."
            ),
            verbose=True,
            allow_delegation=False,
        )

        self.manager = Agent(
            role="Revenue Ops Manager",
            goal=(
                "Perform final quality control, remove weak leads, assign confidence scores, "
                "and return CRM-ready records."
            ),
            backstory=(
                "You are a detail-oriented RevOps lead trusted by sales leadership for pipeline "
                "hygiene and reporting accuracy."
            ),
            verbose=True,
            allow_delegation=False,
        )

    @staticmethod
    def _validate_environment() -> None:
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY is not set. Configure your LLM key before running.")

    def _build_tasks(self) -> list[Task]:
        scout_task = Task(
            description=dedent(
                f"""
                Find up to {self.config.max_leads} companies in {self.config.geography}
                within {self.config.industry} that match this ICP:
                {self.config.icp}

                Return strict JSON array with fields:
                [
                  {{
                    "company_name": str,
                    "website": str,
                    "linkedin_url": str,
                    "decision_maker_title": str,
                    "signal": str,
                    "source": str
                  }}
                ]
                """
            ).strip(),
            expected_output="JSON array of qualified lead objects.",
            agent=self.scout,
        )

        analyst_task = Task(
            description=dedent(
                """
                For each lead from Scout output, analyze the company's web presence and infer:
                1) likely operational/commercial pain points,
                2) urgency triggers,
                3) estimated fit score (0-100).

                Return strict JSON array preserving input fields plus:
                - pain_points: list[str]
                - urgency_trigger: str
                - fit_score: int
                - reasoning: str
                """
            ).strip(),
            expected_output="JSON array of enriched leads with pain-point analysis.",
            agent=self.analyst,
            context=[scout_task],
        )

        writer_task = Task(
            description=dedent(
                """
                Draft one personalized outbound email per lead.
                Constraints:
                - 90 to 140 words
                - conversational but professional
                - specific first line referencing lead context
                - clear CTA for a 15-min discovery call

                Return strict JSON array with:
                - company_name
                - subject_line
                - email_body
                """
            ).strip(),
            expected_output="JSON array of personalized outreach drafts.",
            agent=self.writer,
            context=[analyst_task],
        )

        manager_task = Task(
            description=dedent(
                """
                QA both analysis and drafts. Reject weak personalization.
                Keep only leads with fit_score >= 70.

                Return final strict JSON array where each object includes:
                - company_name
                - website
                - decision_maker_title
                - fit_score
                - pain_points
                - subject_line
                - email_body
                - confidence_label (high/medium)
                - crm_note
                """
            ).strip(),
            expected_output="CRM-ready JSON array of high-quality opportunities.",
            agent=self.manager,
            context=[analyst_task, writer_task],
        )

        return [scout_task, analyst_task, writer_task, manager_task]

    def run(self) -> str:
        crew = Crew(
            agents=[self.scout, self.analyst, self.writer, self.manager],
            tasks=self._build_tasks(),
            process=Process.sequential,
            verbose=True,
            memory=True,
        )
        return crew.kickoff()


def main() -> None:
    config = PipelineConfig(
        industry="B2B SaaS",
        geography="India",
        icp=(
            "Series A-C SaaS companies with 20-300 employees, active hiring in sales/customer "
            "success, and visible demand generation efforts."
        ),
        max_leads=15,
    )

    system = AutonomousB2BAgentSystem(config=config)
    result = system.run()

    print("\n===== FINAL OUTPUT =====\n")

    try:
        parsed = json.loads(result)
        print(json.dumps(parsed, indent=2, ensure_ascii=False))
    except json.JSONDecodeError:
        print(result)


if __name__ == "__main__":
    main()
