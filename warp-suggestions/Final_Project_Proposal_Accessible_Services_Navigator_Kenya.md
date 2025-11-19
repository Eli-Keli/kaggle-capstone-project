# Accessible Services Navigator (Nairobi): Multi-Agent Assistant for Disability-Inclusive Services

**Track:** Agents for Good  
**Title (for Kaggle):** Accessible Services Navigator (Nairobi)  
**Subtitle (for Kaggle):** A multi-agent ADK system that helps persons with disabilities in Nairobi find accessible clinics and social services.

---

## 1. Project Scope and Objectives

This project designs and implements a **Nairobi-only** Accessible Services Navigator as a realistic Capstone MVP.

- **Geographic scope:** Nairobi County only (subcounties/wards such as Westlands, Dagoretti North, Embakasi, CBD).
- **Service scope:** Public and low-cost **clinics**, **hospitals**, and **social service offices** (e.g., NCPWD registration points, social protection desks) within Nairobi.
- **Users:** Persons with disabilities (PWDs) and caregivers living in Nairobi who need to locate services that match their accessibility needs.
- **Goal:** Build a concrete, reproducible, data-backed **multi-agent system in a Kaggle Notebook** that demonstrates ADK concepts (multi-agent orchestration, tools, memory, evaluation, observability) while solving a focused problem.

Nairobi-only scope is a deliberate design choice: it keeps the dataset small enough to curate with reasonable quality, allows deeper evaluation per facility, and is well within the constraints of a single Capstone project.

---

## 2. Problem Statement: Discovering Accessible Services in Nairobi

PWDs in Nairobi face several recurring, well-defined problems when trying to access public services:

- **Fragmented information:** Clinic and social service information is distributed across ministry websites, PDFs, NGO brochures, and informal lists. There is no single, disability-aware directory for Nairobi.
- **Accessibility uncertainty:** Online listings rarely specify ramps, lifts, accessible toilets, sign-language support, or sensory-friendly spaces. Users cannot tell if a facility is realistically usable for their disability.
- **Bureaucratic navigation challenges:** Requirements for services (NCPWD card registration, social protection enrolment, clinic procedures) are inconsistent across offices and not written in one clear place.
- **Inconsistent online data:** Facility addresses, phone numbers, and operating hours differ across sources; some are outdated or incomplete.
- **High cognitive burden:** For a PWD or caregiver, manually cross-checking multiple sources, calling offices, and reconciling conflicting information is time-consuming and mentally exhausting.

The Capstone project addresses these issues by building a **Nairobi-focused assistant** that unifies curated data with light web search, applies accessibility-aware reasoning, and presents concise recommendations.

---

## 3. Minimum Viable Product (MVP)

The MVP is intentionally narrow and implementable in a Kaggle environment:

- **Curated Nairobi dataset**
  - A small but realistic dataset of **Nairobi clinics, hospitals, and social service offices** with basic accessibility annotations.
  - Stored as CSV/Parquet and loaded directly in the notebook.

- **Multi-agent workflow**
  - A four-agent pipeline (Intake/Profile → Search → Reasoning/Summary → Recommendation) orchestrated with ADK multi-agent constructs.

- **At least two tools**
  - **DatasetSearchTool:** custom Python tool that filters and ranks Nairobi facilities based on location, service type, and accessibility fields.
  - **WebEnrichmentTool:** wrapper around ADK’s `google_search` to fetch short snippets or descriptions for a subset of facilities (optional and configurable for deterministic runs).

- **Memory**
  - Use `InMemorySessionService` and an ADK memory service to retain the user’s profile (disability type, preferred area, language preference) and last recommended facilities across turns.

- **Evaluation scenarios**
  - 8–10 Nairobi-specific scenarios representing different disability types and subcounties.

- **Logging / observability**
  - Use ADK logging plugins to capture prompts, tool calls, and intermediate state for debugging and evaluation.

- **Simple, convincing demo path**
  - A single end-to-end workflow in the notebook that starts from a user query and ends with a ranked list of Nairobi facilities plus persisted memory, all visible through a `run_debug`-style trace.

The MVP explicitly does **not** attempt to be a nationwide or fully production-ready system; it is a tightly scoped, technically solid prototype.

---

## 4. Multi-Agent Architecture and Flow

The system is organised as a clear agent graph with well-defined responsibilities and handoffs.

### 4.1 Agents and Components

1. **Intake/Profile Agent**
   - **Input:** Natural-language request such as “I use a wheelchair and live in Embakasi; I need a public clinic for follow-up visits.”
   - **Responsibilities:**
     - Ask minimal clarifying questions (location, disability type, mobility/communication constraints, service type: clinic vs NCPWD vs social services).
     - Normalise inputs into a structured **User Profile** object, e.g.:
       - `disability_type`, `mobility_needs`, `communication_needs`
       - `preferred_subcounty`, `backup_subcounty`
       - `service_category` (clinic / hospital / NCPWD / social_service)
     - Store the profile into session + memory for reuse by downstream agents and future sessions.
   - **Output to next agent:** `UserProfile` JSON-like structure.

2. **Search Agent (Dataset + Web)**
   - **Input:** `UserProfile` from Intake/Profile Agent.
   - **Responsibilities:**
     - Call **DatasetSearchTool** to filter the Nairobi dataset by service category and (sub)county proximity.
     - Sort and return a small candidate set (e.g., top 5–10 facilities).
     - Optionally call **WebEnrichmentTool** (backed by `google_search`) to retrieve one or two short snippets per facility (description, recent notes), when internet access and quotas permit.
   - **Output to next agent:** `CandidateFacilities` list with structured fields + optional web snippets.

3. **Reasoning/Summary Agent**
   - **Input:** `UserProfile` + `CandidateFacilities`.
   - **Responsibilities:**
     - Compute an **accessibility-aware score** for each candidate using dataset fields:
       - Mobility fit (ramps, step-free access, lifts, distance).
       - Hearing fit (sign-language support, SMS/WhatsApp contact options).
       - Visual fit (good signage, staff assistance, clear directions).
     - Generate a concise, structured **ScoredFacilities** summary including justifications for top candidates.
     - Apply **context compaction**: condense the profile + candidate reasoning into a short textual summary that can be carried forward without overloading context.
   - **Output to next agent:** `ScoredFacilities` list + `ContextSummary`.

4. **Recommendation Agent**
   - **Input:** `ScoredFacilities` + `ContextSummary`.
   - **Responsibilities:**
     - Produce a user-facing recommendation in clear, non-technical language.
     - Highlight the **top 2–3 Nairobi facilities**, explicitly describing:
       - Where they are (subcounty/landmarks).
       - Why they fit the user’s accessibility and service needs.
       - What to bring or expect (e.g., NCPWD documents, clinic hours) based on the dataset/meta.
     - Save a concise **Service Plan** summary to memory (profile + top facilities) so that follow-up questions such as “remind me of the options in Westlands” can be answered using memory + lightweight search.

5. **Memory Layer**
   - `InMemorySessionService` to maintain the ongoing conversation state.
   - An ADK memory service (e.g., `InMemoryMemoryService`) to persist:
     - User profiles.
     - Context summaries.
     - The last recommended service set per user.

6. **Context Compaction**
   - After each full recommendation, the Reasoning/Summary Agent writes a compact `ContextSummary` that replaces long past interactions in subsequent calls.
   - This keeps the effective context small while preserving key facts.

7. **Logging and Metrics**
   - Use ADK logging plugin(s) to log:
     - Agent invocations.
     - Tool calls (dataset search, web search).
     - Latency per step and number of candidates per stage.
   - Logs are stored to a file (e.g., `logger.log`) for inspection within the Kaggle Notebook.

8. **Evaluation Suite**
   - A separate notebook cell or module that replays predefined scenarios through the entire agent graph.
   - Collects outputs and scores them against scenario-specific criteria (see Section 7).

### 4.2 Flow Summary

User query → **Intake/Profile Agent** → `UserProfile` → **Search Agent** → `CandidateFacilities` → **Reasoning/Summary Agent** → `ScoredFacilities` + `ContextSummary` → **Recommendation Agent** → final answer + `ServicePlan` stored in memory.

---

## 5. Dataset Design (Nairobi Only)

The project will use small, curated datasets scoped strictly to Nairobi.

### 5.1 Files

1. `nairobi_clinics.csv`
   - Public and low-cost clinics and hospitals in Nairobi.

2. `nairobi_social_services.csv`
   - NCPWD offices, social protection desks, and disability-related helpdesks located in Nairobi.

3. `nairobi_accessible_services.parquet` (optional consolidated file)
   - Combined and cleaned version for faster loading and querying.

### 5.2 Core Schema (shared fields)

Each row represents a facility or office with fields such as:

- `facility_id` (string, primary key)
- `facility_name` (string)
- `category` (enum: `clinic`, `hospital`, `ncpwd_office`, `social_service`)
- `subcounty` (e.g., `Westlands`, `Embakasi East`, `Langata`)
- `ward` (string)
- `neighbourhood_landmark` (string, e.g., “near Kenyatta Market”)
- `latitude`, `longitude` (floats, optional for approximate mapping)
- `managing_agency` (e.g., `County`, `National MoH`, `NGO`)
- `services_offered` (short text list)

### 5.3 Accessibility Scoring Fields

To support reasoning, each row will also have accessibility-specific fields:

- `has_ramp` (bool)
- `has_elevator_or_step_free_entry` (bool)
- `has_accessible_toilet` (bool)
- `has_sign_language_support` (bool)
- `supports_text_based_contact` (bool, e.g., SMS/WhatsApp)
- `visual_signage_quality` (enum: `low`, `medium`, `high`)
- `crowding_level` (enum: `low`, `medium`, `high`, approximate)
- `approx_cost_level` (enum: `free`, `low`, `moderate`)
- `mobility_score` (0–3)
- `hearing_score` (0–3)
- `visual_score` (0–3)
- `notes` (short free text)
- `data_source` (e.g., `MoH list`, `NCPWD site`, `manual survey`)
- `last_verified_date` (date string)

The `*_score` fields (0=not suitable, 3=very suitable) allow the Reasoning/Summary Agent to combine multiple fields into a single accessibility ranking for each disability category.

### 5.4 Example Rows

| facility_id | facility_name                        | category      | subcounty | ward       | has_ramp | has_sign_language_support | mobility_score | hearing_score | notes                                      |
|------------|---------------------------------------|--------------|----------|-----------|----------|---------------------------|----------------|--------------|--------------------------------------------|
| CLN-001    | Mbagathi County Hospital Outpatient  | clinic       | Langata  | Nairobi West | true     | false                     | 3              | 1            | Ramp at main entrance; busy mornings.      |
| SSC-010    | NCPWD Upper Hill Service Office      | ncpwd_office | Kibra    | Upper Hill | true     | true                      | 2              | 3            | Lift in building; KSL interpreter on some days. |

### 5.5 Curation Strategy

- **Manually curated base:**
  - 30–60 Nairobi facilities drawn from public MoH lists, NCPWD information, and NGO directories, cleaned and standardised offline before loading into the notebook.
- **Programmatic enrichment (optional):**
  - A one-time or batched process (outside the main demo run) may use `google_search` to fetch short descriptions or confirm addresses for a subset of facilities.
  - The enriched text snippets can either be stored back into the dataset or used at runtime by the Search Agent for additional context.

This approach keeps the dataset small, explainable, and version-controlled while still being realistic enough for the Capstone.

---

## 6. Demo Workflow (Single Polished Path)

The primary demo will show one cohesive, end-to-end use case inside a Kaggle Notebook.

**Scenario:**
> A wheelchair user living near Donholm (Embakasi East) needs an affordable public clinic for regular check-ups.

**Workflow:**

1. **User input (notebook cell):**
   - The user types a natural-language query describing their location (Donholm, Embakasi), wheelchair use, and preference for a public clinic.

2. **Intake/Profile Agent:**
   - Clarifies missing details if needed (e.g., preferred time of day, whether sign-language support is required).
   - Produces a structured `UserProfile` and stores it in session + memory.

3. **Search Agent:**
   - Invokes **DatasetSearchTool** to filter `nairobi_clinics.csv` for clinics in Embakasi East (and optionally neighbouring subcounties) with `mobility_score ≥ 2` and `approx_cost_level ∈ {"free", "low"}`.
   - Returns a short list of candidate facilities with key fields.
   - Optionally calls **WebEnrichmentTool** for the top 3 results to fetch short web descriptions.

4. **Reasoning/Summary Agent:**
   - Scores each candidate clinic for the user’s profile (wheelchair user, regular visits, cost sensitivity).
   - Produces `ScoredFacilities` plus a one-paragraph `ContextSummary` capturing why the top 2–3 clinics are preferred.

5. **Recommendation Agent:**
   - Generates a concise explanation listing the best 2–3 clinics, their subcounties/landmarks, and specific accessibility reasons.
   - Writes a `ServicePlan` summary (profile + top clinics) into memory.

6. **Notebook output:**
   - Displays the final user-facing recommendation.
   - Optionally shows a condensed debug view: which tools were called, how many candidates were filtered, and the top scores.

7. **Follow-up query (memory demonstration):**
   - The user asks “Remind me of the clinic you recommended in Embakasi East.”
   - The system uses memory to retrieve the stored `ServicePlan` and answers without re-running the full search.

This single polished path is realistic for a Capstone, yet clearly exercises the multi-agent workflow, tools, memory, and observability.

---

## 7. Evaluation Plan

The evaluation plan combines **scenario-based testing** with **agent-level checks**.

### 7.1 Nairobi-Specific Test Scenarios (8–10)

Example scenarios (all within Nairobi):

1. Wheelchair user in **Embakasi East** looking for a low-cost public clinic for monthly check-ups.
2. Deaf user working in **Nairobi CBD** seeking an NCPWD office with **sign-language support** for card renewal.
3. Blind user living in **Westlands** needing a clinic with good staff assistance and clear directions.
4. Parent of a child with cerebral palsy in **Langata** looking for a clinic with physiotherapy services.
5. Hearing-impaired user in **Dagoretti North** needing a social protection desk that supports SMS/WhatsApp communication.
6. User with limited mobility in **Kibra** wanting the nearest facility with a reliable ramp and accessible toilet.
7. Low-income wheelchair user in **Mathare** needing a **free or very low-cost** clinic for chronic care.
8. Visually impaired user commuting through **Upper Hill** looking for an NCPWD or social office with clear signage and lift access.
9. Wheelchair user frequently in **Westlands** during work hours needing a centrally located clinic.
10. Mixed-disability household in **Embakasi West** needing information about both clinic services and social services in one session.

### 7.2 Success Criteria

For each scenario, we will check:

- **Service relevance:** At least one recommended facility is in the correct or a clearly justified neighbouring subcounty/ward.
- **Accessibility alignment:** The explanation references at least one relevant accessibility attribute for the user’s disability (e.g., ramp, sign-language, signage).
- **Data consistency:** Recommendations do not contradict core dataset fields (e.g., do not claim a ramp where `has_ramp = false`).
- **Clarity and brevity:** Response is understandable, avoids jargon, and fits within a reasonable length for screen readers.
- **Tool usage:** Search Agent invokes dataset search at least once; web enrichment is used only when configured and does not dominate reasoning.

### 7.3 Agent-Level Testing

- **Intake/Profile Agent:**
  - Test prompts simulating different ways users describe their disabilities and locations.
  - Verify that the resulting `UserProfile` JSON correctly populates `disability_type`, `service_category`, and `preferred_subcounty`.

- **Search Agent:**
  - Unit tests calling **DatasetSearchTool** directly with synthetic profiles to validate filtering by `subcounty`, `category`, and accessibility scores.
  - Edge cases: no suitable facilities in a subcounty, fallback to nearby areas.

- **Reasoning/Summary Agent:**
  - Provide synthetic `CandidateFacilities` lists and check that higher accessibility scores are consistently favoured.
  - Validate that `ContextSummary` remains within a small token budget.

- **Recommendation Agent:**
  - Given fixed `ScoredFacilities`, verify that the agent:
    - Mentions the correct top facilities.
    - Includes at least one explicit accessibility justification.
    - Writes a `ServicePlan` object to memory.

### 7.4 Failure Analysis

- Use log files and `run_debug` traces to inspect misbehaving scenarios.
- Categorise failures into:
  - **Data gaps** (dataset missing relevant facility or incorrect annotation).
  - **Search issues** (filtering too strict/too loose).
  - **Reasoning errors** (incorrect weighting of accessibility fields).
  - **Presentation issues** (missing explanation, confusing wording).
- For each category, document at least one example and propose small, practical fixes (e.g., adjust scoring rubric, correct dataset rows, tweak prompts).

---

## 8. Implementation Notes and Risks

- **Technology stack:**
  - ADK Python, Gemini models (e.g., `gemini-2.5-flash` / `gemini-2.5-flash-lite`).
  - Kaggle Notebook or GitHub repository as the primary delivery format.

- **Key risks:**
  - **Small dataset size:** With a few dozen Nairobi facilities, coverage is limited. The proposal treats this as a prototyping constraint and documents it clearly.
  - **Annotation accuracy:** Accessibility fields may be approximate; the project will emphasise that data is illustrative, not official.
  - **Model behaviour variability:** LLM reasoning can be non-deterministic; the evaluation harness and logging help identify and mitigate major issues.

- **Why Nairobi-only is strategic:**
  - Enables higher-quality curation and more reliable evaluation.
  - Keeps the project within Capstone time and resource limits.
  - Provides a template that could later be extended to other Kenyan counties without redesigning the architecture.

Overall, this proposal describes a **focused, technically grounded, Nairobi-scoped Capstone project** that demonstrates practical multi-agent design, tool integration, memory, observability, and evaluation using ADK in a way that is achievable within a single notebook.
