from typing import Literal

from pydantic import BaseModel


class WarningStatusUpdate(BaseModel):
    process_status: Literal["已处理", "未处理"]
