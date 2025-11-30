# Investment Decision Assistant

### *A Multi-Agent System for Behavioral Risk Profiling, Market Sentiment Analysis, and Integrated Investment Insights*

---

## Overview

The **Investment Decision Assistant** is a multi-agent AI system that guides users through three structured stages:

1. **Behavioral Risk Profiling**
2. **Market Sentiment Analysis**
3. **Final Integrated Insight**

The goal is to help individuals understand how their **behavioral tendencies** interact with the **current market environment** of their chosen asset.

This project is built for the **Kaggle × Google AI Agents Intensive (Capstone Project)** and demonstrates:

- Multi-agent architecture
- Sessions & memory
- Tool use (Google Search)
- Context engineering
- Agent-to-agent communication
- FastAPI‑based interface

> **Important:** The system provides **behavioral insights only**, NOT financial advice.

---

## Demo Video

**YouTube Link:** [Watch the Demo](https://youtu.be/m6hHqagYGcE)

This short demo (under 3 minutes) explains:

- the problem the project solves,
- the multi-agent workflow,
- how risk assessment and sentiment analysis interact,
- and a live demonstration of the deployed system at **app.rasam.io**.

---

## Pitch

Many people enter financial markets with good intentions, such as growing their savings or improving their financial situation. But understanding one’s reaction to risk is not always straightforward. People often follow trends, react to social media, or feel motivated by short-term opportunities. This causes their real behavior under pressure to differ from what they _think_ they would do — leading to inconsistent or emotional decisions.

This agent addresses that gap using a three-step process:

1. A structured behavioral risk questionnaire
2. Real-world asset sentiment analysis using reputable financial sources
3. A final integrated insight that shows how the user’s tendencies align with the current market environment

The goal is **self-awareness**, not financial advice.  
The system helps people pause, reflect, and avoid common behavioral mistakes before making decisions.

---

## Problem Statement

People often find it challenging to:

- Clearly understand their own risk tendencies
- Notice how uncertainty and emotion influence their choices
- Interpret market information in a structured and consistent way

The combination often leads to **emotional reactions**, **poor timing**, and **inconsistent decision‑making**.

---

## Solution Summary

The **Investment Decision Assistant** provides:

### **1. Behavioral Risk Profiling**

A structured Q&A process extracts:

- Stated risk style
- Hidden instincts
- Self-awareness indicators
- Behavioral patterns

### **2. Market Sentiment Analysis**

Using the Google Search tool, the system provides:

- Overall sentiment
- 30‑day price movement summary
- Three evidence bullet points
- Cited reputable sources

### **3. Final Integrated Insight**

The Advisor Agent combines:

- Behavioral risk summary
- Sentiment summary

And produces a structured, human‑readable reflection about how the user’s tendencies interact with the market environment.

---

## System Architecture

![System Architecture](images/architecture.jpg)

Flow:

1. **Risk Agent** → generates behavioral summary → stored in memory
2. **Sentiment Agent** → generates sentiment summary → stored in memory
3. **Advisor Agent** → loads both summaries → produces final integrated insight

---

## Project Structure

```
project/
│
├── main.py
├── config.py
├── requirements.txt
├── README.md
│
├── agents/
│   ├── risk_agent.py
│   ├── sentiment_agent.py
│   └── advisor_agent.py
│
├── templates/
│   ├── welcome_page.html
│   ├── risk_page.html
│   ├── sentiment_page.html
│   └── advisor_page.html
│
├── images/
│   ├── welcome_screenshot.jpg
│   ├── risk_screenshot.jpg
│   ├── sentiment_screenshot.jpg
│   └── advisor_screenshot.jpg
```

---

## Key Features Demonstrated

- **Multi-Agent System** (3 sequential agents)
- **Tools** (Google Search)
- **Sessions & Memory** (InMemorySessionService + memory store)
- **Context Engineering** (structured output formats)
- **Deployment-Ready FastAPI App**

---

# Technical Implementation

The system is implemented as a **multi-agent pipeline** using Google’s ADK, FastAPI, and lightweight memory services.

---

## 1. Multi-Agent Architecture

### **Risk Assessor Agent**

- Runs an interactive Q&A
- Produces structured _Behavioral Risk Summary_
- Writes output to memory

### **Market Sentiment Agent**

- Validates asset symbol
- Uses `google_search`
- Produces structured _Sentiment Summary_
- Writes output to memory

### **Advisor Agent**

- Loads Risk + Sentiment summaries
- Produces _Final Integrated Insight Report_
- Outputs a 4‑section structured response

---

## 2. Sessions & Memory

The backend uses:

- `InMemorySessionService` for session continuity
- `InMemoryMemoryService` for saving final summaries
- `session_state_store` as lightweight state

Flow:

1. User sends message
2. Agent processes
3. Final summary saved to memory
4. Advisor retrieves both summaries

---

## 3. UI → Backend → Agent Flow

FastAPI routes:

- `/risk`
- `/sentiment`
- `/advisor`

Frontend:

- Clean HTML/CSS templates
- Fetch‑based communication
- Loading states + transitions

Backend:

- Sends messages to ADK runners
- Agents respond asynchronously
- Results rendered in UI

---

## 4. Tool Usage

The Sentiment Agent uses:

```
google_search
```

to gather real data from trusted financial sources.

Extracted:

- Sentiment label
- 30‑day movement
- Evidence points
- Citations

---

## 5. Final Integration Logic

The Advisor Agent merges:

- Behavioral Risk Summary
- Sentiment Summary

and produces:

1. Behavioral Tendencies
2. Market Environment
3. Interaction Insight
4. Process Reminder

---

# Documentation

## Installation & Setup

```bash
git clone <your-repo-url>
cd investment-decision-assistant
conda create -n agentic python=3.10
conda activate agentic
pip install -r requirements.txt
```

Create `.env`:

```
GOOGLE_API_KEY=your_key_here
```

Run:

```bash
uvicorn main:app --reload
```

Visit:

```
http://127.0.0.1:8000/
```

---

## How to Use the Application

1. Start on the Welcome page
2. Complete the Behavioral Risk Assessment
3. Enter an asset for sentiment analysis
4. Receive the Integrated Insight Report

---

## ☁️ Deployment (Google Compute Engine)

This project includes a fully deployed, publicly accessible version running on **Google Compute Engine (GCE)**.

**Live URL:** https://app.rasam.io

Deployment stack:

- FastAPI backend
- Uvicorn application server
- Nginx reverse proxy
- HTTPS enabled via Certbot

---

# Screenshots

![Welcome Screen](images/welcome_screenshot.jpg)  
![Risk Assessment](images/risk_screenshot.jpg)  
![Market Sentiment](images/sentiment_screenshot.jpg)  
![Advisor Output](images/advisor_screenshot.jpg)

---

# Conclusion

The **Investment Decision Assistant** provides a structured way for users to understand:

- Their behavioral tendencies
- The current market environment
- How the two interact

The project demonstrates core concepts from the Google Agents Intensive:
**multi-agent reasoning, memory, tooling, and context engineering**.

---

# Attribution

Built by **Ras Amirzadeh**  
For the **Kaggle × Google Agents Intensive Capstone (2025)**
