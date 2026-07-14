# Ask Anything Chatbot

A conversational AI assistant built with LangChain and LangGraph, running on Groq's LLaMA 3.3 70B. It uses a multi-agent pipeline to decide when a question needs live Wikipedia grounding, draft an answer, and have a second agent independently review that answer before it reaches the user.

---

## What it does

- Chat with an LLM through a Streamlit UI, with four switchable personas (General Assistant, Code Helper, Data Science Tutor, Creative Writer)
- **Agentic routing** — a router agent decides whether a question needs real-world/factual grounding (people, places, events, organizations) or can be answered from the model's own knowledge (code, math, creative writing, opinions)
- **Wikipedia tool use** — when the router decides a question is factual, a Wikipedia search runs automatically and its result is injected into the prompt before the answer is generated
- **Critic agent** — after a draft answer is produced, a second agent independently reviews it against the original question (and the Wikipedia context, if used) to check whether it's actually grounded and on-topic
- **Revision loop** — if the critic isn't satisfied, a revise step produces one corrected pass before the answer is shown to the user
- Conversation memory (last 10 exchanges), transcript download, and response time tracking

---

## Architecture: multi-agent pipeline

```
router ──┬── (factual) ──> search ──> answer ──> critic ──┬── approved ──> done
         │                                                  │
         └── (not factual) ─────────────> answer ───────────┴── needs revision ──> revise ──> done
```

Each stage is a distinct agent with its own responsibility:

| Agent | Role |
|---|---|
| **Router** | Decides SEARCH vs ANSWER based on whether the question needs real-world grounding |
| **Search** | Calls the Wikipedia tool and formats the result as context for the answer agent |
| **Answer** | Drafts a response using the persona, conversation history, and (if applicable) Wikipedia context |
| **Critic** | Independently reviews the draft: does it address the question, and is it consistent with the Wikipedia context if one was provided? Replies APPROVE or REVISE with a reason |
| **Revise** | If the critic flags an issue, produces a corrected final answer incorporating that feedback |

This is implemented as a small state graph using **LangGraph**, with conditional edges after the router (search vs. skip) and after the critic (revise vs. finalize). The graph runs once per user message and returns the final answer along with metadata (whether a tool was used, whether a revision happened) that the UI displays as badges under each response.

---

## Tech stack

| Piece | Tool | Why |
|---|---|---|
| LLM | Groq API, LLaMA 3.3 70B | fast inference, generous free tier |
| Orchestration | LangChain + LangGraph | custom LLM wrapper via LangChain's base class; multi-agent state graph via LangGraph |
| UI | Streamlit | fast to build a usable chat interface with session state |
| Tool use | Wikipedia-API | grounding for factual questions, more reliable than the older `wikipedia` package |
| Custom LLM wrapper | `groq_llm.py` (`GroqLLM`) | wraps Groq's chat completions API so it works with LangChain's `invoke()` and LangGraph nodes |

---

## Project structure

```
.
├── app.py            # Streamlit UI, session state, wiring into the agent graph
├── graph.py           # LangGraph multi-agent pipeline: router, search, answer, critic, revise
├── groq_llm.py         # Custom LangChain LLM wrapper around the Groq API
├── tools.py             # Wikipedia search tool used by the search agent
└── requirements.txt
```

---

## Setup

1. **Clone the repo and create a virtual environment**
   ```bash
   git clone <your-repo-url>
   cd llm-powered-conversational-chatbot
   python -m venv venv
   venv\Scripts\activate        # Windows
   # source venv/bin/activate   # macOS/Linux
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**

   Create a `.env` file in the project root:
   ```
   GROQ_API_KEY=your-groq-api-key-here
   ```
   Get a free key from [console.groq.com](https://console.groq.com).

4. **Run the app**
   ```bash
   streamlit run app.py
   ```

5. **Try it out**

   Open the URL Streamlit gives you (usually `http://localhost:8501`). Pick a persona, try one of the suggested questions, or type your own.

---

## What was tested

- Factual questions (e.g. "Who is Alan Turing?") correctly route to the search agent — confirmed via terminal logs showing `[ROUTER] ... -> SEARCH` and the 🔍 badge in the UI
- Non-factual questions (e.g. coding requests) correctly skip search — confirmed via `[ROUTER] ... -> ANSWER`
- Asked about fictional/non-existent people — the model correctly declined to fabricate a biography rather than inventing one, and the critic approved that honest "I don't have information" response
- Manually verified the critic and revise path fire correctly by temporarily tightening the critic's approval threshold, confirming `[CRITIC] REVISE: ...` triggers the revise node and the ✏️ "Revised after critic review" badge appears in the UI
- Confirmed conversation memory correctly carries the last 10 exchanges into new prompts
- Confirmed transcript download produces a readable `.txt` of the full conversation

---

## Possible next steps

- Cache LLM client instances across graph nodes instead of creating a new one per call, to reduce per-message overhead
- Add a second tool (e.g. a calculator or web search beyond Wikipedia) and let the router choose between multiple tools, not just search vs. no-search
- Persist conversation history across sessions instead of resetting on reload
