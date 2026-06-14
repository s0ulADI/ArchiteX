from pydantic import BaseModel


class DeliveryResult(BaseModel):
    status: str
    url: str | None = None
    detail: str | None = None


class DownloadTokenRequest(BaseModel):
    download_token: str


class GithubDeliveryRequest(BaseModel):
    download_token: str
    repo_name: str
    github_token: str


class VercelDeliveryRequest(BaseModel):
    github_repo_url: str
    vercel_token: str
