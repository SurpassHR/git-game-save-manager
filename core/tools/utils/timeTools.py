import pytz
from datetime import datetime

def getCurrTimeInFmt(fmt: str) -> str:
    return datetime.now().strftime(fmt)

def getCurrTime() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def convertDateFormat(dateObj: datetime):
    timezoneChina = pytz.timezone('Asia/Shanghai')
    localizedDate = timezoneChina.localize(dateObj)
    formattedDate = localizedDate.strftime('%a %b %d %Y %H:%M:%S GMT%z (%Z)')
    return formattedDate