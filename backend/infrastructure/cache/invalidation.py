from .keys import (
    FOUNDING_MEMBERS_KEY,
    ORGANIZATION_CONTENT_KEY,
    PUBLIC_NOTICES_KEY,
)
from .services import delete_cached


def invalidate_organization_content() -> None:
    delete_cached(ORGANIZATION_CONTENT_KEY)


def invalidate_public_notices() -> None:
    delete_cached(PUBLIC_NOTICES_KEY)


def invalidate_founding_members() -> None:
    delete_cached(FOUNDING_MEMBERS_KEY)
