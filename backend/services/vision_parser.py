import asyncio
import json

from config import settings
from models.architecture import ParsedArchitecture
from utils.image_utils import image_to_base64


VISION_PROMPT = """
You are an expert software architect. Analyze this whiteboard/diagram image.

Identify every component. For each, output:
- id: kebab-case slug
- label: display name as written
- type: one of [rest_api, frontend, database, cache, queue, worker]
- language: one of [node, python, null] - null for databases/caches
- endpoints: list of API routes you can read or infer (e.g. /login, /signup)
- env_vars: list of environment variables this service likely needs

Identify every connection (arrow) between components:
- from_id -> to_id
- protocol: http | tcp | amqp

Also provide:
- raw_description: one paragraph describing what you see
- confidence: float 0.0-1.0

Respond ONLY in valid JSON matching this schema:
{
  "services": [...],
  "connections": [...],
  "raw_description": "...",
  "confidence": 0.0
}
No explanation. No markdown. Pure JSON only.
"""


class VisionAPIError(RuntimeError):
    pass


def _clean_json_response(content: str) -> str:
    content = content.strip()
    if content.startswith("```"):
        lines = [line for line in content.splitlines() if not line.strip().startswith("```")]
        return "\n".join(lines).strip()
    return content


def _validate_architecture(content: str) -> ParsedArchitecture:
    cleaned = _clean_json_response(content)
    data = json.loads(cleaned)
    return ParsedArchitecture.model_validate(data)


async def _call_gemini(image_bytes: bytes, mime_type: str) -> str:
    if not settings.gemini_api_key:
        raise VisionAPIError("GEMINI_API_KEY is not configured")

    def _sync_call() -> str:
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(
            [VISION_PROMPT, {"mime_type": mime_type, "data": image_bytes}],
            generation_config={"response_mime_type": "application/json"},
        )
        return response.text

    return await asyncio.wait_for(asyncio.to_thread(_sync_call), timeout=30)


async def _call_openai(image_bytes: bytes, mime_type: str) -> str:
    if not settings.openai_api_key:
        raise VisionAPIError("OPENAI_API_KEY is not configured")

    def _sync_call() -> str:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key, timeout=30)
        encoded = image_to_base64(image_bytes)
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": VISION_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime_type};base64,{encoded}"},
                        },
                    ],
                }
            ],
        )
        content = response.choices[0].message.content
        if not content:
            raise VisionAPIError("OpenAI returned an empty response")
        return content

    return await asyncio.wait_for(asyncio.to_thread(_sync_call), timeout=30)


async def parse_architecture_from_image(
    image_bytes: bytes,
    mime_type: str,
    mode: str = "backend",
) -> ParsedArchitecture:
    preferred = settings.vision_model.lower()
    providers = ["gemini", "openai"] if preferred == "gemini" else ["openai", "gemini"]
    errors: list[str] = []

    for provider in providers:
        try:
            if provider == "gemini":
                content = await _call_gemini(image_bytes, mime_type)
            else:
                content = await _call_openai(image_bytes, mime_type)
            return _validate_architecture(content)
        except Exception as exc:
            errors.append(f"{provider}: {exc}")

    raise VisionAPIError("; ".join(errors) or "No vision provider could parse the diagram")
