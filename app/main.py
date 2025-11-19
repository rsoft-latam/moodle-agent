from fastapi import FastAPI, HTTPException, Query, Request
from mangum import Mangum
import uvicorn

from app.config import WHATSAPP_VERIFY_TOKEN
from app.models.models import InvokeRequest, InvokeResponse
from app.services.agent_service import ensure_agent
from app.services.moodle_service import ensure_moodle_token
from app.services.whatsapp_service import extract_whatsapp_message, send_whatsapp_message, whatsapp_mark_read


app = FastAPI(
    title='Moodle Agent',
    description='API',
    version='1.0.0',
    docs_url='/docs',
    redoc_url='/redoc'
)

@app.get('/health')
def health():
    ok = True
    try:
        ensure_moodle_token()
        return { 'ok': ok }
    except Exception:
        ok = False
        return { 'ok': ok }

@app.post('/invoke', response_model=InvokeResponse)
def invoke(req: InvokeRequest):
    agent = ensure_agent()
    messages = [{ 'role': 'user', 'content': req.input }]
    result = agent.invoke({'messages': messages})

    msgs = result.get('messages', [])
    last = msgs[-1] if msgs else None
    out = getattr(last, 'content') if last is not None and hasattr(last, 'content') else (last.get('content')if isinstance(last, dict) else None) or 'There is no answer from agent'

    return InvokeResponse(message=out)

@app.get('/webhook')
def whatsapp_verify(
    hub_mode:str = Query(None, alias='hub.mode'),
    hub_challenge:str = Query(None, alias='hub.challenge'),
    hub_verify_token:str = Query(None, alias='hub.verify_token')
):
    if hub_mode == 'suscribe' and hub_verify_token == WHATSAPP_VERIFY_TOKEN:
        return int(hub_challenge) if(hub_challenge and hub_challenge.isdigit()) else hub_challenge or ''
    raise HTTPException(status_code=403, detail='verification_failed')

@app.post('/webhook')
async def whatsapp_webhook(req: Request):
    try:
        payload = await req.json()
    except Exception:
        payload = {}
        
    extracted = extract_whatsapp_message(payload)
    text = extracted['text']
    from_phone = extracted['from_phone']
    message_id = extracted['message_id']
    business_phone_id = extracted['business_phone_id']

    if not text or not from_phone:
        return { 'status': 'ignored' }
    
    agent = ensure_agent()
    result = agent.invoke({'messages': [{'role': 'user', 'content': text}]})
    msgs = result.get('messages', [])
    last = msgs[-1] if msgs else None
    out = getattr(last, 'content') if last is not None and hasattr(last, 'content') else (last.get('content')if isinstance(last, dict) else None) or 'There is no answer from agent'

    send_res = send_whatsapp_message(business_phone_id, from_phone, out, message_id)

    if message_id:
        _ = whatsapp_mark_read(business_phone_id, message_id)

    return { 'status': 'ok', 'agent_answer': out, 'send_result': send_res }

# === Lambda adapter ===
lambda_handler = Mangum(app)

# === Local Dev ===
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=3000)
