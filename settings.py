import timeWindow


class SEARCH_CONDITIONS(object):
    FIRST_ARRIVAL_TIME = "'17-11-2020'"
    LAST_LEAVE_TIME = "'16-11-2019'"
    # #eper.Id 277-308 new staypoints (test on them)
    # FIRST_EXPERIMENT_ID = "'699'" #consider data from 699 till 728 (<699)
    # LAST_EXPERIMENT_ID = "'728'"
    
    FIRST_EXPERIMENT_ID = "'715'"
    LAST_EXPERIMENT_ID = "'715'"


class DBSCAN_PARAMETERS(object):
    RADIUS = 10
    MINIMUM_SAMPLES = 10
    
    CLUSTER_RADIUS = 30
    CLUSTER_MINIMUM_SAMPLES = 2


class TIMEWINDOW_PARAMETERS(object):
    TIME_UNIT = timeWindow.TimeUnits.Hour
    FREQUENCY = 1


class PLOT_SETTINGS(object):
    FONTSIZE = 15
    ALPHA_VALUE_CORE = 0.6
    ALPHA_VALUE_NON_CORE = 0.1


class DB_SETTINGS(object):
    FILENAME = 'database.ini'
    DATABASE_NAME = 'latency.staypoint'
    SECTION = 'researchdb'
    # DATABASE_NAME = 'staypoints'
    # SECTION = 'localDb2'

class RANKING_SETTINGS(object):
    # this is a percentage
    WEIGHTS_NUMBER_OF_POINTS = 60
    WEIGHTS_STATIONARY_TIME = 40
    #combine both wights, priority for number of points, and then we use the time to distiguish between the clusters with the same number of visitors
    # save clusters with ranking in db
    LIMIT_TOP_CLUSTERS_COUNT = 5

    # CLUSTER_CENTER_THRESHOLD = 50