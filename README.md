# Agentic — Researcher & Executioner (Autonomous B2B Agent)

Ye project ek **multi-agent outbound system** ka starter implementation hai jo sirf baat nahi karta, balki:
1. leads research karta hai,
2. unke pain points identify karta hai,
3. personalized outreach likhta hai,
4. CRM-ready output banata hai.

## Architecture

System mein 4 agents hain:

- **Agent A — Scout**: ICP ke hisaab se web se leads collect karta hai.
- **Agent B — Analyst**: company signals aur website context se pain points infer karta hai.
- **Agent C — Writer**: har lead ke liye personalized email draft karta hai.
- **Agent D — Manager**: quality gate lagata hai aur final CRM-ready records return karta hai.

Implementation file: `b2b_autonomous_agent.py`

## Tech choices

- **Orchestration**: CrewAI (sequential multi-agent flow)
- **LLM**: CrewAI-configured provider (e.g., GPT-4o / Gemini via configured backend)
- **Memory**: Crew + agent-level memory enabled
- **Output contract**: strict JSON at each stage

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="your-key"
```

## Run

```bash
python b2b_autonomous_agent.py
```

## What you can extend next

- Scout mein real tools add karo (SERP, LinkedIn API, company DB connectors).
- Analyst mein website crawler + intent scoring model plug karo.
- Writer mein A/B variant generation aur tone controls add karo.
- Manager step se direct HubSpot/Salesforce API push enable karo.

## Notes

- Current script production-safe template nahi, balki **strong starting blueprint** hai.
- Real internet browsing execution ke liye compliant tooling + rate-limits + legal checks zaroor add karein.
