from copy import deepcopy

import glom
from pydantic import BaseModel


def tweak(payload, replace: dict | None = None, drop: list[str] | None = None, add: dict | None = None):
    if not replace:
        replace = {}
    if not drop:
        drop = []
    if not add:
        add = {}
    updated_payload = payload.model_dump() if isinstance(payload, BaseModel) else deepcopy(payload)
    for k, v in replace.items():
        glom.glom(updated_payload, k)
        glom.assign(updated_payload, k, v)

    for path in drop:
        glom.delete(updated_payload, path)

    for k, v in add.items():
        glom.assign(updated_payload, k, v)

    return updated_payload
