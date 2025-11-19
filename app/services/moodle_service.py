from typing import Any, Optional
import requests

from app.config import MOODLE_BASE_URL, MOODLE_PASSWORD, MOODLE_SERVICE, MOODLE_USERNAME

_MOODLE_TOKEN: Optional[str] = None

def ensure_moodle_token() -> str:
    """
    Ensure a token exists in cache.
    """
    global _MOODLE_TOKEN
    if not _MOODLE_TOKEN:
        _MOODLE_TOKEN = _login()
    return _MOODLE_TOKEN    

def moodle_call(ws_function:str, **body):
    token = ensure_moodle_token()
    data = _moodle_call_ws(ws_function,token, **body)
    return data

def _login():
    """
    Logs in against /login/token.php with username/password/service and returns the token. 
    Throws an exception if it fails.
    """
    if not(MOODLE_USERNAME and MOODLE_PASSWORD and MOODLE_SERVICE):
        raise RuntimeError('MOODLE_USERNAME, MOODLE_PASSWORD, or MOODLE_SERVICE are missing from the environment.')

    url = (
        f"{MOODLE_BASE_URL}/login/token.php"
        f"?username={MOODLE_USERNAME}&password={MOODLE_PASSWORD}&service={MOODLE_SERVICE}"
    )

    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        raise RuntimeError(f'Error connecting to Moodle login: {e}')

    if 'token' not in data:
        raise RuntimeError(f'Invalid Moodle login: {e}')    

    return data['token']

def _moodle_call_ws(ws_function:str, token:str, **body) -> Any:
    """
    Calls the Moodle REST WS with the specified token. Returns the JSON (Python object). 
    Does not handle re-login. That is done by the 'moodle_call' wrapper below.
    """
    url = f"{MOODLE_BASE_URL}/webservice/rest/server.php"
    params = {
        'moodlewsrestformat': 'json',
        'wsfunction': ws_function,
        'wstoken': token
    }
    try:
        resp = requests.post(url, params=params, data=body, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data
    except requests.RequestException as e:
        return {
            'exception': 'request fail',
            'message': str(e)
        }
        
def moodle_current_userid() -> Optional[int]:
    info = moodle_call('core_webservice_get_site_info')
    if isinstance(info, dict) and 'userid' in info:
        return info['userid']
    return None