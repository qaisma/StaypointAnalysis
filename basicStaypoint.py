import datetime


class StayPoint:
    staypointid = int
    trajectoryid = int
    experimentid = int
    posx = float
    posy = float
    arrivaltime = datetime.datetime.strptime('2000-01-01 00:00:00.000', '%Y-%m-%d %H:%M:%S.%f')
    leavetime = datetime.datetime.strptime('2000-01-01 00:00:00.000', '%Y-%m-%d %H:%M:%S.%f')