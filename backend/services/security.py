from backend.models.url import Url
from backend.models.user import User

#


async def is_url_freely_accessible(url: Url) -> bool:  # noqa: ARG001
    # TODO: simple URL access level check
    return True



async def can_url_be_visited_by(user: User, url: Url) -> bool:  # noqa: ARG001
    # TODO: privilege level checks ??
    return True

