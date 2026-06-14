import asyncio
import json

import httpx
from bs4 import BeautifulSoup
from fastapi import APIRouter
from pydantic import BaseModel

from config import settings
from utils.errors import api_error


router = APIRouter()


class UrlScrapeRequest(BaseModel):
    url: str


def _section_type(tag_name: str, index: int) -> str:
    if tag_name in {"nav", "header", "main", "footer", "aside"}:
        return tag_name
    if tag_name == "section":
        return f"section-{index}"
    if tag_name == "article":
        return f"article-{index}"
    return f"block-{index}"


def _structure_from_html(html: str) -> dict[str, object]:
    soup = BeautifulSoup(html, "html.parser")
    body = soup.body or soup
    structural_tags = body.find_all(["nav", "header", "main", "section", "article", "aside", "footer"], recursive=True)
    sections = []
    for index, tag in enumerate(structural_tags[:12], start=1):
        sections.append(_section_type(tag.name or "block", index))

    if not sections:
        sections = ["body"]

    nav = soup.find("nav")
    header = soup.find("header")
    nav_pattern = "top-fixed" if nav and header else "top"
    max_direct_children = max((len(tag.find_all(recursive=False)) for tag in structural_tags), default=1)
    column_structure = "multi-column" if max_direct_children >= 3 else "single-column"

    return {
        "layout_description": "Structural page skeleton with " + ", ".join(sections[:6]),
        "sections": sections,
        "column_structure": column_structure,
        "nav_pattern": nav_pattern,
    }


async def _llm_refine_structure(structure: dict[str, object]) -> dict[str, object]:
    if not settings.openai_api_key:
        return structure

    prompt = (
        "Describe only the structural skeleton of this page - sections, layout pattern, nav type. "
        "Do not describe any brand, color, or content. Return JSON with keys "
        "layout_description, sections, column_structure, nav_pattern.\n\n"
        f"Observed structure: {json.dumps(structure)}"
    )

    def _sync_call() -> dict[str, object]:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key, timeout=30)
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.choices[0].message.content or "{}"
        refined = json.loads(content)
        return {
            "layout_description": str(refined.get("layout_description") or structure["layout_description"]),
            "sections": list(refined.get("sections") or structure["sections"]),
            "column_structure": str(refined.get("column_structure") or structure["column_structure"]),
            "nav_pattern": str(refined.get("nav_pattern") or structure["nav_pattern"]),
        }

    return await asyncio.wait_for(asyncio.to_thread(_sync_call), timeout=30)


@router.post("/scrape")
async def scrape_url(request: UrlScrapeRequest) -> dict[str, object]:
    try:
        async with httpx.AsyncClient(timeout=settings.scraper_timeout_seconds, follow_redirects=True) as client:
            response = await client.get(request.url)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise api_error(502, "URL scrape failed", str(exc)) from exc

    structure = _structure_from_html(response.text)
    try:
        return await _llm_refine_structure(structure)
    except Exception:
        return structure
