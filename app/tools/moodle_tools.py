import json
import time
from typing import Any, Optional
from langchain.tools import tool
from pydantic import BaseModel, Field

from app.services.moodle_service import ensure_moodle_token, moodle_call, moodle_current_userid

class User(BaseModel):
    userid: Optional[int] = Field(default=None, description='user id from student in moodle')

@tool('moodle_force_login', return_direct=False, description='test')
def moodle_force_login() -> str:
    try:
        ensure_moodle_token()
        return json.dumps({
            'ok': True,
            'message': 'login sucessfully'
        })
    except Exception as e:
        return json.dumps({
            'ok': False,
            'message': str(e)
        })
    
@tool('moodle_site_info', return_direct=False, description='test')
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

@tool('moodle_user_courses', return_direct=False, args_schema=User, description='test')
def moodle_user_courses(userid: Optional[int] = None) -> str:
    try:
        if userid is None:
            userid = moodle_current_userid()
        if userid is None:
            return json.dumps({ 'error': 'we could not find the user id' })     
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

@tool('moodle_course_assigments', return_direct=False, description='test')
def moodle_course_assigments(courseid: int) -> str:
    try:
        payload = {'courseids[0]': courseid}
        resp = moodle_call('mod_assign_get_assignments', **payload)
        return json.dumps({
            'ok': True,
            'data': resp
        })
    except Exception as e:
        return json.dumps({
            'ok': False,
            'message': str(e)
        })

@tool('moodle_user_grades_by_courses', return_direct=False, description='test')
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

@tool('moodle_calendar_upcoming', return_direct=False, description='test')
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

@tool('moodle_call_raw', return_direct=False, description='test')
def moodle_call_raw(wsfunction: str, params: Any) -> str:
    try:
        resp = moodle_call(wsfunction, **params )
        return json.dumps({
            'ok': True,
            'data': resp
        })
    except Exception as e:
        return json.dumps({
            'ok': False,
            'message': str(e)
        })   
