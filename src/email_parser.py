import base64
import html2text

def _get_part_payload(part):
    data = part.get("body", {}).get("data")
    if not data:
        return ""
    text = base64.urlsafe_b64decode(data.encode("ASCII"))
    try:
        return text.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return text.decode("latin-1")
        except Exception:
            return ""

def extract_plain_text_from_payload(payload):
    if payload.get("mimeType") == "text/plain":
        return _get_part_payload(payload)
    if payload.get("mimeType") == "text/html":
        html = _get_part_payload(payload)
        return html2text.html2text(html).strip()
    parts = payload.get("parts", [])
    text_chunks = []
    html_chunk = None
    for part in parts:
        mt = part.get("mimeType", "")
        if mt == "text/plain":
            txt = _get_part_payload(part)
            if txt:
                text_chunks.append(txt)
        elif mt == "text/html":
            html_chunk = _get_part_payload(part) or html_chunk
        else:
            if part.get("parts"):
                nested = extract_plain_text_from_payload(part)
                if nested:
                    text_chunks.append(nested)
    if text_chunks:
        return "\n\n".join(text_chunks).strip()
    if html_chunk:
        return html2text.html2text(html_chunk).strip()
    return ""

def parse_message_to_row(msg):
    headers = msg.get("payload", {}).get("headers", [])
    header_map = {h["name"].lower(): h["value"] for h in headers}
    sender = header_map.get("from", "")
    subject = header_map.get("subject", "")
    date = header_map.get("date", "")
    body = extract_plain_text_from_payload(msg.get("payload", {}))
    body = body.strip()
    return [sender, subject, date, body]