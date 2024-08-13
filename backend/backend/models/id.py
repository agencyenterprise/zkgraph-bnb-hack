from pydantic import Field
from bson import ObjectId
from typing import Annotated

ID = Annotated[ObjectId | None, Field(None, alias='_id')]