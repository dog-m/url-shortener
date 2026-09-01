import re

from pydantic_core import core_schema

#


_MAX_NAME_LENGTH = 200


def validate_name(name: str) -> str:
    # normalize
    name = ' '.join(name.strip().split())

    # basic checks
    if not name:
        raise ValueError('Name cannot be empty')
    if len(name) > _MAX_NAME_LENGTH:
        raise ValueError(f'Name must be no longer than {_MAX_NAME_LENGTH} characters')
    if not name.isprintable():
        raise ValueError('Name contains non-printable characters')

    # structural rules
    if re.search(r"[.'-]{2,}", name):
        raise ValueError('Name cannot contain consecutive punctuation')
    if re.search(r"^[.'-]|[.'-]$", name):
        raise ValueError('Name cannot start or end with punctuation')

    # allow Unicode letters + safe separators
    if not all(c.isalpha() or c in " -'." for c in name):
        raise ValueError('Name contains invalid characters')

    return name



class ValidName(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        return core_schema.no_info_after_validator_function(
            validate_name,
            core_schema.str_schema(min_length=1, max_length=_MAX_NAME_LENGTH),
        )

