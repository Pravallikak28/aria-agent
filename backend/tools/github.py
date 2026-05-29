import os
from github import Github
from dotenv import load_dotenv

load_dotenv()

def get_github_client():
    return Github(os.getenv("GITHUB_TOKEN"))

def get_notifications() -> str:
    """Get GitHub notifications"""
    try:
        g = get_github_client()
        notifications = g.get_user().get_notifications()

        items = []
        count = 0
        for notif in notifications:
            if count >= 5:
                break
            items.append(f"🔔 [{notif.reason}] {notif.subject.title} — {notif.repository.full_name}")
            count += 1

        if not items:
            return "No new GitHub notifications."

        return "\n".join(items)

    except Exception as e:
        return f"GitHub error: {str(e)}"


def get_pull_requests() -> str:
    """Get open pull requests across user repos"""
    try:
        g = get_github_client()
        user = g.get_user()

        prs = []
        for repo in user.get_repos():
            open_prs = repo.get_pulls(state='open')
            for pr in open_prs:
                prs.append(f"🔀 [{repo.name}] #{pr.number} {pr.title} by {pr.user.login}")

        if not prs:
            return "No open pull requests found."

        return "\n".join(prs[:10])

    except Exception as e:
        return f"GitHub PR error: {str(e)}"