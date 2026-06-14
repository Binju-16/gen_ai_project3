import json
import os
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv
import httpx
import openai
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
FALLBACK_DICTIONARY = DATA_DIR / "fallback_dictionary.json"
COURSE_NOTES_FILE = DATA_DIR / "course_notes.json"

openai.api_key = os.getenv("OPENAI_API_KEY", "")
if not openai.api_key:
    print("WARNING: OPENAI_API_KEY is not set. The app will not be able to call the OpenAI API until you set this environment variable.")

app = FastAPI(title="MentorMate AI Companion")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are MentorMate, an AI study assistant designed to help students understand course material clearly and efficiently. "
        "Use the available tools only when they help you answer the user's question with grounded supporting data. "
        "If the user asks for a definition, use the dictionary tool. If the user asks for course-specific examples or explanations, use the notes search tool. "
        "When a tool returns data, incorporate it into your answer and make it explicit which supporting sources you used. "
        "Do not call tools for general conversation or unrelated questions. "
        "Keep your answers helpful, concise, and focused on the user's study goal."
    ),
}

TOOL_DEFINITIONS = [
    {
        "name": "lookup_dictionary_entry",
        "description": "Fetch a precise definition, example usage, and explanation for a study term or concept.",
        "parameters": {
            "type": "object",
            "properties": {
                "word": {
                    "type": "string",
                    "description": "A course term or technical concept to look up.",
                },
                "language": {
                    "type": "string",
                    "description": "The language of the lookup. Use English for this application.",
                    "default": "English",
                },
            },
            "required": ["word"],
        },
    },
    {
        "name": "search_course_notes",
        "description": "Search local course notes and study guidance for relevant explanations or examples.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The topic, concept, or question to search for in course notes.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "The maximum number of note matches to return.",
                    "default": 3,
                },
            },
            "required": ["query"],
        },
    },
]


def load_fallback_dictionary() -> Dict[str, Any]:
    if not FALLBACK_DICTIONARY.exists():
        return {}
    with open(FALLBACK_DICTIONARY, "r", encoding="utf-8") as handle:
        return json.load(handle)


def format_api_dictionary_result(raw_data: Any) -> Dict[str, Any]:
    entries = []
    for item in raw_data:
        word = item.get("word")
        phonetics = ", ".join([p.get("text", "") for p in item.get("phonetics", []) if p.get("text")])
        meanings = []
        for meaning in item.get("meanings", []):
            definitions = []
            for definition in meaning.get("definitions", []):
                definitions.append(
                    {
                        "definition": definition.get("definition"),
                        "example": definition.get("example"),
                        "synonyms": definition.get("synonyms", []),
                    }
                )
            meanings.append(
                {
                    "part_of_speech": meaning.get("partOfSpeech"),
                    "definitions": definitions,
                }
            )
        entries.append(
            {
                "word": word,
                "phonetics": phonetics,
                "meanings": meanings,
            }
        )
    return {"source": "dictionaryapi.dev", "entries": entries}


async def lookup_dictionary_entry(word: str, language: str = "English") -> Dict[str, Any]:
    language = language.strip().lower()
    if language != "english":
        return {
            "word": word,
            "source": "fallback",
            "error": f"Only English lookup is supported. Received language={language}.",
        }

    api_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(api_url)
            response.raise_for_status()
            raw_data = response.json()
            return format_api_dictionary_result(raw_data)
        except Exception:
            fallback = load_fallback_dictionary()
            entry = fallback.get(word.lower())
            if entry:
                return {"source": "fallback", "entries": [entry]}
            return {
                "word": word,
                "source": "none",
                "error": "Definition unavailable in the live dictionary API and the fallback dictionary.",
            }


def load_course_notes() -> Dict[str, Any]:
    if not COURSE_NOTES_FILE.exists():
        return {}
    with open(COURSE_NOTES_FILE, "r", encoding="utf-8") as handle:
        return json.load(handle)


async def search_course_notes(query: str, max_results: int = 3) -> Dict[str, Any]:
    query = query.strip().lower()
    notes = load_course_notes().get("notes", [])
    matches = []
    for note in notes:
        title = note.get("topic", "").lower()
        content = note.get("content", "").lower()
        if query in title or query in content:
            matches.append(note)

    if not matches:
        matches = notes[:max_results]

    return {
        "query": query,
        "source": "course_notes",
        "matches": matches[:max_results],
    }


TOOL_HANDLERS = {
    "lookup_dictionary_entry": lookup_dictionary_entry,
    "search_course_notes": search_course_notes,
}


async def call_openai_chat(messages: list[dict]) -> dict:
    if not openai.api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    response = openai.chat.completions.create(
        model="gpt-4-0613",
        messages=messages,
        functions=TOOL_DEFINITIONS,
        function_call="auto",
        temperature=0.2,
    )
    return response


@app.get("/", response_class=HTMLResponse)
async def root(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/chat")
async def chat_api(request: Request) -> JSONResponse:
    payload = await request.json()
    user_message = payload.get("message", "").strip()
    if not user_message:
        raise HTTPException(status_code=400, detail="Message text is required.")

    messages = [SYSTEM_PROMPT, {"role": "user", "content": user_message}]
    tool_trace = []

    for _ in range(3):
        response = await call_openai_chat(messages)
        choice = response.choices[0]
        message = choice.message

        function_call = message.function_call
        if function_call:
            tool_name = function_call.name
            raw_args = function_call.arguments or "{}"
            try:
                args = json.loads(raw_args)
            except json.JSONDecodeError:
                args = {}

            tool_func = TOOL_HANDLERS.get(tool_name)
            if tool_func:
                tool_result = await tool_func(**args)
            else:
                tool_result = {"error": f"Unknown tool: {tool_name}"}

            tool_trace.append({"tool": tool_name, "args": args, "result": tool_result})
            messages.append(
                {
                    "role": "assistant",
                    "content": None,
                    "function_call": {
                        "name": tool_name,
                        "arguments": json.dumps(args),
                    },
                }
            )
            messages.append(
                {
                    "role": "assistant",
                    "content": json.dumps({"tool": tool_name, "result": tool_result}),
                }
            )
            continue

        assistant_content = message.content or ""
        return JSONResponse({"answer": assistant_content, "tool_trace": tool_trace})

    raise HTTPException(status_code=500, detail="Tool loop exceeded the maximum number of iterations.")
