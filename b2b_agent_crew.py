"""Autonomous B2B multi-agent scaffold using CrewAI.

This script demonstrates the "Researcher & Executioner" concept:
- Scout: lead sourcing
- Analyst: pain-point + fit analysis
- Writer: personalized outreach
- Manager: quality control + CRM handoff

Replace placeholder tools/integrations with real connectors for production use.
"""

from crewai import Agent, Crew, Task


TOPIC = "B2B AI automation services buyers in India (2026)"


scout = Agent(
    role="Lead Scout",
    goal="Discover high-potential B2B leads relevant to {topic} with source evidence.",
    backstory=(
        "You are an expert at finding high-intent leads from public web signals, "
        "industry directories, and business profiles."
    ),
    verbose=True,
    allow_delegation=False,
    memory=True,
)

analyst = Agent(
    role="Market & Pain-Point Analyst",
    goal=(
        "Filter leads by ICP-fit, then infer business pain points from websites, "
        "job posts, product pages, and news updates."
    ),
    backstory=(
        "You specialize in extracting decision-maker-relevant insights and ranking "
        "opportunities by urgency and expected ROI."
    ),
    verbose=True,
    allow_delegation=False,
    memory=True,
)

writer = Agent(
    role="Personalized Outreach Writer",
    goal="Write human-like, context-aware outreach for each validated lead.",
    backstory=(
        "You convert technical and business context into concise, persuasive emails "
        "that sound natural and executive-friendly."
    ),
    verbose=True,
    allow_delegation=False,
)

manager = Agent(
    role="Campaign Manager",
    goal=(
        "Validate quality, remove weak claims, and output CRM-ready structured records "
        "for approved leads and messages."
    ),
    backstory=(
        "You enforce output quality, consistency, and compliance before pushing data "
        "to downstream systems such as HubSpot/Salesforce."
    ),
    verbose=True,
    allow_delegation=True,
)


lead_research_task = Task(
    description=(
        "Research at least 10 leads for topic: {topic}. For each lead capture: "
        "company name, website, potential contact role, source URL, and a short why-now signal."
    ),
    expected_output=(
        "A markdown table of leads with source links and confidence notes for each entry."
    ),
    agent=scout,
)

analysis_task = Task(
    description=(
        "Analyze researched leads, score ICP fit (1-10), identify top pain points, "
        "and keep only top 5 leads with strongest urgency and value alignment."
    ),
    expected_output=(
        "A prioritized top-5 list with score, pain points, buying triggers, and rationale."
    ),
    agent=analyst,
)

writing_task = Task(
    description=(
        "For each shortlisted lead, write: subject line, short personalization opener, "
        "value proposition, and one clear CTA. Keep tone professional and human."
    ),
    expected_output=(
        "Five personalized outreach messages with subject + body + CTA and one variant each."
    ),
    agent=writer,
)

qa_and_crm_task = Task(
    description=(
        "Review all outreach drafts for factual safety and quality. Produce final CRM-ready "
        "JSON records with fields: company, contact_role, pain_points, score, subject, message, cta."
    ),
    expected_output=(
        "A validated JSON array suitable for HubSpot/Salesforce upsert plus a short QA summary."
    ),
    agent=manager,
)


crew = Crew(
    agents=[scout, analyst, writer, manager],
    tasks=[lead_research_task, analysis_task, writing_task, qa_and_crm_task],
    verbose=True,
)


if __name__ == "__main__":
    result = crew.kickoff(inputs={"topic": TOPIC})
    print("\n=== FINAL OUTPUT ===\n")
    print(result)
