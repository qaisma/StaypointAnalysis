import basicStaypoint
import DAL
import matplotlib.pyplot as plt
import timeWindow
import settings
from sklearn.cluster import DBSCAN
import rankingManager
from datetime import datetime
import os
import numpy as np
import Utilities

########### --- Context-Aware Window Sizing for Point of Interest Detection in Multi-Purpose Areas --- ###########


def GetDayName(dateObj):
    weekno = dateObj.weekday()
    dayname = 'Mon'
    if(weekno == 1):
        dayname = 'Tue'
    elif (weekno == 2):
        dayname = 'Wed'
    elif (weekno == 3):
        dayname = 'Thu'
    elif (weekno == 4):
        dayname = 'Fri'
    elif (weekno == 5):
        dayname = 'Sat'
    elif (weekno == 6):
        dayname = 'Sun'
    return dayname


def CalculateClustersMeanCenter(clusters):
    for cluster in clusters:
        clusterPointsMatrix = [(point.posx, point.posy)
                               for point in cluster.stayPoints]
        # we need to store the mean center of each cluster into the attribute 'MeanCenterPoint' of type tuple
        meanCenterPointXs = [clusterPointsMatrix[i][0]
                             for i in range(0, len(clusterPointsMatrix))]
        meanCenterPointYs = [clusterPointsMatrix[i][1]
                             for i in range(0, len(clusterPointsMatrix))]

        meanCenterPointX = Utilities.CalculateMean(meanCenterPointXs)
        meanCenterPointY = Utilities.CalculateMean(meanCenterPointYs)
        cluster.MeanCenterPoint = (round(meanCenterPointX,2), round(meanCenterPointY,2))

    return clusters

def CalculateCategoryMeanCenter(category):
    meanCenterPointXs=[]
    meanCenterPointYs=[]

    for staypointCluster in category.clusters:
        meanCenterPointXs.append(staypointCluster.MeanCenterPoint[0])
        meanCenterPointYs.append(staypointCluster.MeanCenterPoint[1])

    meanCenterPointX = Utilities.CalculateMean(meanCenterPointXs)
    meanCenterPointY = Utilities.CalculateMean(meanCenterPointYs)
    return (round(meanCenterPointX,2), round(meanCenterPointY,2))

def CalculateMeanCenterDistance(clusterMeanCenter, CategoryMeanCenter):
    return (round(abs(CategoryMeanCenter[0] - clusterMeanCenter[0]),2),round(abs(CategoryMeanCenter[1] - clusterMeanCenter[1]),2))
# remove the parameter expID after finishing the automated plot generating


def CreateRankedClusters(expID):
    searchConditions = []
    searchConditions.append(
        ('experimentid', '=', '\'' + str(expID) + '\'')
    )

    # increase window size to become more than a day and observe the difference in the graph
    print('Retrieving Data from Database...')
    data = DAL.DataMethods.Search(
        basicStaypoint.StayPoint, settings.DB_SETTINGS.DATABASE_NAME, searchConditions)

    pointsMatrix = [(data[i].posx, data[i].posy) for i in range(0, len(data))]

    print('Clustering using DBSCAN...')
    db = DBSCAN(eps=settings.DBSCAN_PARAMETERS.RADIUS,
                min_samples=settings.DBSCAN_PARAMETERS.MINIMUM_SAMPLES)
    db.fit(pointsMatrix)
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True

    labels = db.labels_

    distinctLabels = list(set(labels))

    colors = [plt.cm.Spectral(each)
              for each in np.linspace(0, 1, len(distinctLabels))]
    XY = np.array(pointsMatrix)

    print('Filtering Data...')

    # fig, axs = plt.subplots()
    # xRange = np.arange(0, 650)
    # yRange = np.arange(0, 650)
    # axs.plot(xRange, yRange)

    for distinctLabel, color in zip(distinctLabels, colors):
        class_member_mask = (labels == distinctLabel)

        # xy = XY[class_member_mask & ~core_samples_mask]
        # clusterLabel='cluster-' + str(i+1)
        # if distinctLabel == -1:
        #     # Black used for noise.
        #     axs.scatter(xy[:, 0], xy[:, 1], alpha=0.2,edgecolors='none',color=[0, 0, 0, 1])
        # else:
        #     axs.scatter(xy[:, 0], xy[:, 1], alpha=settings.PLOT_SETTINGS.ALPHA_VALUE_NON_CORE,color=color)

        # xy = XY[class_member_mask & core_samples_mask]
        # clusterLabel='cluster-' + str(i+1)
        # pointsAlpha=settings.PLOT_SETTINGS.ALPHA_VALUE_CORE
        # xy = XY[class_member_mask]
        # if distinctLabel == -1:
        #     # Black used for noise.
        #     axs.scatter(xy[:, 0], xy[:, 1], alpha=0.2,
        #                 edgecolors='none', label='noise', color=[0, 0, 0, 1])
        # else:
        #     axs.scatter(xy[:, 0], xy[:, 1], alpha=settings.PLOT_SETTINGS.ALPHA_VALUE_CORE,
        #                 label='cluster-' + str(distinctLabel), color=color)

    globalFilteredPoints = []
    globalFilteredLabels = []
    for i in range(len(labels)):
        lable = labels[i]
        # execlude un-clustered staypoints (lable = -1)
        if(lable >= 0):
            globalFilteredPoints.append(data[i])
            globalFilteredLabels.append(lable)

    rankedClusters = rankingManager.RankStayPoints(
        globalFilteredPoints, globalFilteredLabels)

    # print('expID= ' + str(expID))
    for cluster in rankedClusters:
        cluster.experiermentId = expID
    #     print('label: ' + str(cluster.label) + ', pointsCount: ' + str(cluster.pointsCount) + ', totalTime_seconds: ' + str(cluster.totalTime.total_seconds())+', rankingDegree: ' + str(cluster.rankingDegree))
    # print('\n\n')
    # claculate the mean center of each cluster
    # consider clusters that have their centers within the threshold settings.RANKING_SETTINGS.CLUSTER_CENTER_THRESHOLD
    CalculateClustersMeanCenter(rankedClusters)

    return rankedClusters


def ComputeClusterDifferences(allClusters):
    # use dbscan again to cluster the center points of each cluster then compare them
    # centerPointsMatrix = [(allClusters[i].MeanCenterPoint[0],
    #                        allClusters[i].MeanCenterPoint[1]) for i in range(0, len(allClusters))]
    centerPointsMatrix = [(allClusters[i].MeanCenterPoint)
                          for i in range(0, len(allClusters))]

    db = DBSCAN(eps=settings.DBSCAN_PARAMETERS.CLUSTER_RADIUS,
                min_samples=settings.DBSCAN_PARAMETERS.CLUSTER_MINIMUM_SAMPLES)
    db.fit(centerPointsMatrix)
    labels = db.labels_

    distinctLabels = list(set(labels))

    clusterCategories = []

    if len(distinctLabels) == 0:
        print('no labels for the current category settings')
        return

    for i in range(0, len(distinctLabels)):
        distinctLabel = distinctLabels[i]

        if distinctLabel < 0:
            continue

        clusterCategories.append(rankingManager.ClusterCategory(distinctLabel))

    for i in range(0, len(labels)):
        label = labels[i]
        if label < 0:
            continue

        # fill each cluster into the corresponding dictionary ([0] = label)
        for j in range(len(clusterCategories)):
            if clusterCategories[j].label == label:
                clusterCategories[j].clusters.append(allClusters[i])

    result = ''
    result2 = ''#\begin{table}[]\centering\caption{test caption}\label{tab:my-table}\resizebox{\textwidth}{!}{%\begin{tabular}{lllll}'
    for i in range(0, len(clusterCategories)):
        category = clusterCategories[i]
        result += 'category ' + \
            str(category.label) + ' has ' + \
            str(len(category.clusters)) + ' clusters:\n'
        categoryMeanCenter = CalculateCategoryMeanCenter(category)
        result2 += '\nFor the category '+str(category.label)+', category mean center: '+str(categoryMeanCenter)+' in table \\ref{tab:tbl-cat-'+str(category.label)+'}, we can see that it has '+str(len(category.clusters))+' clusters. \n' 
        result2 += '\\begin{table}[htb] \n \\centering \n \\caption{ Clustering Category: '+str(category.label)+'} \n \\label{tab:tbl-cat-'+str(category.label)+'} \n \\begin{tabular}{c|c|c|c|c} \n Cluster Local Label & Date & StayPoints Count & Cluster Mean Center & Cluster Distance From Category Mean Center \\\\ \n'
        for j in range(0, len(category.clusters)):
            cluster = category.clusters[j]
            format = "%d/%m/%Y"
            result += '         Date: ' + cluster.stayPoints[0].arrivaltime.strftime(format) + GetDayName(cluster.stayPoints[0].arrivaltime) + ' Local DBSCAN label: ' + str(cluster.label) + ' pointsCount: ' + str(cluster.pointsCount) + ' center: ' + str(cluster.MeanCenterPoint) +  '\n'
            result2 += str(cluster.label) + ' & ' + cluster.stayPoints[0].arrivaltime.strftime(format) + ' & ' + str(cluster.pointsCount) + ' & ' + str(cluster.MeanCenterPoint) +  ' & ' + str(CalculateMeanCenterDistance(cluster.MeanCenterPoint,categoryMeanCenter)) + ' \\\\ \n '
        result += '--------------------------------------------------\n\n'
        result2 += '\\end{tabular}\\end{table} \n'

        
    print(result)
    print('++++++++++++++++++++++++++++++++++++++++++++++++++++')
    print(result2)

    #plotting categories
    #this condition to disable plotting categories
    if(False):
        core_samples_mask = np.zeros_like(labels, dtype=bool)
        core_samples_mask[db.core_sample_indices_] = True

        data = [(allClusters[i].MeanCenterPoint[0],
                           allClusters[i].MeanCenterPoint[1]) for i in range(0, len(allClusters))]
        data = np.array(data)
        colors = [plt.cm.Spectral(each)
            for each in np.linspace(0, 1, len(distinctLabels))]
        fig, axs = plt.subplots()
        for k, col in zip(distinctLabels, colors):
            if k == -1:
                # Black used for noise.
                col = [0, 0, 0, 1]

            class_member_mask = (labels == k)
            plotLabel = 'Noise'
            if(k>-1):
                plotLabel = 'Category '+ str(k)
            xy = data[class_member_mask & core_samples_mask]
            axs.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col), markeredgecolor='k', markersize=14)

            xy = data[class_member_mask & ~core_samples_mask]
        
            axs.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),markeredgecolor='k', markersize=6,label=plotLabel)
    
        xRange = np.arange(0, 650)
        yRange = np.arange(0, 650)
        axs.plot(xRange, yRange)
        axs.invert_yaxis()
        axs.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
        axs.set_aspect('equal', adjustable='box')
        plt.show()
    
    #calculate mean center for categories



def main():
    allClusters = []
    for i in range(699, 729):
        # for i in range(713, 716):
        allClusters.extend(CreateRankedClusters(i))

    ComputeClusterDifferences(allClusters)


if __name__ == "__main__":
    main()
