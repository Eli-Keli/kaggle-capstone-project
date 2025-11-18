# Accessible Services Navigator: Multi-Agent Assistant for Kenyan Persons with Disabilities

**Track:** Agents for Good  
**Title (for Kaggle):** Accessible Services Navigator: Multi-Agent Assistant for Kenyan PWDs  
**Subtitle (for Kaggle):** Helping Kenyan persons with disabilities discover accessible services, benefits, and support using AI agents built with Google’s ADK.

## 1. Problem and Motivation

In Kenya, persons with disabilities (PWDs) and their caregivers often struggle to find clear, up-to-date information about services that are genuinely accessible to them. Details about ramps, sign-language interpreters, tactile paving, accessible toilets, or quiet waiting areas are rarely centralised. Instead, PWDs rely on informal networks—asking friends, community health volunteers, or local WhatsApp groups—to answer basic questions such as:

- Which public hospital near me has wheelchair access and accessible toilets?
- Where can I register for an NCPWD card, and what documents do I need?
- Are there disability-friendly legal aid or social protection desks in my county?

This information barrier leads to wasted time, higher transport costs, and exclusion from health, education, and social protection systems. An AI agentic system can help bridge this information gap by aggregating scattered data sources and reasoning about accessibility for different disability profiles.

## 2. Proposed Solution (High-Level)

We propose an **Accessible Services Navigator**: a multi-agent assistant that helps Kenyan PWDs (and their families or support workers) discover nearby services that match their specific accessibility needs, and guides them through next steps.

From a user’s perspective:

1. The agent asks short, clear questions about location, disability type, mobility/communication needs, and preferred language.
2. It searches structured and unstructured sources (datasets plus web pages) for services in the user’s county or town.
3. It reasons about which services are likely to be usable, given the user’s profile (e.g., wheelchair user vs. blind user).
4. It returns a ranked list of options with:
   - Accessibility notes (e.g., ramp present, sign-language support, low stairs only).
   - Practical details (opening hours, approximate costs, what to bring).
   - Simple wording that can be read aloud by screen readers.

The project will be implemented in a Kaggle Notebook or GitHub repo using the **Agent Development Kit (ADK)**.

## 3. Target Users and Use Cases

Primary users:

- Adults with mobility, visual, hearing, or cognitive disabilities in Kenyan counties.
- Parents and caregivers of children with disabilities.
- Community-based organisations and disability advocates who support multiple clients.

Example use cases:

- A wheelchair user in Kisumu wants to find a public facility where they can renew their NCPWD card without facing steep stairs.
- A deaf user in Nairobi wants to know which hospitals have sign-language interpreters or SMS-based triage lines.
- A parent of a child with cerebral palsy in Mombasa wants to locate physiotherapy services that are both affordable and physically accessible.

## 4. Agentic Architecture

The system will use a **multi-agent architecture** composed of specialised agents orchestrated via ADK:

1. **Intake and Profile Agent**
   - Collects user profile: location, disability type, mobility and communication needs, and preferred language.
   - Normalises responses into a structured “Accessibility Profile”.
   - Stores key details in long-term memory for future sessions.

2. **Data and Research Agent**
   - Uses tools to query:
     - Static service directories stored as CSV/Parquet files in the project (e.g., health facilities, social services, NGO centres).
     - Web search (via the built-in `google_search` tool) for additional details such as accessibility statements or photos.
   - Can run in parallel over multiple data sources where beneficial.

3. **Accessibility Reasoning Agent**
   - Interprets raw data and heuristically scores the accessibility of each candidate service for the current user’s profile.
   - For example: mark facilities with ramps as high-suitability for wheelchair users, and discount those without clear access information.

4. **Recommendation and Follow-up Agent**
   - Produces final, user-friendly recommendations.
   - Suggests next actions (which documents to bring, typical queues, suggested time of day).
   - Optionally summarises the conversation and saves it to memory as a brief “service plan”.

These agents are orchestrated using **SequentialAgent** (and optionally **ParallelAgent**) to clearly demonstrate multi-agent composition.

## 5. Key ADK Concepts Demonstrated

The project is explicitly designed to satisfy the Capstone requirement of using at least three core concepts, and in practice will aim to include more:

- **Multi-agent system**
  - Intake and Profile Agent, Data and Research Agent, Accessibility Reasoning Agent, Recommendation and Follow-up Agent.
  - Orchestrated via Sequential and Parallel agents.

- **Tools**
  - Built-in tools: `google_search` for web results.
  - Custom Python tools:
    - Service-directory lookups over local datasets (e.g., filter health facilities by county and type).
    - Simple scoring utilities that assign accessibility scores.
  - Optional MCP or OpenAPI tools to wrap local datasets behind a consistent interface.

- **Sessions and Memory**
  - Use `InMemorySessionService` for conversational state.
  - Use a memory service to persist user profiles (disability type, base location, language preferences) across sessions.
  - Demonstrate how the agent can recall a returning user and avoid re-asking every question.

- **Context Engineering**
  - Implement context compaction: summarise long search histories and recommendations into short notes that can fit within model context.
  - Carefully design system and agent instructions to emphasise accessibility, Kenyan context, and safety.

- **Observability and Agent Quality**
  - Add logging plugins to capture prompts, tool calls, and intermediate decisions.
  - Optionally track simple metrics (e.g., number of tools invoked, latency per query).
  - Use at least one small evaluation harness (prompt-based evaluation) to rate answer usefulness and correctness for a set of test scenarios.

- **Agent Evaluation**
  - Create a small synthetic evaluation set: e.g., 10–20 realistic PWD scenarios.
  - Use ADK evaluation patterns to run automatic or semi-automatic checks comparing outputs against expected attributes (e.g., “mentions ramp”, “mentions county name”, “contains clear next steps”).

- **A2A Protocol (optional stretch goal)**
  - Expose the Data and Research Agent as a separate A2A-compatible service.
  - Have the main Navigator agent consume it as a remote `RemoteA2aAgent`, showing how Kenyan NGOs could plug in their own resource catalogues.

- **Agent Deployment (optional bonus)**
  - Package the Navigator as an ADK app suitable for deployment to Vertex AI Agent Engine, following the course’s deployment patterns.

## 6. Data and Tools

Because many Kenyan datasets are not provided via stable APIs, the project will focus on **reproducible local datasets**:

- Sample CSV/Parquet files created for:
  - Public health facilities and social services in a subset of counties (e.g., Nairobi, Kisumu, Mombasa).
  - Simple annotations for accessibility features (presence of ramps, sign-language support, approximate accessibility level).
- These datasets can be:
  - Created manually from public information for the demo.
  - Included in the Kaggle dataset or GitHub repo for easy reuse.

Tools planned:

- Custom tool for filtering and ranking services from the local dataset.
- Google Search tool for enriching a subset of entries with up-to-date information (where allowed).
- Optional MCP/OpenAPI wrappers so that the same logic can be reused if datasets are later exposed through APIs.

## 7. Implementation Plan

At a high level, the implementation will include:

- ADK-based Python agents for intake, research, reasoning, and recommendation.
- A small configuration layer (e.g., Python settings) for counties and service types.
- A notebook or script demonstrating end-to-end flows for several personas.
- Clear logging and comments so other learners can understand how the system is wired together.

The code will be shared either as a **Kaggle Notebook** or a **public GitHub repository**, as required by the Capstone submission guidelines.

## 8. Evaluation Plan

Evaluation will focus on both **user-centric quality** and **technical correctness**:

- Define 10–20 test scenarios (e.g., “Wheelchair user in Nairobi seeking a public clinic”, “Blind user in Kisumu looking for social protection services”).
- For each scenario, run the Navigator and check:
  - Does it find at least one plausible service in the right county?
  - Does the explanation mention relevant accessibility details?
  - Is the language clear and non-stigmatising?

Where possible, simple automatic checks (string or tag-based) will be combined with manual review, and the evaluation harness will be documented in the notebook.

## 9. Risks and Limitations

- **Data completeness:** Real-world accessibility data is limited. For now, the project will rely on illustrative but limited datasets, clearly labelled as such.
- **Changing information:** Service availability and accessibility features can change; static datasets may become outdated without active maintenance.
- **Not a replacement for lived experience:** The Navigator is meant to reduce information barriers, not to replace consultation with PWD organisations or lived expertise.

These limitations will be clearly communicated in the documentation and user messaging.

## 10. Future Extensions

If time allows, future improvements could include:

- Adding more counties and service types (education, employment centres, legal aid).
- Supporting Kiswahili and local languages to widen accessibility.
- Integrating feedback loops where users can rate service accessibility and update the knowledge base.
- Collaborating with Kenyan DPOs and NGOs to refine the scoring logic and datasets.

Overall, this Capstone aims to demonstrate how **agentic systems built with ADK** can support inclusion and accessibility for Kenyan PWDs, while showcasing multiple core concepts from the 5‑Day AI Agents Intensive course.
