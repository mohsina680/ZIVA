# Future Process Model — NPCC
## Data Institutionalization Project: Big Data Solution

**Central Power Purchasing Agency (Market Operator)**  
**Collaborator:** IBL-Unisys

---

## 1. Document Information

| Field | Details |
| :--- | :--- |
| **Project Name** | Data Institutionalization Project - Big Data Solution[cite: 1] |
| **Document Name** | Future Process Model - NPCC[cite: 1] |
| **Document Scope** | NPCC source data acquisition, secured ingestion, mapping, storage, and publication to CPPA enterprise data platform[cite: 1] |
| **Source Entity** | NPCC (National Power Control Center)[cite: 1] |
| **Use Case** | API-to-DB integration for NPCC scheduling and pricing data feeds[cite: 1] |

---

## 2. Process Flow Overview

### 2.1 AS-IS Process Flow (Source: NPCC)
The AS-IS model shows NPCC SDXP as the external source, CPPA-initiated API pulls, mapping logic, and direct loading into `MMS_PRODDB` target tables[cite: 1].

### 2.2 TO-BE Future Process Model
The TO-BE model shows the same NPCC business feeds moving through a governed ingestion and orchestration layer before publication to the CPPA Enterprise Data Lake storage layer[cite: 1].

---

## 3. Key Process Improvements

The table below summarizes the principal shifts from the AS-IS model to the future TO-BE process. The delta is expressed in business process terms and is aligned with the AS-IS and TO-BE architectures[cite: 1].

| Change Area | AS-IS Position | TO-BE Position | Change Reflected |
| :--- | :--- | :--- | :--- |
| **Source Handling** | NPCC SDXP exposes a token endpoint and five JSON-based data APIs consumed directly by CPPA[cite: 1]. | The five NPCC feeds are represented as secured, governed source feeds for controlled acquisition[cite: 1]. | Source access becomes feed-level controlled while preserving the same business feed scope[cite: 1]. |
| **Authentication** | Bearer token request over HTTPS with IP binding is used before daily data pull[cite: 1]. | Encrypted, mutually authenticated feeds with centrally managed credentials are introduced[cite: 1]. | Credential handling moves from connection-level access to governed enterprise credential control[cite: 1]. |
| **Triggering** | Daily scheduler initiates the CPPA pull at 06:00[cite: 1]. | Enterprise orchestration manages schedule, workflow task triggers, retry, and logging[cite: 1]. | Execution becomes workflow-controlled, traceable, and retry-capable[cite: 1]. |
| **Ingestion** | API pull engine performs HTTPS GET calls and passes JSON responses to mapping logic[cite: 1]. | Automated ingestion service uses a common connector pattern for all five NPCC feeds[cite: 1]. | Ingestion becomes standardized and reusable instead of feed-specific pull handling[cite: 1]. |
| **Mapping** | JSON responses are parsed into availability, price, increased generation, decreased generation, and must-run mappings[cite: 1]. | The same feed-level mappings continue inside a governed pipeline before curated publication[cite: 1]. | Business mapping is retained, but processing is controlled through a future-state data pipeline[cite: 1]. |
| **Storage** | Mapped data is loaded directly into `MMS_PRODDB` tables on MS SQL Server[cite: 1]. | Validated data is published through an enterprise data lake storage layer using open table format[cite: 1]. | Storage shifts from direct database loading to governed data platform publication[cite: 1]. |
| **Monitoring** | Operational monitoring, retry behavior, and audit logging are not shown as formal process capabilities[cite: 1]. | Pipeline monitoring, execution logs, retry status, and record-level run logs are included[cite: 1]. | Failures, execution state, and publication outcome become visible and supportable[cite: 1]. |

---

## 4. Change Scope

The table below maps each process area across the current and future model, with the key change or improvement identified[cite: 1].

| Process Area | Current Process Model | Future Process Model | Key Change / Improvement |
| :--- | :--- | :--- | :--- |
| **Data Source** | NPCC SDXP platform exposes operational scheduling and pricing data through API endpoints[cite: 1]. | NPCC remains the source system, but the source outputs are formalized as secured business feeds[cite: 1]. | Clarifies source ownership and converts API consumption into governed feed acquisition[cite: 1]. |
| **Feed Coverage** | Five feeds are pulled: Generation Availability, Marginal Price, Increased Generation, Decreased Generation, and Must-Run Generation[cite: 1]. | The same five feeds are retained as secured feeds and processed through a common ingestion pipeline[cite: 1]. | No business feed is removed; the process control model changes[cite: 1]. |
| **Data Acquisition**| CPPA performs daily HTTPS GET calls after token generation[cite: 1]. | Automated ingestion service performs controlled secure pulls under orchestration[cite: 1]. | Reduces dependency on ad-hoc pull execution and improves repeatability[cite: 1]. |
| **Scheduling** | A daily 06:00 scheduler initiates token and feed collection[cite: 1]. | Enterprise orchestration controls the schedule, sequencing, retry, and execution logging[cite: 1]. | Improves operational control over timing, dependencies, and failure recovery[cite: 1]. |
| **Parsing & Mapping**| Mapping is handled for each JSON feed before loading the relevant MMS table[cite: 1]. | Parsing and mapping continue by feed but are executed inside a governed pipeline[cite: 1]. | Preserves the target data meaning while improving governance and control[cite: 1]. |
| **Validation** | The AS-IS diagram identifies validation rules as not defined for the feed mappings[cite: 1]. | The future process introduces quality-gate readiness; detailed validation rules remain to be finalized before enforcement[cite: 1]. | Makes validation a production readiness requirement rather than an undocumented gap[cite: 1]. |
| **Storage & Publication**| Data is loaded into `MMS_PRODDB` tables for downstream operational use[cite: 1]. | Data is stored in the enterprise data lake and published as curated settlement-grade data products[cite: 1]. | Moves the process from direct database loading to governed publication[cite: 1]. |
| **Exception Handling**| Failure handling and operational audit are not formally represented[cite: 1]. | Retry, failure notification, run logging, and replay/backfill support are introduced[cite: 1]. | Improves traceability, recovery, and production support[cite: 1]. |

---

## 5. Change Logistics

Maps each process element to its AS-IS and TO-BE configuration across systems, feeds, authentication, scheduling, and output targets[cite: 1].

| Area | AS-IS | TO-BE |
| :--- | :--- | :--- |
| **Source System** | NPCC SDXP platform[cite: 1] | NPCC SDXP platform[cite: 1] |
| **Source Location** | NPCC Data Center, Islamabad, Pakistan[cite: 1] | NPCC Data Center, Islamabad, Pakistan[cite: 1] |
| **Access Pattern** | CPPA-initiated API pull after token request[cite: 1] | Governed secure acquisition through enterprise ingestion service[cite: 1] |
| **Authentication** | Bearer token + IP binding over HTTPS 443[cite: 1] | Encrypted transport, mutual authentication, and centrally managed credentials[cite: 1] |
| **Schedule** | Daily pull at 06:00[cite: 1] | Daily orchestration with retry, logging, and date-window support[cite: 1] |
| **Availability Feed** | GET generation availability; target `mtavailabilitydata`[cite: 1] | Secured Generation Availability feed; target `mtavailabilitydata`[cite: 1] |
| **Marginal Price Feed**| GET marginal price report; target `MtMarginalPrice`[cite: 1] | Secured Marginal Price feed; target `MtMarginalPrice`[cite: 1] |
| **Increased Gen Feed** | GET increased generation; target `MtAsclG`[cite: 1] | Secured Increased Generation feed; target `MtAsclG`[cite: 1] |
| **Decreased Gen Feed** | GET decreased generation; target `MtAscRG`[cite: 1] | Secured Decreased Generation feed; target `MtAscRG`[cite: 1] |
| **Must-Run Gen Feed** | GET must-run generation; target `MtMustRunGen`[cite: 1] | Secured Must-Run Generation feed; target `MtMustRunGen`[cite: 1] |
| **Current Target** | `MMS_PRODDB` - MS SQL Server[cite: 1] | No longer treated as the only process endpoint in the future-state view[cite: 1] |
| **Future Target** | Not applicable[cite: 1] | CPPA Enterprise Data Lake storage layer using open table format[cite: 1] |
| **Primary Output** | Database records for MMS operational usage[cite: 1] | Curated NPCC scheduling and pricing data products for market operations[cite: 1] |

---

## 6. Risks & Mitigation

Risks identified during the AS-IS review and their respective treatments in the future process model[cite: 1].

> ### ⚠️ Validation Rules
> * **Risk / Gap:** The AS-IS mapping boxes show that validation rules are not defined[cite: 1].
> * **Future Process Treatment:** Field-level validation rules and quality gates should be finalized before production enforcement[cite: 1].

> ### 🔑 Credential Exposure
> * **Risk / Gap:** Bearer token handling, cookies, and connection credentials are part of the current access pattern[cite: 1].
> * **Future Process Treatment:** Centrally managed credentials remove secrets from code, documents, and local scripts[cite: 1].

> ### ⏱️ Fixed Pull Window
> * **Risk / Gap:** A fixed daily 06:00 pull can miss delayed, corrected, or backfilled source data[cite: 1].
> * **Future Process Treatment:** Date-window parameterization, incremental acquisition, and replay support reduce missed-data risk[cite: 1].

> ### 👁️ Failure Visibility
> * **Risk / Gap:** Failure notification, retry status, and operational audit are not formalized in the AS-IS flow[cite: 1].
> * **Future Process Treatment:** Pipeline monitoring, run logging, alerts, and retry handling improve operational visibility[cite: 1].

> ### 🗄️ Direct Database Dependency
> * **Risk / Gap:** Direct loading into `MMS_PRODDB` makes the database the primary process endpoint[cite: 1].
> * **Future Process Treatment:** Data lake publication introduces a governed storage layer before downstream consumption[cite: 1].

> ### 📊 Feed Layout Change
> * **Risk / Gap:** Changes in NPCC JSON structure may affect mapping into the five target tables[cite: 1].
> * **Future Process Treatment:** Schema monitoring, versioned mappings, and exception handling should be applied[cite: 1].

> ### 🔄 Data Completeness
> * **Risk / Gap:** Late or corrected scheduling/pricing values may require manual recovery in the current model[cite: 1].
> * **Future Process Treatment:** Controlled reprocessing and backfill logic support recovery without uncontrolled duplicate publication[cite: 1].

---

## 7. Document Signoff

**Dated:** _______________

```text
_____________________               _____________________               _____________________
Name:                               Mr. Salman Zahid                    Mr. Farrukh SALEEM
Designation:                        Manager                             Manager
                                    (Service Owner)                     (Project Manager – IBL UNISYS)