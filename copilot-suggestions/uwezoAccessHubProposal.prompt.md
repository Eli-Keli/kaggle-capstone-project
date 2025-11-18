# Uwezo Access Hub: AI Agents for Digital Inclusion in Kenya
## Kaggle Capstone Project - Agents for Good Track

---

## Executive Summary

**Uwezo** (Swahili for "capability" or "ability") Access Hub is a multi-agent AI system designed to bridge the digital accessibility gap for Persons with Disabilities (PWDs) in Kenya. With over 2.2 million PWDs in Kenya facing significant barriers to education, employment, and digital services, Uwezo provides personalized, context-aware assistance that adapts to individual accessibility needs while respecting local context, language, and infrastructure constraints.

**Track:** Agents for Good  
**Primary Impact Areas:** Education, Employment, Digital Inclusion  
**Target Users:** Kenyan PWDs with visual, hearing, mobility, and cognitive impairments  
**Alignment with SDGs:** SDG 4 (Quality Education), SDG 8 (Decent Work), SDG 10 (Reduced Inequalities)

---

## The Problem

### Digital Exclusion in Kenya

Kenya's PWDs face compounded challenges:

1. **Education Gap:** Only 27% of children with disabilities attend school vs. 82% of children without disabilities
2. **Employment Barrier:** 60%+ unemployment rate among PWDs vs. 40% national average
3. **Digital Divide:** Most digital services lack accessibility features (screen reader compatibility, sign language support, simplified interfaces)
4. **Infrastructure Constraints:** Limited internet, expensive smartphones, reliance on USSD/SMS in rural areas
5. **Language Barriers:** Content primarily in English, limited Swahili accessibility resources
6. **Awareness Gap:** Many PWDs unaware of available resources, support programs, and rights

### Existing Solutions Fall Short

- International accessibility tools not localized for Kenyan context
- Expensive solutions beyond reach of most PWDs (avg. income <$2/day)
- No integration with local systems (M-PESA, NHIF, NSSF, HELB)
- Lack of Kenyan Sign Language (KSL) support
- No consideration for feature phone users

---

## The Solution: Uwezo Access Hub

A sophisticated multi-agent system powered by Google's Agent Development Kit (ADK) that provides:

### Core Agent Architecture

#### 1. **Visual Assistance Agent** (Sequential)
**Purpose:** Supports users with visual impairments

**Capabilities:**
- Describes images, documents, and web content using Gemini's vision capabilities
- Reads text aloud in Swahili or English
- Provides navigation guidance through digital interfaces
- Identifies colors, objects, and text in images (important for form-filling, ID cards)

**Tools:**
- Gemini 2.5 Flash with vision
- Custom text-to-speech tool (Swahili + English)
- Google Search for context-aware information
- MCP integration for document processing

**Workflow:**
```
User uploads image → Vision Agent analyzes → Extracts text/objects → 
Provides description in user's preferred language → Offers to read aloud → 
Saves description to memory for future reference
```

---

#### 2. **Opportunity Matcher Agent** (Parallel + Sequential)
**Purpose:** Connects PWDs with education and employment opportunities

**Sub-Agents (Parallel):**

**a) Job Matcher**
- Searches for PWD-friendly job postings
- Analyzes accessibility of workplaces
- Matches user skills with opportunities
- Provides application assistance

**b) Education Navigator**
- Finds accessible schools, universities, courses
- Identifies scholarship opportunities
- Checks HELB (Higher Education Loans Board) eligibility
- Provides application guidance

**c) Resource Connector**
- Locates disability support organizations
- Finds government assistance programs
- Identifies NGO support services
- Connects to assistive technology providers

**Tools:**
- Google Search for real-time job/education listings
- Custom web scraper for Kenyan job boards (BrighterMonday, LinkedIn Kenya)
- Database for local organizations (NCPWD, KNAD, KAIH)
- Code execution for skills matching algorithms
- Long-running operations for application submission

**Workflow:**
```
User provides profile (skills, needs, location) → 
Parallel agents search (jobs, education, resources) → 
Aggregator combines results → 
Ranking based on accessibility + relevance → 
Provides top recommendations with application steps
```

---

#### 3. **Accessibility Advisor Agent** (Loop with Human-in-the-Loop)
**Purpose:** Provides personalized advice and advocacy support

**Capabilities:**
- Explains disability rights under Kenya's Persons with Disabilities Act 2003
- Advises on workplace accommodations
- Helps draft accommodation requests
- Provides advocacy guidance
- Connects to legal aid if needed

**Tools:**
- Knowledge base of Kenyan disability law
- Custom tool for generating accommodation letters
- Memory service for user's accommodation history
- Long-running operation for human expert review (pause/resume)

**Workflow (Loop):**
```
User describes situation → 
Agent provides initial advice → 
User feedback on advice → 
Agent refines (loop) → 
If complex: pause for human expert review → 
Resume with expert input → 
Generate action plan → 
Store in memory for follow-up
```

---

#### 4. **Communication Bridge Agent** (A2A Integration)
**Purpose:** Facilitates accessible communication

**Capabilities:**
- Converts text to simplified Swahili/English
- Provides Kenyan Sign Language (KSL) guidance via text descriptions
- Generates communication boards for non-verbal users
- Translates technical/government language to plain language

**Tools:**
- Gemini for language simplification
- Custom KSL dictionary tool
- MCP for image generation (communication symbols)
- A2A protocol to connect with external translation services

**Workflow:**
```
User inputs complex text/document → 
Agent analyzes complexity → 
Simplifies language → 
Offers KSL guidance if requested → 
Generates visual aids if needed → 
User can request clarification (loop)
```

---

#### 5. **Personal Assistant Agent** (Coordinator/Orchestrator)
**Purpose:** Central coordinator that manages user interactions and delegates to specialized agents

**Capabilities:**
- Understands user intent from natural language
- Routes requests to appropriate specialized agents
- Maintains conversation context
- Learns user preferences over time
- Provides proactive suggestions

**Tools:**
- Session management (DatabaseSessionService for persistence)
- Memory service (long-term user preferences, history)
- Context compaction for efficient context management
- AgentTool wrappers for all sub-agents

**Workflow:**
```
User query → Personal Assistant analyzes intent → 
Determines which agents needed → 
Delegates to agents (sequential or parallel) → 
Synthesizes responses → 
Provides unified answer → 
Stores interaction in memory
```

---

### Technical Architecture

#### Multi-Agent Orchestration
```
┌─────────────────────────────────────────┐
│    Personal Assistant Agent (Root)      │
│         (LlmAgent + Orchestrator)       │
└──────────────┬──────────────────────────┘
               │
     ┌─────────┴─────────┬─────────────┬──────────────┬──────────────┐
     │                   │             │              │              │
┌────▼────┐      ┌──────▼──────┐  ┌──▼───────┐  ┌───▼─────┐  ┌────▼──────┐
│ Visual  │      │ Opportunity  │  │Accessibi-│  │  Comms  │  │  Session  │
│Assistant│      │   Matcher    │  │  lity    │  │ Bridge  │  │  Memory   │
│ Agent   │      │   (Parallel) │  │  Advisor │  │  Agent  │  │  Service  │
└─────────┘      └──────┬───────┘  │ (Loop)   │  │  (A2A)  │  └───────────┘
                        │          └──────────┘  └─────────┘
              ┌─────────┼─────────┐
              │         │         │
         ┌────▼───┐ ┌──▼────┐ ┌─▼────────┐
         │  Job   │ │  Edu  │ │Resource  │
         │Matcher │ │  Nav  │ │Connector │
         └────────┘ └───────┘ └──────────┘
```

#### Key Technical Components

**1. Agents:**
- **LlmAgent** for all agents (Gemini 2.5 Flash)
- **SequentialAgent** for multi-step workflows
- **ParallelAgent** for simultaneous information gathering
- **LoopAgent** for iterative refinement with feedback

**2. Tools:**
- **Custom Tools:** 
  - KSL dictionary lookup
  - M-PESA integration (future: bill payments, donations)
  - Kenyan organizations database
  - Text-to-speech (Swahili/English)
  - Web scrapers for local job boards
  
- **MCP Tools:**
  - Document processing (PDFs, images)
  - File system access for user documents
  
- **Built-in Tools:**
  - Google Search for real-time information
  - Code Execution for data processing/matching algorithms

- **Long-running Operations:**
  - Job applications (pause for document upload)
  - Expert consultation (pause for human review)

**3. State Management:**
- **Sessions:** DatabaseSessionService (SQLite) for conversation persistence
- **Memory:** InMemoryMemoryService for user preferences, history, accessibility needs
- **Context Engineering:** Events compaction to manage long conversations efficiently

**4. Observability:**
- **LoggingPlugin** for comprehensive debugging
- Custom metrics for accessibility features usage
- User feedback collection for continuous improvement

**5. A2A Integration:**
- Communication Bridge Agent exposed via A2A protocol
- Potential integration with external KSL video generation service
- Future: Connect with government service APIs

**6. Deployment:**
- Cloud deployment on Vertex AI Agent Engine
- Scalable architecture (min 0, max 5 instances)
- API endpoints for mobile app integration

---

### Key Concepts Demonstrated (7+)

✅ **1. Multi-Agent System:**
- Sequential Agents (Visual Assistant workflow)
- Parallel Agents (Opportunity Matcher sub-agents)
- Loop Agents (Accessibility Advisor with feedback)
- Agent coordination via Personal Assistant

✅ **2. Comprehensive Tool Usage:**
- Custom tools (KSL dictionary, M-PESA, web scrapers)
- MCP integration (document processing)
- Built-in tools (Google Search, Code Execution)
- Long-running operations (applications, expert review)

✅ **3. Sessions & Memory:**
- DatabaseSessionService for persistence
- InMemoryMemoryService for user preferences
- load_memory tool for retrieving past interactions

✅ **4. Context Engineering:**
- Events compaction for long conversations
- Strategic context window management
- User profile summarization

✅ **5. Observability:**
- LoggingPlugin for all agents
- Custom metrics tracking
- Error handling and debugging

✅ **6. A2A Protocol:**
- Communication Bridge Agent as A2A service
- Agent card generation
- Inter-agent communication

✅ **7. Agent Deployment:**
- Cloud deployment configuration
- Production-ready architecture
- Scalability considerations

---

## Implementation Plan

### Phase 1: Core Infrastructure (Week 1)
- [ ] Set up ADK environment
- [ ] Implement Personal Assistant (root agent)
- [ ] Create session and memory services
- [ ] Build basic custom tools (database access)
- [ ] Implement observability (LoggingPlugin)

### Phase 2: Specialized Agents (Week 2)
- [ ] Visual Assistant Agent with vision capabilities
- [ ] Opportunity Matcher with parallel sub-agents
- [ ] Basic job/education matching algorithms
- [ ] Google Search integration
- [ ] Testing and debugging

### Phase 3: Advanced Features (Week 3)
- [ ] Accessibility Advisor with loop + human-in-loop
- [ ] Communication Bridge Agent
- [ ] MCP integration for documents
- [ ] Long-running operations
- [ ] Memory consolidation

### Phase 4: A2A & Deployment (Week 4)
- [ ] Expose Communication Bridge via A2A
- [ ] Agent evaluation metrics
- [ ] Cloud deployment
- [ ] Documentation
- [ ] Demo video creation

### Phase 5: Polish & Submission (Week 5)
- [ ] User testing with PWD community
- [ ] Refinement based on feedback
- [ ] Comprehensive documentation
- [ ] Submission materials (writeup, video)

---

## Evaluation Criteria Alignment

### Category 1: The Pitch (30 points)

**Problem Statement (10 pts):**
- Clear articulation of digital exclusion faced by Kenyan PWDs
- Quantified impact (2.2M PWDs, 60%+ unemployment)
- Personal stories from user research

**Solution Innovation (10 pts):**
- Novel multi-agent approach to accessibility
- Local context awareness (Swahili, KSL, M-PESA)
- Comprehensive coverage (education, employment, communication)

**Impact Potential (10 pts):**
- Direct benefit to 2.2M+ Kenyan PWDs
- Scalable to other African countries
- Alignment with 3 SDGs
- Measurable outcomes (job placements, school enrollments)

### Category 2: The Implementation (70 points)

**Technical Complexity (20 pts):**
- 5 specialized agents with different patterns
- 7+ key concepts demonstrated
- Advanced features (A2A, long-running ops, MCP)

**Code Quality (20 pts):**
- Well-structured agent architecture
- Comprehensive error handling
- Extensive documentation
- Clean, readable code following best practices

**Functionality (20 pts):**
- All core features operational
- Robust tool integration
- Effective state management
- Reliable performance

**Innovation (10 pts):**
- Creative use of ADK features
- Novel accessibility solutions
- Kenyan context adaptation

### Bonus Points (20 points potential)

**Deployment (5 pts):**
- Cloud deployment on Vertex AI Agent Engine
- Production-ready configuration

**Agent Evaluation (5 pts):**
- Evaluation metrics for accuracy
- User feedback integration
- Performance benchmarks

**Additional Features (10 pts):**
- Mobile app prototype
- USSD/SMS fallback for feature phones
- Community partnerships (NCPWD, KNAD)
- User testimonials

---

## Expected Outcomes & Impact

### Immediate Impact (3-6 months)
- **100+** PWDs onboarded and actively using the system
- **50+** job/education opportunities matched
- **200+** accessibility questions answered
- **10+** successful job/school placements

### Medium-term Impact (6-12 months)
- **1,000+** active users across Kenya
- **500+** successful matches (jobs, schools, resources)
- Partnership with 5+ disability organizations
- Integration with government services (eCitizen)

### Long-term Impact (1-3 years)
- **10,000+** users across East Africa
- Expansion to other African countries
- Influence policy for digital accessibility standards
- Become reference implementation for accessible AI systems

### Measurable Metrics
- User engagement (DAU, session length)
- Match success rate (job placements, enrollments)
- User satisfaction (NPS score >50)
- Accessibility compliance (WCAG 2.1 AA standard)
- Cost savings for users (reduced middleman fees)

---

## Sustainability & Scalability

### Technical Scalability
- Cloud-native architecture
- Auto-scaling (0-5 instances)
- Efficient context management
- Modular agent design

### Financial Sustainability
- Freemium model (basic free, premium features)
- B2B partnerships (companies seeking to hire PWDs)
- Grant funding from accessibility-focused organizations
- Government contracts for public service delivery

### Community Engagement
- Open-source core components
- Community feedback loops
- PWD advisory board
- Local language volunteers (KSL experts)

### Expansion Strategy
- Phase 1: Nairobi and major cities
- Phase 2: All Kenyan counties
- Phase 3: East Africa (Uganda, Tanzania, Rwanda)
- Phase 4: Pan-African expansion

---

## Risk Mitigation

### Technical Risks
- **LLM hallucinations:** Implement verification layers, human-in-loop for critical decisions
- **API costs:** Optimize context, use caching, implement rate limiting
- **Data privacy:** End-to-end encryption, GDPR/Kenya Data Protection Act compliance
- **Offline access:** Develop USSD/SMS fallback, offline mode

### User Adoption Risks
- **Digital literacy:** Simple UI, voice interface, training workshops
- **Trust:** Partnerships with trusted disability organizations
- **Accessibility of the tool itself:** Rigorous accessibility testing with PWDs
- **Language barriers:** Swahili support, simplified language, KSL integration

### Operational Risks
- **Maintenance:** Automated monitoring, comprehensive logging
- **Scaling costs:** Efficient architecture, grant funding
- **Data updates:** Web scraping automation, community contributions
- **Regulatory:** Proactive compliance with disability and data laws

---

## Team & Resources

### Development Team (Proposed)
- **Lead Developer:** AI/ML expertise, ADK proficiency
- **Accessibility Expert:** PWD community member, UX specialist
- **Kenyan Context Advisor:** Local partner, understands systems/culture
- **Testing Team:** PWDs with diverse disabilities

### Resources Needed
- Google Cloud credits for deployment
- Access to Kenyan disability organizations
- KSL expert consultation
- User testing participants (PWDs)

### Timeline
- **Total:** 5 weeks
- **Code Completion:** Week 4
- **Testing & Refinement:** Week 5
- **Submission:** December 1, 2025

---

## Conclusion

Uwezo Access Hub represents a paradigm shift in how AI can serve marginalized communities in African contexts. By combining cutting-edge multi-agent technology with deep local understanding, we can create truly inclusive digital experiences that empower rather than exclude.

This project demonstrates not just technical excellence, but a commitment to using AI as a force for social good—turning the promise of "AI for everyone" into reality for Kenya's 2.2 million persons with disabilities.

**Uwezo** means capability. This project proves that with the right tools, thoughtful design, and genuine empathy, we can unlock the full capability of every person, regardless of their physical or cognitive differences.

---

## Appendices

### Appendix A: Kenyan PWD Statistics
- Total PWDs: 2,215,000 (Census 2019)
- Visual impairment: 32%
- Hearing impairment: 18%
- Physical disability: 28%
- Cognitive disability: 22%

### Appendix B: Key Kenyan Organizations
- NCPWD (National Council for Persons with Disabilities)
- KNAD (Kenya National Association of the Deaf)
- KAIH (Kenya Association for the Intellectually Handicapped)
- KUHP (Kenya Union of the Blind)

### Appendix C: Relevant Kenyan Laws
- Persons with Disabilities Act 2003
- Kenya Data Protection Act 2019
- Constitution of Kenya 2010 (Article 54)

### Appendix D: Technology Stack
- **LLM:** Gemini 2.5 Flash
- **Framework:** Google ADK (Python)
- **Database:** SQLite → PostgreSQL (production)
- **Deployment:** Vertex AI Agent Engine
- **Monitoring:** Google Cloud Logging
- **Version Control:** GitHub

### Appendix E: Sample Interactions
*(See separate document with detailed conversation flows)*

---

**Project Name:** Uwezo Access Hub  
**Track:** Agents for Good  
**Submission Date:** December 1, 2025  
**Contact:** [Your details]  
**Repository:** [GitHub link to be added]  
**Demo Video:** [YouTube link to be added]

---

*"Technology should adapt to people, not the other way around. Uwezo Access Hub ensures that AI serves everyone, especially those who need it most."*
