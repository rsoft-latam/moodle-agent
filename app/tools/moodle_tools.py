import json
import time
from typing import Any
from langchain.tools import tool
from pydantic import BaseModel, Field

from app.services.moodle_service import force_relogin, moodle_call

class User(BaseModel):
    userid: int = Field(description='user id from student in moodle')

@tool('relogin', return_direct=False)
def relogin() -> str:
    try:
        force_relogin()
        return json.dumps({
            'ok': True,
            'message': 'login sucessfully'
        })
    except Exception as e:
        return json.dumps({
            'ok': False,
            'message': str(e)
        })
    
@tool('moodle_site_info', return_direct=False)
def moodle_site_info() -> str:
    try:
        resp = moodle_call('core_webservice_get_site_info')
        return json.dumps({
            'ok': True,
            'data': resp
        })
    except Exception as e:
        return json.dumps({
            'ok': False,
            'message': str(e)
        })   

@tool('moodle_user_courses', return_direct=False, args_schema=User)
def moodle_user_courses(userid: int) -> str:
    try:
        resp = moodle_call('core_enrol_get_users_courses', userid=userid)
        return json.dumps({
            'ok': True,
            'data': resp
        })
    except Exception as e:
        return json.dumps({
            'ok': False,
            'message': str(e)
        })   

@tool('moodle_course_assigments', return_direct=False)
def moodle_course_assigments(courseid: int) -> str:
    try:
        resp = moodle_call('mod_assign_get_assignments', {'courseids[0]': courseid})
        return json.dumps({
            'ok': True,
            'data': resp
        })
    except Exception as e:
        return json.dumps({
            'ok': False,
            'message': str(e)
        })

@tool('moodle_user_grades_by_courses', return_direct=False)
def moodle_user_grades_by_courses(courseid: int, userid: int) -> str:
    try:
        resp = moodle_call('gradereport_user_get_grade_items', courseid=courseid, userid= userid)
        return json.dumps({
            'ok': True,
            'data': resp
        })
    except Exception as e:
        return json.dumps({
            'ok': False,
            'message': str(e)
        })     

@tool('moodle_calendar_upcoming', return_direct=False)
def moodle_calendar_upcoming(limitnum: int = 10) -> str:
    try:
        now = int(time.time())
        resp = moodle_call('core_calendar_get_action_events_by_timesort', timesortfrom=now, limitnum=limitnum )
        return json.dumps({
            'ok': True,
            'data': resp
        })
    except Exception as e:
        return json.dumps({
            'ok': False,
            'message': str(e)
        })     

@tool('moodle_call_raw', return_direct=False)
def moodle_call_raw(wsfunction: str, params: Any) -> str:
    try:
        resp = moodle_call(wsfunction, params )
        return json.dumps({
            'ok': True,
            'data': resp
        })
    except Exception as e:
        return json.dumps({
            'ok': False,
            'message': str(e)
        })   
