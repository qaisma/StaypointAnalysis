import datetime
import enum
from operator import itemgetter

class TimeWindow:
    startTime = datetime.datetime.strptime('2000-01-01 00:00:00.000', '%Y-%m-%d %H:%M:%S.%f')
    endTime = datetime.datetime.strptime('2000-01-01 00:00:00.000', '%Y-%m-%d %H:%M:%S.%f')
    stypoints = []
    duration = datetime.timedelta

#enum
class TimeUnits(enum.Enum):
    Hour = 1
    Day = 2
    Week = 3
    Month = 4
    Year = 5

def DivideIntoTimeWindows(data: list, timeUnit: TimeUnits, frequency: int):
    # this function arranges the staypoints into containers, these containers (list) represent time windows
    result = []
    
    if(len(data)==0):
        raise ValueError('No data match the query conditions')

    sortedData = sorted(data, key=lambda point: point.arrivaltime)
    experimentEndTime = sortedData[len(sortedData)-1].leavetime
    timeDelta={}
    
    if(timeUnit == TimeUnits.Hour):
        timeDelta = datetime.timedelta(hours=1)
    elif(timeUnit == TimeUnits.Day):
        timeDelta = datetime.timedelta(days=1)
    elif(timeUnit == TimeUnits.Week):
        timeDelta = datetime.timedelta(weeks=1)
    elif(timeUnit == TimeUnits.Month): #30 days
        timeDelta = datetime.timedelta(days=30)
    elif(timeUnit == TimeUnits.Year):
        timeDelta = datetime.timedelta(days=365)

    currentWindowStart = sortedData[0].arrivaltime
    currentWindowEnd = currentWindowStart + timeDelta

    while currentWindowEnd <= experimentEndTime:
        timeWindow = TimeWindow()
        timeWindow.duration = timeDelta
        timeWindow.startTime = currentWindowStart
        timeWindow.endTime = currentWindowEnd
        timeWindow.stypoints = [staypoint for staypoint in sortedData if staypoint.arrivaltime >= currentWindowStart
         and staypoint.leavetime < currentWindowEnd]
        result.append(timeWindow)
        # increase current pointer for next items
        currentWindowStart = currentWindowEnd
        currentWindowEnd = currentWindowEnd + timeDelta
    
    return result
        




