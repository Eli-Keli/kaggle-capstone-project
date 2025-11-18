# Inclusive AI Agent Project Ideas for Kenyan Persons with Disabilities

This document lists candidate Capstone project ideas for the 5‑Day AI Agents Intensive Course with Google. All ideas target inclusivity and accessibility for persons with disabilities (PWDs) in a Kenyan context and fit the **Agents for Good** track. Each idea is designed to showcase multiple ADK capabilities (multi‑agent systems, tools, sessions & memory, observability, evaluation, A2A, and optional deployment).

## Idea 1 – Accessible Services Navigator for Kenyan PWDs (Recommended)

**Track:** Agents for Good  
**Problem:** Information about accessible public services in Kenya (clinics, NHIF/NCPWD offices, social protection desks, schools, transport routes) is fragmented, often out of date, and rarely organized in disability‑friendly ways. PWDs and caregivers spend a lot of time asking around just to find a clinic with ramps or a sign‑language interpreter.  
**Agentic solution:** A multi‑agent assistant that profiles the user (location, disability, mobility and communication needs), searches structured and unstructured sources for services near them, and returns ranked, accessibility‑aware recommendations plus next steps (e.g., documents to bring, estimated costs).  
**Key ADK concepts:**

- Multi‑agent pipeline (Profiling Agent → Data/Research Agent → Accessibility Reasoning Agent → Recommendation/Follow‑up Agent) using `SequentialAgent` and optionally `ParallelAgent`.
- Tools: Google Search, custom HTTP/API tools for Kenyan open data and NGO datasets, and simple code‑execution tools to clean/merge tabular data.
- Sessions & memory: store user profile and previous searches so the agent can personalize recommendations over time.
- Context engineering: compact search and profile history into summaries for long conversations.
- Observability & evaluation: logging plugin, traces for tool calls, and a small evaluation set of typical PWD scenarios.
- Optional A2A: integrate with a remote NGO “resource catalog” agent exposed via A2A.
- Optional deployment: package as an ADK app that can be deployed to Agent Engine.

**Kenya‑specific context & data sources (examples):**

- Public service locations from Kenyan open data portals and county websites.
- NGO/CSO datasets from disability organizations (e.g., service directories exported as CSV).
- Manually curated sample data where official APIs are missing, to keep the demo reproducible in a Kaggle Notebook.

## Idea 2 – Inclusive Skills and Job Coach for Kenyan PWDs

**Track:** Agents for Good  
**Problem:** Kenyan PWDs often face barriers in accessing formal employment and training, from inaccessible job platforms to lack of guidance on which roles can be adapted to their abilities.  
**Agentic solution:** A coaching assistant that helps a PWD user map their skills and constraints to realistic job roles, suggests accessible upskilling paths (online courses, TVETs, community programs), and tailors CV and cover letters to inclusive employers.  
**Key ADK concepts:**

- Multi‑agent system: Profiling Agent, Job/Training Research Agent, CV Tailor Agent, Interview Coach Agent.
- Tools: web/job‑board search, course catalog search, simple OpenAPI tools for training providers, code executor for CV formatting.
- Sessions & memory: remember user skills, interests, and job search history.
- Evaluation: scenario‑based tests (e.g., deaf software tester in Nairobi, wheelchair user in Mombasa seeking accounting work).

## Idea 3 – Accessible Learning Path Planner for Kenyan Students with Disabilities

**Track:** Agents for Good  
**Problem:** Secondary and tertiary students with disabilities often lack tailored advice on which subjects, institutions, and delivery modes (online, in‑person, hybrid) will be accessible to them.  
**Agentic solution:** An advisory agent that helps students pick subjects and institutions, highlighting accessibility features (e.g., ramps, braille materials, sign‑language support, exam accommodations) and suggesting low‑bandwidth learning options.  
**Key ADK concepts:**

- Multi‑agent: Student Profiling Agent, Curriculum/Institution Research Agent, Accessibility Policy Agent, Study‑Plan Generator Agent.
- Tools: search and structured data about Kenyan universities/TVETs, MCP/OpenAPI tools for static datasets hosted behind an MCP server.
- Sessions & memory: keep long‑term profile of the learner’s goals and constraints.
- Context engineering: condense multi‑term planning discussions into summary notes.
- Observability & evaluation: test plans against a rubric for clarity, feasibility, and accessibility coverage.

## Idea 4 – Assistive‑Tech and Social Benefits Advisor for Kenyan PWD Households

**Track:** Agents for Good  
**Problem:** Many Kenyan families are unaware of affordable assistive devices (wheelchairs, white canes, hearing aids) and government or NGO‑run benefits (cash transfers, NHIF waivers, NCPWD cards). Rules are complex and change over time.  
**Agentic solution:** An eligibility and options advisor that asks structured questions, explains which assistive devices or benefits may fit, and breaks down application steps in simple language (and optionally in Kiswahili or Sheng).  
**Key ADK concepts:**

- Tools: rules/eligibility logic implemented as custom tools, plus web search for up‑to‑date program information.
- Multi‑agent: Eligibility Agent, Benefits Explainer Agent, Document Checklist Agent.
- Long‑running operations: pause/resume around actions that require human approval or document preparation.
- Memory: store partial application progress across sessions.

## Idea 5 – Accessible Transport and Route Advisor for Nairobi Commuters with Disabilities

**Track:** Agents for Good  
**Problem:** Commuters with mobility, visual, or hearing impairments struggle to know in advance which routes, matatus, or BRT stations are accessible, safe, and affordable.  
**Agentic solution:** A route‑planning agent tailored to accessibility constraints: it factors in ramps, step‑free paths, typical crowding, and cost, and can suggest realistic alternatives (e.g., paratransit, boda, walking) based on the user’s profile and location.  
**Key ADK concepts:**

- Multi‑agent: Data Ingestion Agent for static GTFS‑like data, Live‑Info Agent (optional), Route Planner Agent, Explanation Agent.
- Tools: custom tools over transport datasets (real or synthetic), Google Search to fetch station details, potential A2A integration with a separate “transport status” agent.
- Sessions & memory: remember frequent routes (home ↔ work, clinic, school) and user comfort levels.

---

**Recommended final project for the Capstone:**  
Idea 1 – **Accessible Services Navigator for Kenyan PWDs**. It has clear social impact, is feasible with static datasets inside Kaggle, and naturally exercises many of the required ADK features (multi‑agent orchestration, tools, sessions & memory, context engineering, observability, evaluation, optional A2A and deployment).