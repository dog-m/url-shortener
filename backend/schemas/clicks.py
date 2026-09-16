from pydantic import BaseModel

#


class ClickActivityDaily(BaseModel):
    date: str
    count: int



class ClickActivityWeekly(BaseModel):
    mon: int = 0
    tue: int = 0
    wed: int = 0
    thu: int = 0
    fri: int = 0
    sat: int = 0
    sun: int = 0


WEEKDAY_INDEX_TO_ATTR_NAME = {
    0: "sun",
    1: "mon",
    2: "tue",
    3: "wed",
    4: "thu",
    5: "fri",
    6: "sat",
}



class ClickActivityStats(BaseModel):
    dates: list[ClickActivityDaily]
