from datetime import date, datetime, time, timedelta
import settings


def RankStayPoints(staypoints: list, dbScanLables: list):
    """
    this function will receive a list of stayPoints and rank them based on the number of neighbours and duration of each stayPoint

    combine each staypoint and count the number of labels that share the same lable with each staypoint
    then, send the objects list to the sorter

    dict is a dictionary that contains label + number of staypoints
    """
    resultsDictionary = {}

    for i in range(len(dbScanLables)):
        label = dbScanLables[i]
        staypointId = staypoints[i]
        if label in resultsDictionary:
            SPs = resultsDictionary[label]
            SPs.append(staypointId)
            resultsDictionary[label] = SPs
        else:
            SPs = []
            SPs.append(staypointId)
            resultsDictionary[label] = SPs


    # perform quick sorting algorithm to sort stayPoints based on number of neighbours
    # convert dic to a list before being sorted
    # rankingList = [(k, v) for k, v in resultsDictionary.items()]

    # create a list of RankingObjects in order to organize the required attributes used for ranking
    ###############################################################################################
    # rankingObjects = [RankingObject(obj[0], obj[1]) for obj in rankingList]
    rankingList = [StaypointCluster(k, v) for k, v in resultsDictionary.items()]

    arr = TimeCalculator.CalculateLabelsStationaryTime(rankingList)

    # arr[i].numberOfPoints is the value that should be multiplied by settings.RANKING_SETTINGS.NUMBER_OF_POINTS
    #   then, arr[i].totalTime should be multiplied by settings.RANKING_SETTINGS.STATIONARY_TIME. add the 2 values

    for i in range(len(arr)):
        rankingObj = arr[i]
        rankingObj.rankingDegree = (rankingObj.pointsCount * settings.RANKING_SETTINGS.WEIGHTS_NUMBER_OF_POINTS) + \
            (rankingObj.totalTime.total_seconds() * settings.RANKING_SETTINGS.WEIGHTS_STATIONARY_TIME)

    # do the sorting after the ranking then take top N records (specified in settings)

    # sorter = Sorter()
    # Sorter.Quicksort(rankingList, 0, len(rankingList))
    #############################################################################################
    rankingList = [StaypointCluster(k, v) for k, v in resultsDictionary.items()]

    arr = TimeCalculator.CalculateLabelsStationaryTime(rankingList)

    # arr[i].numberOfPoints is the value that should be multiplied by settings.RANKING_SETTINGS.NUMBER_OF_POINTS
    #   then, arr[i].totalTime should be multiplied by settings.RANKING_SETTINGS.STATIONARY_TIME. add the 2 values

    for i in range(len(arr)):
        rankingObj = arr[i]
        rankingObj.rankingDegree = (rankingObj.pointsCount * settings.RANKING_SETTINGS.WEIGHTS_NUMBER_OF_POINTS) + \
            (rankingObj.totalTime.total_seconds() * settings.RANKING_SETTINGS.WEIGHTS_STATIONARY_TIME)

    # do the sorting after the ranking then take top N records (specified in settings)

    # sorter = Sorter()
    Sorter.Quicksort(rankingList, 0, len(rankingList))
    ##############################################################################################
    return arr[0:settings.RANKING_SETTINGS.LIMIT_TOP_CLUSTERS_COUNT]


# https://www.codespeedy.com/quicksort-in-python/
class Sorter:
    def __init__(self):
        pass

    @staticmethod
    def Quicksort(rankingList, begin, end):
        """
        a modified implementation of quick sort algorithm to sort by number of neighbours
        ranking objects are sorted in a descending order
        pdf: 'Review on Sorting Algorithms'
        """
        if end - begin > 1:
            p = Sorter.Partition(rankingList, begin, end)
            Sorter.Quicksort(rankingList, begin, p)
            Sorter.Quicksort(rankingList, p + 1, end)

    @staticmethod
    def Partition(rankingList, begin, end):
        pivot = rankingList[begin].rankingDegree
        i = begin + 1
        j = end - 1

        while True:
            while (i <= j and rankingList[i].rankingDegree >= pivot):
                i = i + 1
            while (i <= j and rankingList[j].rankingDegree <= pivot):
                j = j - 1

            if i <= j:
                rankingList[i], rankingList[j] = rankingList[j], rankingList[i]
            else:
                rankingList[begin], rankingList[j] = rankingList[j], rankingList[begin]
            return j

# a class to represent the result objects. it contains cluster, DBSCAN-info and staypoint-related attributes


# class RankingObject:
class StaypointCluster:
    def __init__(self, label, staypoints):
        self.label = label
        self.stayPoints = staypoints
        self.pointsCount = len(staypoints)
        self.minSamples = settings.DBSCAN_PARAMETERS.MINIMUM_SAMPLES
        self.radius = settings.DBSCAN_PARAMETERS.RADIUS

    label = int
    stayPoints = list
    experiermentId = int
    # db scan params attributes
    radius = int
    minSamples = int
    #ranking related attributes
    rankingIndex = float
    pointsCount = int
    totalTime = timedelta
    MeanCenterPoint = tuple


class ClusterCategory:
    def __init__(self, label):
        self.label = label
        self.clusters = []

    label = int
    clusters = list


# this class is concerned with time operations. like: calculating stationary time of POIs, calculating leave-
# time (in case another data structure is going to be used)
class TimeCalculator:
    def __init__(self):
        pass

    @staticmethod
    def CalculateLabelsStationaryTime(staypointClusters):
        """
        this function will calculate the accumulated stationary time for a list of stay points
        """

        for staypointCluster in staypointClusters:
            # rankingObject = rankingObjects[i]
            timeAccumulator = timedelta(0)
            for staypoint in staypointCluster.stayPoints:
                timeD = staypoint.leavetime - staypoint.arrivaltime
                timeAccumulator = timeAccumulator + timeD

            staypointCluster.totalTime = timeAccumulator
        return staypointClusters
