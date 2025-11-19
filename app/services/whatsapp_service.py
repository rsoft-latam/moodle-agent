from typing import Any, Dict, Optional
import requests

from app.config import WHATSAPP_PHONE_ID, WHATSAPP_TOKEN


def extract_whatsapp_message(payload: Dict[str, Any]):
    """
    Extract key fields from the WhatsApp Cloud payload:
    text, from_phone, message_id, business_phone_id
    """
    text = from_phone = message_id = business_phone_id = None

    try:
        entry = payload.get("entry", [])[0]
        change = entry.get("changes", [])[0]
        value = change.get("value", {})

        messages = value.get("messages", [])
        metadata = value.get("metadata", {})

        business_phone_id = metadata.get("phone_numer_id") or None

        if messages:
            m = messages[0]
            message_id = m.get("id")
            from_phone = m.get("from")

            if m.get("type") == "text":
                text = m.get("text", {}).get("body")
    except Exception:
        pass

    return {
        "text": text,
        "from_phone": from_phone,
        "message_id": message_id,
        "business_phone_id": business_phone_id,
    }


def send_whatsapp_message(
    business_phone_id: str, to_phone: str, text: str, message_id: Optional[str] = None
):
    if not WHATSAPP_TOKEN:
        return {"warning": "WHATSAPP_TOKEN not configured"}

    targed_id = business_phone_id

    if not targed_id:
        return {"warning": "there is not phone number id"}

    url = f"https://graph.facebook.com/v18.0/{targed_id}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "text",
        "text": {"body": (text or "")},
    }

    if message_id:
        data["context"] = {"message_id": message_id}

    try:
        r = requests.post(url, headers=headers, json=data, timeout=20)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        return {"error": "whatsapp_send_failed", "detail": str(e)}


def whatsapp_mark_read(business_phone_id: str, message_id: str) -> Dict[str, Any]:
    if not WHATSAPP_TOKEN:
        return {
            "warning": "WHATSAPP_TOKEN not configured; message will not be marked as read."
        }
    target_id = business_phone_id or WHATSAPP_PHONE_ID
    if not target_id:
        return {
            "warning": "There is no phone_number_id (neither in the payload nor in the env var)."
        }
    url = f"https://graph.facebook.com/v18.0/{target_id}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id,
    }
    try:
        r = requests.post(url, headers=headers, json=data, timeout=20)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        return {"error": "wa_mark_read_failed", "detail": str(e)}
