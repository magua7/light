from pydantic import BaseModel


class DashboardStatItem(BaseModel):
    name: str
    value: int | float
