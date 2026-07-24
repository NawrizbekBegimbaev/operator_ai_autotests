# TOR

# Operator AI

## Terms of Reference (TOR)

**Version:** 0.1 (Draft)

**Project:** Operator AI

**Document Type:** Terms of Reference (TOR)

**Prepared by:** Product Management

**Status:** Draft

---

# 1. Introduction

## 1.1 Purpose

This document defines the business objectives, functional scope, business processes, user roles, integrations, and system requirements for the **Operator AI** platform. It serves as the primary reference for stakeholders, designers, developers, and QA engineers throughout the software development lifecycle.

The purpose of this document is to establish a common understanding of the product vision and ensure that all project participants share the same expectations regarding the system's functionality and behavior.

---

## 1.2 Project Overview

Operator AI is an AI-powered operational platform designed to optimize the daily workflow of call center operators (sales representatives) and provide businesses (ROPs) with intelligent tools for lead management, call analysis, workflow automation, and operator performance evaluation.

The platform integrates with existing CRM and telephony systems to automate repetitive tasks that are traditionally performed manually after customer calls. By leveraging artificial intelligence, Operator AI analyzes call recordings, extracts structured business information, generates concise call summaries, evaluates operator performance, and assists operators in handling subsequent customer interactions more efficiently.

Rather than replacing existing CRM systems, Operator AI extends them by acting as an intelligent operational layer that automates business processes while keeping CRM data synchronized.

---

## 1.3 Business Problem

Organizations relying on outbound sales or customer service operators often encounter several operational challenges:

- Operators spend significant time performing repetitive administrative tasks after each call.
- CRM records require manual updates, increasing the likelihood of inconsistent or incomplete data.
- Managers must manually review call recordings to evaluate operator performance, making quality assurance time-consuming and subjective.
- Valuable customer information discussed during calls is often omitted or inaccurately documented.
- Operators receive limited real-time guidance on improving customer interactions or determining the most appropriate next actions.
- Call prioritization and follow-up activities are managed manually, reducing operational efficiency.

These challenges increase operational costs, reduce productivity, and limit management's ability to maintain consistent service quality.

---

## 1.4 Proposed Solution

Operator AI addresses these challenges by introducing an AI-assisted operational workflow integrated with the organization's existing CRM and telephony infrastructure.

Following each completed call, the system automatically:

- Retrieves the recorded conversation.
- Performs AI-based call analysis.
- Extracts structured lead information.
- Suggests lead status updates.
- Suggests CRM field updates.
- Generates a concise call summary.
- Evaluates operator performance.
- Provides personalized feedback for future improvement.

Before synchronizing any modifications with the CRM, the system presents AI-generated suggestions to the operator for review and confirmation. This human-in-the-loop approach ensures data accuracy while significantly reducing manual effort.

Additionally, Operator AI manages an automated call queue that prioritizes leads according to configurable business rules, enabling operators to focus primarily on customer communication rather than administrative activities.

---

## 1.5 Project Objectives

The primary objectives of Operator AI are:

### Business Objectives

- Reduce manual CRM data entry performed by operators.
- Improve the consistency and quality of lead information.
- Increase operator productivity through workflow automation.
- Enable objective operator performance evaluation using AI.
- Standardize lead processing across organizations.
- Provide business owners with actionable operational insights.

### Operational Objectives

- Automate post-call administrative activities.
- Improve call handling efficiency.
- Reduce human error during CRM updates.
- Assist operators during customer communication.
- Provide intelligent recommendations for future interactions.
- Simplify monitoring of operator activities.

---

## 1.6 Product Scope

The initial release (MVP) includes the following major functional areas:

### Administration

- Super Admin management
- ROP (company) management
- Operator management

### AI Configuration

- Lead analysis rules
- Operator evaluation rules (partial MVP)
- Call queue configuration

### Lead Management

- Lead synchronization with AmoCRM
- AI-generated lead updates
- Lead history
- Call history

### AI Analysis

- Call transcription processing
- Lead information extraction
- Status recommendation
- Form field recommendation
- Call summary generation
- Operator evaluation

### Call Operations

- Automatic call queue
- OnlinePBX integration
- Operator working sessions
- Guideline workflow
- AI confirmation workflow

### Analytics

- Operator work sessions
- Operator performance metrics
- AI evaluation history
- Call history

### Integrations

- AmoCRM
- OnlinePBX

---

## 1.7 Out of Scope (MVP)

The following capabilities are not included in the initial project scope and may be considered in future releases:

- Self-service password recovery
- Advanced operator evaluation rules
- Callback scheduling automation
- Advanced reporting and exports
- Billing and subscription management
- Multi-language AI analysis
- Third-party integrations beyond AmoCRM and OnlinePBX

---

## 1.8 Target Users

The platform supports three primary user roles:

### Super Admin

Responsible for managing organizations (ROPs), configuring integrations, and monitoring platform-wide operator activities.

### ROP (Company)

Responsible for configuring AI behavior, managing operators, reviewing analytics, and monitoring operational performance.

### Operator

Responsible for processing assigned leads, communicating with customers, reviewing AI-generated suggestions, and confirming CRM updates.

---

# 2. Business Process Overview

## 2.1 Current Business Process (As-Is)

Prior to implementing Operator AI, organizations manage customer leads through a combination of AmoCRM, OnlinePBX, and manual operator activities.

The existing workflow is highly dependent on manual actions performed after each customer interaction.

### Current Workflow

1. Customer leads are generated through communication channels such as Instagram and Telegram.
2. New leads are automatically created in AmoCRM.
3. Operators receive assigned leads within AmoCRM.
4. Operators initiate phone calls using the OnlinePBX integration available inside AmoCRM.
5. After each completed call, operators manually:
    - Review the conversation.
    - Determine the appropriate lead status.
    - Update CRM lead fields.
    - Write a summary or notes.
6. The same process is repeated until the lead reaches a final business status.
7. Managers periodically review call recordings manually to evaluate operator performance.
8. Lead processing concludes when the lead is successfully converted or closed.

### Challenges of the Current Process

The current workflow introduces several operational inefficiencies:

- High volume of repetitive manual work after each call.
- Inconsistent CRM data quality due to human error.
- Significant time spent documenting customer interactions.
- Manual quality assurance requiring managers to listen to call recordings.
- Lack of standardized operator evaluation.
- Limited actionable feedback for operators.
- No intelligent prioritization or guidance during daily work.

---

## 2.2 Future Business Process (To-Be)

Operator AI introduces an AI-assisted operational workflow while integrating with existing CRM and telephony systems.

Instead of manually performing administrative tasks after every call, operators review AI-generated recommendations before synchronizing changes with the CRM.

### Future Workflow

1. Customer leads continue to be received through existing channels and synchronized with the CRM.
2. Operator AI retrieves new leads from the CRM.
3. The operator starts a work session.
4. Operator AI automatically selects the next lead according to configured call queue rules.
5. Before each call, the operator is presented with a guideline screen displaying relevant information from previous interactions.
6. The operator communicates with the customer through OnlinePBX.
7. After the call ends:
    - The recording is retrieved.
    - AI analyzes the conversation.
    - AI generates:
        - Suggested lead status
        - Suggested lead field updates
        - Call summary
        - Operator evaluation
8. The operator reviews the AI suggestions.
9. The operator may:
    - Confirm all or selected changes, or
    - Allow them to remain pending for later review.
10. Confirmed changes are synchronized to the CRM, including:
    - Lead status
    - Lead fields
    - Call summary (as a CRM comment)
11. Operator AI automatically prepares the next call according to the configured call queue.
12. The workflow repeats until the operator pauses or ends the work session.

---

## 2.3 Business Value

The future workflow provides measurable improvements over the current process.

### For Operators

- Reduced manual administrative work.
- Faster lead processing.
- AI-assisted decision making.
- Continuous performance feedback.
- Guided preparation before each customer interaction.

### For ROPs (Companies)

- Standardized lead processing.
- Improved CRM data quality.
- Increased operator productivity.
- Objective AI-assisted performance evaluation.
- Centralized operational analytics.

### For Super Admin

- Centralized management of organizations.
- Simplified integration management.
- Cross-organization visibility into operator activities.
- Scalable platform administration.

---

## 2.4 MVP vs Future Vision

### MVP

The initial release integrates with:

- AmoCRM (CRM)
- OnlinePBX (telephony)

Operator AI serves as an intelligent operational layer that augments the existing CRM by automating workflows, analyzing calls, and synchronizing approved updates.

### Future Vision

In future releases, the CRM functionality currently provided by AmoCRM is planned to be replaced with a native Operator AI CRM module. The platform architecture should therefore remain modular and integration-oriented, enabling the CRM component to be replaced without significant changes to the AI analysis engine, call queue, operator workflows, or business rules.

---

# 3. User Roles and Responsibilities

## 3.1 Overview

Operator AI follows a role-based access control (RBAC) model. Each authenticated user is assigned one of three predefined roles with specific permissions and responsibilities.

The three supported roles in the MVP are:

- Super Admin
- ROP (Company)
- Operator

Each role has access only to the functionality required to perform its responsibilities.

---

# 3.2 Super Admin

## Description

The Super Admin is the platform administrator responsible for managing organizations (ROPs), maintaining platform integrations, and overseeing the overall health of the system.

The Super Admin operates at the platform level and has visibility across all organizations.

---

## Responsibilities

- Create and manage ROP accounts.
- Configure external integrations for each ROP.
- Monitor registered operators across all organizations.
- Maintain platform administration.

---

## Permissions

### ROP Management

- Create ROP accounts.
- Update ROP information.
- Delete ROP accounts.
- View all registered ROPs.

### Integration Management

Configure integrations for each ROP:

- AmoCRM
- OnlinePBX

### Operator Monitoring

View information for all operators, including:

- Operator profile
- Call recordings
- Operator activity history

The Super Admin has **read-only** access to operator operational data and cannot modify operator activities.

---

# 3.3 ROP (Company)

## Description

The ROP represents a client organization using Operator AI.

The ROP is responsible for configuring business rules, managing operators, monitoring operational performance, and defining how AI should process customer interactions.

---

## Responsibilities

- Configure AI analysis rules.
- Configure business rules for automatic calling.
- Manage operators.
- Review operator performance.
- Monitor AI-generated insights.
- Review call recordings and analytics.

---

## Permissions

### Rules Configuration

Manage Lead Rules:

- Configure pipeline
- Configure status rules
- Configure lead field rules

Manage Operator Rules *(MVP Partial)*

- Configure sales script

Manage Call Rules

- Configure automatic call order
- Reorder pipeline statuses

---

### Operator Management

- Create operators
- Update operators
- Delete operators
- Reset operator passwords
- View operator profiles
- View operator work sessions
- View operator call history
- View AI feedback

---

### Analytics

Access operator analytics, including:

- Working sessions
- Working hours
- Pause history
- AI evaluation history
- Script compliance
- Call recordings
- Operator statistics

---

# 3.4 Operator

## Description

Operators are responsible for communicating with leads, reviewing AI-generated recommendations, and confirming CRM updates before synchronization.

Their primary responsibility is customer communication rather than manual administrative work.

---

## Responsibilities

- Process assigned leads.
- Handle customer calls.
- Review AI-generated recommendations.
- Confirm or edit AI suggestions.
- Continue daily work through the automated call workflow.

---

## Permissions

### Lead Management

- View assigned leads.
- View lead information.
- View call history.
- View AI-generated summaries.
- View call transcriptions.

---

### Call Operations

- Start working session.
- Pause working session.
- Resume working session.
- End working session.

---

### AI Confirmation

Review AI-generated recommendations, including:

- Suggested lead status
- Suggested lead field updates
- Generated call summary

Operators may:

- Accept recommendations.
- Modify recommendations.
- Leave recommendations pending.

---

### Personal Analytics

View personal:

- AI feedback
- AI evaluation scores
- Script compliance
- Call history

---

# 3.5 Permission Matrix

| Feature | Super Admin | ROP | Operator |
| --- | --- | --- | --- |
| Manage ROPs | ✅ | ❌ | ❌ |
| Configure Integrations | ✅ | ❌ | ❌ |
| Configure Business Rules | ❌ | ✅ | ❌ |
| Manage Operators | Read Only | ✅ | ❌ |
| View All Operators | ✅ | Company Only | ❌ |
| Process Leads | ❌ | ❌ | ✅ |
| Make Calls | ❌ | ❌ | ✅ |
| Review AI Suggestions | ❌ | ❌ | ✅ |
| View Analytics | Platform | Company | Personal |
| View Call Recordings | All | Company | Own |

---

# 4. MVP Scope

---

# 5. Screen structure

- Sitemap

# 6. Future Integrations (Out of Scope for MVP)

The platform architecture should support future integration with additional services, including but not limited to:

- Alternative CRM platforms
- Alternative telephony providers
- Messaging platforms
- Reporting and business intelligence tools
- Third-party APIs

These integrations are outside the scope of the MVP and are not covered by the current requirements.

---

# 7. Glossary

| Term | Definition |
| --- | --- |
| **Operator AI** | The AI-powered platform that automates lead processing, analyzes customer calls, manages operator workflows, and integrates with external CRM and telephony systems. |
| **Super Admin** | Platform administrator responsible for managing ROP accounts, configuring integrations, and monitoring the overall system. |
| **ROP** | A client organization (company) using Operator AI. The ROP configures business rules, manages operators, and monitors operational performance. |
| **Operator** | A user responsible for communicating with leads, processing calls, and confirming AI-generated CRM updates. |
| **Lead** | A potential customer imported from the CRM and assigned to an operator for communication and follow-up. |
| **CRM** | Customer Relationship Management system used to store and manage lead information. During the MVP, AmoCRM serves as the CRM platform. |
| **AmoCRM** | The CRM system integrated with Operator AI during the MVP for lead synchronization and status management. |
| **OnlinePBX** | The telephony platform integrated with Operator AI to initiate outbound calls and provide call recordings for AI analysis. |
| **Call Recording** | The audio recording of a completed conversation between an operator and a customer. |
| **Call Analysis** | The AI process of analyzing a call recording to extract business information, evaluate the operator, and generate recommendations. |
| **Lead Analysis** | The AI process of identifying the most appropriate lead status and extracting values for configured lead form fields. |
| **Operator Evaluation** | The AI-generated assessment of an operator's performance based on the recorded conversation and configured evaluation rules. |
| **Call Summary** | A concise AI-generated overview of the customer conversation that can be synchronized to the CRM as a comment. |
| **Call Transcription** | The text representation of the recorded conversation generated during AI analysis. |
| **Lead Rules** | Configurable business rules that help the AI determine the appropriate lead status and form field values during analysis. |
| **Operator Rules** | Configurable rules used by the AI to evaluate operator performance, such as sales script compliance. |
| **Call Rules** | Configurable business rules that determine the order in which leads are selected for automatic calling. |
| **Automatic Call Queue** | The mechanism that automatically selects the next eligible lead based on the configured call rules. |
| **Guideline Screen** | The screen displayed before each call, presenting previous interaction details and AI-generated context to prepare the operator. |
| **Work Session** | The period between an operator selecting **Start Working** and **End Working**, including pauses and resumed activities. |
| **AI Recommendation** | A set of AI-generated suggestions produced after analyzing a call, including lead status, lead field updates, call summary, and operator evaluation. |
| **Synchronization** | The process of applying confirmed AI-generated updates from Operator AI to the CRM. |
| **Pending Recommendation** | An AI recommendation that has not yet been confirmed by the operator and therefore has not been synchronized with the CRM. |
| **Business Rules** | Configurable rules defined by the ROP that govern AI behavior and automatic call queue processing. |
| **Pipeline** | A sequence of lead statuses in the CRM representing the progression of a lead through the sales process. |
| **Pipeline Status** | A stage within a CRM pipeline indicating the current state of a lead. |
| **Lead Form Field** | A configurable CRM field that stores structured information about a lead, such as preferred branch or preferred appointment date. |
| **Synchronization Status** | The current state of an AI recommendation within Operator AI. Supported statuses include **New**, **Analysis Pending**, **Awaiting Confirmation**, and **Synchronized**. |
| **MVP (Minimum Viable Product)** | The first production release of Operator AI, limited to the agreed functional scope and integrations with AmoCRM and OnlinePBX. |

---