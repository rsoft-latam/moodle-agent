
from typing import Any, Optional
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

from app.config import OPENAI_API_KEY, OPENAI_MODEL
from app.tools.moodle_tools import moodle_calendar_upcoming, moodle_call_raw, moodle_course_assigments, moodle_site_info, moodle_user_courses, moodle_user_grades_by_courses, moodle_force_login


MOODLE_TOOLS = [
    moodle_force_login,
    moodle_site_info,
    moodle_user_courses,
    moodle_course_assigments,
    moodle_user_grades_by_courses,
    moodle_calendar_upcoming,
    moodle_call_raw
]

SYSTEM_PROMP = """Eres un asistente academico integrado con moodle
Reglas: 
- Usa las herramientas de Moodle para responder preguntas sobre cursos, tareas, calendario, calificaciones del usuario del token   
- Si necesitas informacion general del sitio o usuario, usa moodle_site_info
- Para listar cursos: moodle_user_courses
- Para tareas de un curso: moodle_course_assigments
- Para calificaciones: moodle_user_grades_by_courses
- Para eventos proximos: moodle_calendar_upcoming
- Para cualquier otra funcion dosponible: moodle_call_raw
- Si alguna llamada devuelve 'invalidtoken' el sistema reintenta automaticamente con moodle_force_login
Response en español, claro y consiso
"""

def build_agent(): 
    if not OPENAI_API_KEY:
        raise RuntimeError('Missing OPENAI_API_KEY')
    
    llm = ChatOpenAI(
        model=OPENAI_MODEL,
        temperature=0.2,
        api_key=OPENAI_API_KEY,
        timeout=40,
        max_retries=2
    )

    agent = create_agent(
        model=llm,
        tools=MOODLE_TOOLS,
        system_prompt=SYSTEM_PROMP
    )

    return agent

AGENT: Optional[Any] = None

def ensure_agent():
    global AGENT
    if AGENT is None:
        AGENT = build_agent()
    return AGENT    
