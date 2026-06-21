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
    print("WARNING: OPENAI_API_KEY is not set.")

app = FastAPI(title="MentorMate AI Companion")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are MentorMate, an agentic AI study companion for students across academic subjects. "
        "Your job is to help students understand concepts, prepare for exams, summarize study material, "
        "generate practice questions, create study guides, and build study plans. "

        "Use tools when they genuinely help the user: lookup_term for definitions, "
        "search_course_notes for available course-specific context, build_study_plan for study schedules, "
        "and generate_practice_quiz for practice questions, quizzes, self-testing, or exam practice. "

        "The model decides whether a tool is needed and which tool to use. "
        "Do not force a tool if the user simply needs a clear explanation that can be answered directly. "

        "For academic explanations, provide a clear student-friendly answer even if no course note is available. "
        "If course notes are available and relevant, use them to ground the answer. "
        "If course notes are not available, answer using general academic knowledge and make the explanation easy to understand. "

        "For complete study guides, include an explanation, key points, examples, practice questions, "
        "and a quick review checklist when appropriate. "

        "For study plans, use build_study_plan only when the user clearly asks for a schedule, deadline, sessions, "
        "or exam preparation timeline. "

        "If a tool returns found=false, no matches, no useful data, or an error, do not mention tool failure "
        "or expose internal tool behavior. Never say 'the lookup tool did not find', 'tool failed', or "
        "'dictionary unavailable'. Instead, continue with the best helpful academic explanation. "

        "Keep answers clear, supportive, accurate, and study-focused."
    ),
}

TOOL_DEFINITIONS = [
    {
        "name": "lookup_term",
        "description": "Look up a term in a dictionary or fallback glossary when the user asks for a precise definition.",
        "parameters": {
            "type": "object",
            "properties": {
                "term": {
                    "type": "string",
                    "description": "The study term or concept to define.",
                },
                "language": {
                    "type": "string",
                    "description": "The language for the definition lookup. Use English.",
                    "default": "English",
                },
            },
            "required": ["term"],
        },
    },
    {
        "name": "search_course_notes",
        "description": (
            "Search local course notes for available class topics, examples, and grounded course context. "
            "Use this when the user asks about course-related material, summaries, comparisons, or study guides."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The academic topic or course concept to search for.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of matching notes to return.",
                    "default": 3,
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "build_study_plan",
        "description": (
            "Create a structured study schedule based on topics, deadlines, and available study hours. "
            "Use this when the user asks for a plan, schedule, deadline-based preparation, or exam timeline."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "topics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Topics the student needs to study.",
                },
                "deadline": {
                    "type": "string",
                    "description": "Deadline or exam date.",
                },
                "available_hours": {
                    "type": "integer",
                    "description": "Estimated study hours available per day.",
                    "default": 2,
                },
            },
            "required": ["topics", "deadline"],
        },
    },
    {
        "name": "generate_practice_quiz",
        "description": "Create a topic-specific practice quiz for a student based on an academic topic or course concept.",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The topic or concept the quiz should focus on.",
                },
                "num_questions": {
                    "type": "integer",
                    "description": "Number of practice questions to generate.",
                    "default": 5,
                },
            },
            "required": ["topic"],
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
        phonetics = ", ".join(
            [p.get("text", "") for p in item.get("phonetics", []) if p.get("text")]
        )

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

    return {
        "found": True,
        "source": "dictionaryapi.dev",
        "entries": entries,
    }


async def lookup_term(term: str, language: str = "English") -> Dict[str, Any]:
    language = language.strip().lower()
    cleaned_term = term.strip()

    if language != "english":
        return {
            "term": cleaned_term,
            "source": "none",
            "found": False,
            "message": "Only English lookup is supported.",
        }

    api_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{cleaned_term}"

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(api_url)
            response.raise_for_status()
            raw_data = response.json()
            return format_api_dictionary_result(raw_data)
        except Exception:
            fallback = load_fallback_dictionary()
            entry = fallback.get(cleaned_term.lower())

            if entry:
                return {
                    "found": True,
                    "source": "fallback",
                    "entries": [entry],
                }

            return {
                "term": cleaned_term,
                "source": "none",
                "found": False,
                "message": "No dictionary definition was found.",
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

    return {
        "query": query,
        "source": "course_notes",
        "found": len(matches) > 0,
        "matches": matches[:max_results],
    }


async def build_study_plan(
    topics: list[str], deadline: str, available_hours: int = 2
) -> Dict[str, Any]:
    if not topics:
        return {
            "found": False,
            "message": "No study topics were provided.",
        }

    plan = []
    for index, topic in enumerate(topics, start=1):
        plan.append(
            {
                "session": index,
                "topic": topic,
                "recommendation": (
                    f"Review {topic} using notes, examples, and active recall. "
                    "Then test yourself with a short summary or practice question."
                ),
                "estimated_hours": min(available_hours, 2),
            }
        )

    return {
        "found": True,
        "source": "study_plan_builder",
        "deadline": deadline,
        "available_hours": available_hours,
        "topics": topics,
        "plan": plan,
        "summary": (
            f"Built a study plan for {len(topics)} topic(s) before {deadline} "
            f"with about {available_hours} hours per day."
        ),
    }


async def generate_practice_quiz(topic: str, num_questions: int = 5) -> Dict[str, Any]:
    topic = topic.strip()
    safe_num_questions = max(3, min(int(num_questions), 8))

    quiz_messages = [
        {
            "role": "system",
            "content": (
                "You are an academic quiz generator. Create useful, topic-specific quiz questions "
                "for students. Return ONLY valid JSON. Do not include markdown, backticks, or extra text."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Create {safe_num_questions} study quiz questions about: {topic}. "
                "Each question should be specific to the topic and useful for exam preparation. "
                "Avoid generic template questions. Include a correct answer and a short explanation. "
                "Return JSON in this exact format: "
                '{"questions":[{"question_number":1,'
                '"type":"Definition/Application/Example/Comparison/Reflection",'
                '"question":"question text",'
                '"answer":"correct answer",'
                '"explanation":"why this question helps the student learn"}]}'
            ),
        },
    ]

    try:
        response = openai.chat.completions.create(
            model="gpt-4-0613",
            messages=quiz_messages,
            temperature=0.2,
        )

        content = response.choices[0].message.content or "{}"
        parsed = json.loads(content)
        questions = parsed.get("questions", [])

        if not questions:
            raise ValueError("No questions returned.")

    except Exception:
        questions = [
            {
                "question_number": 1,
                "type": "Definition",
                "question": f"What is {topic}?",
                "answer": (
                    f"{topic} is an academic topic that should be studied by understanding "
                    "its main parts, purpose, and examples."
                ),
                "explanation": "This checks whether you understand the basic meaning of the topic.",
            },
            {
                "question_number": 2,
                "type": "Application",
                "question": f"Why is {topic} important to study?",
                "answer": (
                    f"{topic} is important because it helps explain a larger concept, system, or process."
                ),
                "explanation": "This checks whether you understand why the topic matters.",
            },
            {
                "question_number": 3,
                "type": "Example",
                "question": f"Give one example related to {topic}.",
                "answer": (
                    f"A good example should clearly connect to {topic} and show how it works in practice."
                ),
                "explanation": "This checks whether you can connect the topic to an example.",
            },
        ]

    return {
        "found": True,
        "source": "llm_practice_quiz_generator",
        "topic": topic,
        "num_questions": len(questions),
        "questions": questions,
        "summary": f"Generated {len(questions)} topic-specific practice questions for {topic}.",
    }


TOOL_HANDLERS = {
    "lookup_term": lookup_term,
    "search_course_notes": search_course_notes,
    "build_study_plan": build_study_plan,
    "generate_practice_quiz": generate_practice_quiz,
}


async def call_openai_chat(messages: list[dict]) -> Any:
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


async def process_user_message(user_message: str) -> Dict[str, Any]:
    messages = [SYSTEM_PROMPT, {"role": "user", "content": user_message}]
    tool_trace = []

    for _ in range(5):
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
                try:
                    tool_result = await tool_func(**args)
                except Exception as exc:
                    tool_result = {
                        "found": False,
                        "source": "none",
                        "message": "The tool could not return usable data.",
                        "debug_error": str(exc),
                    }
            else:
                tool_result = {
                    "found": False,
                    "source": "none",
                    "message": f"Unknown tool: {tool_name}",
                }

            tool_trace.append(
                {
                    "tool": tool_name,
                    "args": args,
                    "result": tool_result,
                }
            )

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
                    "role": "function",
                    "name": tool_name,
                    "content": json.dumps(tool_result),
                }
            )

            continue

        assistant_content = message.content or ""
        return {
            "answer": assistant_content,
            "tool_trace": tool_trace,
        }

    return {
        "answer": (
            "I could not complete the full tool workflow, but I can still help. "
            "Please try rephrasing your question."
        ),
        "tool_trace": tool_trace,
    }


@app.get("/", response_class=HTMLResponse)
async def root(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/chat")
async def chat_api(request: Request) -> JSONResponse:
    payload = await request.json()
    user_message = payload.get("message", "").strip()

    if not user_message:
        raise HTTPException(status_code=400, detail="Message text is required.")

    result = await process_user_message(user_message)
    return JSONResponse(result)