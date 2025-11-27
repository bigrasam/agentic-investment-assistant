from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.templating import Jinja2Templates
from pydantic import BaseModel
import logging

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from google.adk.memory import InMemoryMemoryService


# --- Agents ---
from agents.risk_assessor import risk_assessor
from agents.sentiment_agent import market_state_sentiment_assessor
from agents.advisor_agent import advisor_agent


APP_NAME = "RiskAssessorApp"
DEFAULT_USER_ID = "user_1"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

# ------------------------------------------------------------------------------------
# 1. SHARED SESSION SERVICE (For Conversation History)
# ------------------------------------------------------------------------------------
memory_service = InMemoryMemoryService()
session_service = InMemorySessionService()

# ------------------------------------------------------------------------------------
# 2. SHARED APP STATE STORE (For Summaries)
# ------------------------------------------------------------------------------------
session_state_store = {}


# ------------------------------------------------------------------------------------
# 3. RUNNERS
# ------------------------------------------------------------------------------------
risk_runner = Runner(
    agent=risk_assessor,
    session_service=session_service,
    memory_service=memory_service,
    app_name=APP_NAME,
)

sentiment_runner = Runner(
    agent=market_state_sentiment_assessor,
    session_service=session_service,
    memory_service=memory_service,
    app_name=APP_NAME,
)

advisor_runner = Runner(
    agent=advisor_agent,
    session_service=session_service,
    memory_service=memory_service,
    app_name=APP_NAME,
)


class ChatRequest(BaseModel):
    message: str
    session_id: str


# ====================================================================================
# ROUTES
# ====================================================================================


@app.get("/", response_class=HTMLResponse)
def welcome(request: Request):
    return templates.TemplateResponse("welcome.html", {"request": request})


# --- RISK AGENT ---
# Keep using the base session_id here (it's the first step)


@app.get("/risk", response_class=HTMLResponse)
def chat_page_ui(request: Request):
    return templates.TemplateResponse("risk.html", {"request": request})


@app.post("/risk")
async def chat_with_agent(req: ChatRequest):
    print(f"\nUser ({req.session_id}) > {req.message}")

    try:
        await session_service.create_session(
            app_name=APP_NAME, user_id=DEFAULT_USER_ID, session_id=req.session_id
        )
    except Exception:
        pass

    query_content = types.Content(role="user", parts=[types.Part(text=req.message)])
    agent_response_text = ""

    async for event in risk_runner.run_async(
        user_id=DEFAULT_USER_ID, session_id=req.session_id, new_message=query_content
    ):
        if event.is_final_response() and event.content and event.content.parts:
            text = event.content.parts[0].text
            if text and text != "None":
                agent_response_text += text

    print(f"Risk Agent > {agent_response_text}")

    is_complete = "Risk Assessment Summary" in agent_response_text

    if is_complete:
        if req.session_id not in session_state_store:
            session_state_store[req.session_id] = {}

        session_state_store[req.session_id]["risk_summary"] = agent_response_text
        session = await session_service.get_session(
            app_name=APP_NAME, user_id=DEFAULT_USER_ID, session_id=req.session_id
        )
        await memory_service.add_session_to_memory(session)

        print(f"✅ Risk Summary saved for session {req.session_id}")

    return {"response": agent_response_text, "is_complete": is_complete}


# --- SENTIMENT AGENT ---
# [FIX] Use a UNIQUE session ID for history (req.session_id + "_sentiment")


@app.get("/sentiment", response_class=HTMLResponse)
def sentiment_ui(request: Request):
    return templates.TemplateResponse("sentiment.html", {"request": request})


@app.post("/sentiment")
async def sentiment_agent(req: ChatRequest):
    print(f"\n[Sentiment Agent] User ({req.session_id}) > {req.message}")

    # [CRITICAL FIX] Create a separate history lane for sentiment
    # This prevents the Risk Assessment history from confusing the Sentiment Agent.
    sentiment_history_id = f"{req.session_id}_sentiment"

    try:
        await session_service.create_session(
            app_name=APP_NAME, user_id=DEFAULT_USER_ID, session_id=sentiment_history_id
        )
    except Exception:
        pass

    query_content = types.Content(role="user", parts=[types.Part(text=req.message)])
    agent_response_text = ""

    # Run using the ISOLATED session ID
    async for event in sentiment_runner.run_async(
        user_id=DEFAULT_USER_ID,
        session_id=sentiment_history_id,
        new_message=query_content,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            text = event.content.parts[0].text
            if text and text != "None":
                agent_response_text += text

    print(f"[Sentiment Agent] Response > {agent_response_text}")

    # Save result to the MAIN shared store (using the original ID)
    if req.session_id not in session_state_store:
        session_state_store[req.session_id] = {}

    session_state_store[req.session_id]["sentiment_summary"] = agent_response_text
    session = await session_service.get_session(
        app_name=APP_NAME, user_id=DEFAULT_USER_ID, session_id=sentiment_history_id
    )
    await memory_service.add_session_to_memory(session)
    print(f"✅ Sentiment Summary saved for session {req.session_id}")

    return {"response": agent_response_text, "is_complete": True}


# --- ADVISOR AGENT ---
# [FIX] Use a UNIQUE session ID for history (req.session_id + "_advisor")


@app.post("/advisor")
async def advisor(req: ChatRequest):
    print(f"\n[Advisor Agent] User ({req.session_id}) > {req.message}")

    # [CRITICAL FIX] Isolated history for advisor
    advisor_history_id = f"{req.session_id}_advisor"

    try:
        await session_service.create_session(
            app_name=APP_NAME, user_id=DEFAULT_USER_ID, session_id=advisor_history_id
        )
    except Exception:
        pass

    # Retrieve data from SHARED store
    user_data = session_state_store.get(req.session_id, {})
    risk_data = user_data.get(
        "risk_summary", "Not Available (User skipped risk section)"
    )
    sentiment_data = user_data.get(
        "sentiment_summary", "Not Available (User skipped sentiment section)"
    )

    context_payload = (
        "Generate a coherent final insight combining the user's risk profile and "
        "market sentiment. You may call load_memory() if earlier data is needed.\n\n"
        "--- PROVIDED DATA ---\n"
        f"RISK PROFILE:\n{risk_data}\n\n"
        f"MARKET SENTIMENT:\n{sentiment_data}\n"
    )

    query_content = types.Content(role="user", parts=[types.Part(text=context_payload)])
    agent_response_text = ""

    # Run using the ISOLATED session ID
    async for event in advisor_runner.run_async(
        user_id=DEFAULT_USER_ID,
        session_id=advisor_history_id,
        new_message=query_content,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            part_text = event.content.parts[0].text
            if part_text and part_text != "None":
                agent_response_text += part_text

    print(f"[Advisor Agent] Response > {agent_response_text}")

    is_complete = "ADVISOR_SUMMARY" in agent_response_text

    return {"response": agent_response_text, "is_complete": is_complete}


@app.get("/advisor", response_class=HTMLResponse)
def advisor_ui(request: Request):
    return templates.TemplateResponse("advisor.html", {"request": request})
