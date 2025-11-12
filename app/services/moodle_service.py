import requests

def _login(): 
    url = (
        f"{MOODLE_BASE_URL}/login/token.php"
        f"?username={MOODLE_USERNAME}&password={MOODLE_PASSWORD}&service={MOODLE_SERVICE}"
    )

    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    return data['token']

def _moodle_call_ws(ws_function:str, token:str, **body):
    url = f"{MOODLE_BASE_URL}/webservice/rest/server.php"
    params = {
        'moodlewsrestformat': 'json',
        'wsfunction': ws_function,
        'wstoken': token
    }
    try:
        resp = requests.post(url, params, body, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data
    except requests.RequestException as e:
        return {
            'exception': 'request fail',
            'message': str(e)
        }
    
def moodle_call(ws_function:str, **body):
    token = _login()
    data = _moodle_call_ws(ws_function,token, body)
    return data