# Project Overview

# American Express Cross-Channel Journey Stitching Platform

## Vision

This project aims to build a production-inspired Customer Journey Intelligence Platform that unifies customer interactions across multiple channels into a single, continuous customer journey.

Large enterprises such as American Express receive customer interactions from many independent systems:

- Website
- Mobile Application
- Call Centre
- Physical Store
- CRM Systems
- Internal Services

Since these systems operate independently, they have different identifiers, different event formats, and different data stores. As a result, a single customer's journey becomes fragmented across multiple systems.

Our goal is to build a platform that can intelligently combine these fragmented interactions into one unified timeline, analyse customer behaviour, and provide actionable business insights.

This repository is intended to be both:

- A hackathon project
- A portfolio-quality distributed systems project

The architecture should resemble a real production system while remaining lightweight enough to demonstrate end-to-end functionality.

## Problem Statement

If customer data is siloed across channels such as app, website, and phone, it becomes nearly impossible to understand the full customer journey, identify where experiences break down, or intervene before a customer churns or escalates. This platform addresses that problem by building cross-channel identity resolution and event stitching to assemble a unified timeline per customer across app, web, call-center, and in-person touchpoints.

Unified journey visibility enables teams to find and fix the exact moments where the experience fails.

## Reference Tech Stack & Frameworks

The stack remains flexible, but the project is informed by the following reference technologies:

- Frontend: React, Next.js
- Backend and APIs: Node.js, Python (FastAPI)
- Data pipeline and streaming: Apache Kafka, Spark
- Analytics and visualization: Mixpanel, Amplitude, Tableau
- Cloud computing platforms: AWS, GCP
- Database systems: Snowflake, BigQuery, MongoDB

## Core Tasks

- Design an identity resolution algorithm to link a single customer's interactions across app, web, call-center, and in-person channels
- Build a data pipeline to ingest, normalize, and stitch events from all four channels into a unified timeline per customer
- Develop an analyst-facing interface to visualize stitched journeys and highlight drop-off points, escalations, and unresolved issues
- Implement journey analytics logic to surface patterns that correlate with churn, repeat contacts, or poor customer experience
- Test and optimize the platform for identity resolution accuracy, end-to-end data latency, and actionability of insights

## Deliverables

- Project description
- Presentation
- Supporting documentation and project files
- Demo video and project link

## What We Are Building

The platform consists of several logical modules. Each module is intentionally independent so that it can evolve separately in the future.

### 1. Event Simulator

Since we do not have access to real American Express systems, we will build simulators representing different customer touchpoints.

These simulators generate realistic customer events from different channels:

- Website
- Mobile Application
- Call Centre
- Physical Store

The simulator exists only to generate realistic event streams for demonstration purposes.

### 2. Event Streaming Pipeline

All customer interactions should flow through an event streaming system instead of directly communicating with backend services.

The streaming layer represents how modern event-driven architectures process real-time customer events.

Every customer interaction eventually becomes an event flowing through the platform.

### 3. Event Normalization

Different channels generate events in different formats.

The platform should internally convert all incoming events into one common event schema so downstream systems can process them consistently.

The rest of the system should never need to know which channel originally produced the event.

### 4. Graph-Based Identity Resolution

One customer may appear with multiple identifiers across different systems.

Examples include:

- Email
- Phone number
- Customer ID
- Card number
- Device ID
- Cookie ID

The platform should maintain a graph representing relationships between these identifiers.

Whenever a new event arrives, the platform should determine which real customer that event belongs to.

Identity resolution is one of the core components of this project.

### 5. Event Stitching

After identifying the customer, the incoming event should be appended to that customer's unified journey.

Instead of multiple disconnected events, the platform maintains one chronological timeline for each customer.

This creates a complete view of the customer lifecycle across all channels.

### 6. Journey Analytics Engine

Once customer journeys are stitched together, the platform analyses those journeys to discover business insights.

Initially, analytics will be rule-based.

The engine should detect situations such as:

- Repeated payment failures
- Multiple support contacts
- Customer inactivity
- Escalations
- Journey completion
- Customer friction

The analytics engine should remain modular so future machine learning models can be integrated without changing the overall architecture.

### 7. Interactive Dashboard

The dashboard acts as the primary interface for business users.

It should provide visibility into:

- Live incoming events
- Customer timelines
- Identity graph
- Customer analytics
- System health
- Journey insights

The dashboard is expected to demonstrate how analysts would interact with the platform.

## Planned Advanced Features

The following capabilities are planned as future phases of the project. They are part of the overall vision but will not necessarily be implemented during the initial development phases.

### AI Journey Summarizer

Automatically generate concise natural-language summaries describing a customer's complete journey.

### Root Cause Detection

Identify the primary causes behind customer friction, drop-offs, and repeated issues.

### Customer Health Score

Continuously maintain a numerical score representing the overall customer experience.

### Explainable Churn Prediction

Predict customers likely to churn while clearly explaining the events contributing to that prediction.

### Smart Recommendations

Suggest actions that business teams can take to improve customer experience.

Examples include:

- Priority support
- Cashback offers
- Fee waivers
- Loyalty rewards

### Identity Confidence Score

Every identity match should expose a confidence score indicating how certain the platform is about that match.

### Conversation Sentiment Analysis

Analyse customer support conversations to determine customer sentiment and incorporate that information into journey analytics.

### Time-to-Resolution Analytics

Measure how long customer issues take to resolve and expose metrics that help improve operational efficiency.

### AI Analyst Copilot

Allow analysts to ask natural-language questions about customer journeys and receive AI-generated insights.

Examples include:

- Why are Platinum customers churning?
- Which journeys have the highest drop-off?
- What caused today's spike in payment failures?

## Design Philosophy

This project is intentionally designed around a few core principles:

- Event-driven architecture
- Modular services
- Clear separation of concerns
- Extensible system design
- Production-inspired architecture
- Explainable analytics
- Incremental development
- Maintainability over complexity

Every module should have a single responsibility and should be independently testable.

## Long-Term Goal

The objective is not simply to create a hackathon demonstration.

The objective is to build a realistic customer journey intelligence platform that showcases concepts commonly found in modern distributed systems, including:

- Event streaming
- Identity resolution
- Graph algorithms
- Customer journey stitching
- Analytics pipelines
- Real-time dashboards
- AI-assisted business intelligence

By the end of the project, the platform should demonstrate how fragmented customer interactions from multiple systems can be transformed into meaningful, actionable insights for business and customer support teams.
