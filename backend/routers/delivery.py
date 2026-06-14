from fastapi import APIRouter
from fastapi.responses import Response

from models.delivery import DownloadTokenRequest, GithubDeliveryRequest, VercelDeliveryRequest
from services.github_pusher import GitHubPushError, push_files_to_github
from services.repository_store import get_repository
from services.vercel_deployer import VercelDeployError, deploy_github_repo
from services.zipper import files_to_zip_bytes
from utils.errors import api_error


router = APIRouter()


@router.post("/zip")
async def deliver_zip(request: DownloadTokenRequest) -> Response:
    record = get_repository(request.download_token)
    if record is None:
        raise api_error(404, "download_token not found or expired", request.download_token)

    return Response(
        content=files_to_zip_bytes(record.files),
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="repo.zip"'},
    )


@router.post("/github")
async def deliver_github(request: GithubDeliveryRequest) -> dict[str, str]:
    record = get_repository(request.download_token)
    if record is None:
        raise api_error(404, "download_token not found or expired", request.download_token)

    try:
        repo_url = await push_files_to_github(record.files, request.repo_name, request.github_token)
    except GitHubPushError as exc:
        raise api_error(502, "GitHub push failure", str(exc)) from exc

    return {"repo_url": repo_url}


@router.post("/vercel")
async def deliver_vercel(request: VercelDeliveryRequest) -> dict[str, str]:
    try:
        deploy_url = await deploy_github_repo(request.github_repo_url, request.vercel_token)
    except VercelDeployError as exc:
        raise api_error(502, "Vercel deploy failure", str(exc)) from exc

    return {"deploy_url": deploy_url}
