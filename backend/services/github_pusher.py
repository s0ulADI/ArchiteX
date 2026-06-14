import asyncio


class GitHubPushError(RuntimeError):
    pass


async def push_files_to_github(files: dict[str, str], repo_name: str, github_token: str) -> str:
    def _sync_push() -> str:
        from github import Github, GithubException

        try:
            client = Github(github_token)
            user = client.get_user()
            repo = user.create_repo(repo_name, private=False, auto_init=False)
            for path, content in sorted(files.items()):
                repo.create_file(path, f"Add {path}", content)
            return repo.html_url
        except GithubException as exc:
            detail = getattr(exc, "data", None) or str(exc)
            raise GitHubPushError(str(detail)) from exc

    try:
        return await asyncio.wait_for(asyncio.to_thread(_sync_push), timeout=30)
    except GitHubPushError:
        raise
    except Exception as exc:
        raise GitHubPushError(str(exc)) from exc
