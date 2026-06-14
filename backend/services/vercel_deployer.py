import asyncio

import httpx


class VercelDeployError(RuntimeError):
    pass


async def deploy_github_repo(github_repo_url: str, vercel_token: str) -> str:
    async def _request() -> str:
        headers = {"Authorization": f"Bearer {vercel_token}"}
        payload = {"gitSource": {"type": "github", "repo": github_repo_url}}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post("https://api.vercel.com/v13/deployments", json=payload, headers=headers)
        if response.status_code >= 400:
            raise VercelDeployError(response.text)
        data = response.json()
        url = data.get("url") or data.get("alias", [None])[0]
        if not url:
            raise VercelDeployError("Vercel did not return a deployment URL")
        if not url.startswith("http"):
            url = f"https://{url}"
        return url

    try:
        return await asyncio.wait_for(_request(), timeout=30)
    except VercelDeployError:
        raise
    except Exception as exc:
        raise VercelDeployError(str(exc)) from exc
