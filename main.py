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
import os
def clear(): os.system('cls') #on Windows System

########### --- Context-Aware Window Sizing for Point of Interest Detection in Multi-Purpose Areas --- ###########

def get_cmap(n, name='hsv'):
    '''Returns a function that maps each index in 0, 1, ..., n-1 to a distinct RGB color;
    the keyword argument name must be a standard mpl colormap name.'''
    return plt.cm.get_cmap(name, n)  # 2 ^ n)

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

# remove the parameter expID after finishing the automated plot generating
def StartApplication(expID):
    searchConditions = []
    searchConditions.append(
        # id = later from Golnaz (using research DB)
        ("experimentid", "=", '\'' + str(expID) + '\'')
    )

    # increase window size to become more than a day and observe the difference in the graph
    print('Retrieving Data from Database...')
    data = DAL.DataMethods.Search(
        basicStaypoint.StayPoint, settings.DB_SETTINGS.DATABASE_NAME, searchConditions)  # DAL.Utilities.TableNames.staypoint, searchConditions)

    ################################## 20-11-2020: execluding time windows ######################
    fig, axs = plt.subplots()

    xPoints = [item.posx for item in data]
    yPoints = [item.posy for item in data]

    pointsMatrix = [(xPoints[j], yPoints[j]) for j in range(0, len(xPoints))]
    print('Clustering using DBSCAN...')
    dbscan = DBSCAN(eps=settings.DBSCAN_PARAMETERS.RADIUS,
                    min_samples=settings.DBSCAN_PARAMETERS.MINIMUM_SAMPLES)
    dbscan.fit(pointsMatrix)

    distinctLabels = list(set(dbscan.labels_))
    cmap = get_cmap(len(distinctLabels))
    print('Filtering Data...')
    for i in range(len(distinctLabels)):
            lable = distinctLabels[i]
            # if(lable < 0):
            #     continue
            # get label points
            localXpoints = []
            localYpoints = []
            for j in range(len(dbscan.labels_)):
                if(dbscan.labels_[j] == lable):
                    localXpoints.append(pointsMatrix[j][0])
                    localYpoints.append(pointsMatrix[j][1])
            if(lable < 0):
                axs.scatter(localXpoints, localYpoints, alpha=0.03,
                        label='noise', edgecolors='none', color='black')
            else:
                axs.scatter(localXpoints, localYpoints, alpha=settings.PLOT_SETTINGS.ALPHA_VALUE,
                        label='cluster-' + str(i+1), color=cmap(i))
    # axs.autoscale()
    xRange= np.arange(0,650)
    yRange= np.arange(0,650)
    axs.plot(xRange,yRange)
    axs.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
    axs.set_xlabel('X-Axis', fontsize=settings.PLOT_SETTINGS.FONTSIZE)
    axs.set_ylabel('Y-Axis', fontsize=settings.PLOT_SETTINGS.FONTSIZE)

    # plotTitle = "From: " + str(data[0].arrivaltime) + ' To: '+str(
    #     data[len(data)-1].leavetime) + ' | Points count: ' + str(len(data))
     
    plotTitle = "Date: " + str(data[0].arrivaltime) + ' ('+ \
        GetDayName(data[len(data)-1].leavetime) + ') | Points count: ' + str(len(data))
    plotTitle += " | Radius= " + str(settings.DBSCAN_PARAMETERS.RADIUS) + \
                                     ' | Min samples= ' + \
                                         str(settings.DBSCAN_PARAMETERS.MINIMUM_SAMPLES)
    plt.title(plotTitle, fontsize=5)
    # plt.rcParams['axes.titlesize']=10
    # plt.title(str=plotTitle, dict={'fontsize': 10,'fontweight': rcParams['axes.titleweight'],'verticalalignment': 'baseline', 'horizontalalignment': loc})

    print('saving plot...')
    dirName=os.path.dirname(os.path.abspath(__file__)) + '/plots/'
    #remove after finishing automated scripts
    # dirName += settings.SEARCH_CONDITIONS.FIRST_EXPERIMENT_ID.replace(
    #     '\'', '') + ' to ' + settings.SEARCH_CONDITIONS.LAST_EXPERIMENT_ID.replace('\'', '') + '/'

    #uncomment after finishing automated scripts
    # dirName +='auto/'+str(expID)
    dirName +='auto/'
    if not (os.path.isdir(dirName)):
        os.makedirs(dirName)

    filename=str(datetime.now()).replace(':', '_').replace('.', '_') + '.png'

    plt.tight_layout()
    plt.savefig(dirName + filename, dpi=800, format='png')

    return
    plt.show()
    return
    ################################## 20-11-2020: end of execluding time windows ######################
    print('Diving Data into timewindows...')
    windowslist=timeWindow.DivideIntoTimeWindows(
        data, settings.TIMEWINDOW_PARAMETERS.TIME_UNIT, settings.TIMEWINDOW_PARAMETERS.FREQUENCY)

    print('windows count = ' + str(len(windowslist)))


    fig, axs=plt.subplots()
    # cmap variable is a mapping object for colors ()
    cmap=get_cmap(len(windowslist))

    # these golbal variables are used to aggregate values form each time window
    globalFilteredPoints=[]
    globalFilteredLabels=[]

    # for windows: add points to the global one, make a global array for colors, color for each windows is cmap from len(windows)
    globalColors=[]
    print('Retrieving Data from Database...')
    for i in range(len(windowslist)):
        filteredXPoints=[]
        filteredYPoints=[]
        filteredDbscanLabels=[]

        # collect posX from each staypoint in the time window
        xPoints=[item.posx for item in windowslist[i].stypoints]
        yPoints=[item.posy for item in windowslist[i].stypoints]

        if(len(xPoints) == 0):
            print('window ' + str(i+1) + ' is empty')
            continue

        pointsMatrix=[(xPoints[j], yPoints[j])
                        for j in range(0, len(xPoints))]
        dbscan=DBSCAN(eps=settings.DBSCAN_PARAMETERS.RADIUS,
                        min_samples=settings.DBSCAN_PARAMETERS.MINIMUM_SAMPLES)
        dbscan.fit(pointsMatrix)
        for j in range(len(dbscan.labels_)):
            lable=dbscan.labels_[j]
            # execlude un-clustered staypoints (lable = -1)
            if(lable >= 0):
                filteredXPoints.append(xPoints[j])
                filteredYPoints.append(yPoints[j])
                filteredDbscanLabels.append(str(lable + (i+1)))
                globalFilteredPoints.append(windowslist[i].stypoints[j])
                globalFilteredLabels.append(lable)

        if(len(filteredXPoints) == 0):
            print('no points to be plotted in window: ' + str(i+1))
        else:
            axs.scatter(filteredXPoints, filteredYPoints,
                        alpha=settings.PLOT_SETTINGS.ALPHA_VALUE, label='window-' + str(i+1), c=cmap(i))

    axs.autoscale()
    axs.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
    axs.set_xlabel('X-Axis', fontsize=settings.PLOT_SETTINGS.FONTSIZE)
    axs.set_ylabel('Y-Axis', fontsize=settings.PLOT_SETTINGS.FONTSIZE)
    # temp
    plt.show()

    # ranking staypoints
    # the scope of ranking is among all time windows. it has to be moved into 'for i in range(len(windowslist)):'
    # if we want to make into specific per time window
    print('global labels count: ' + str(len(globalFilteredLabels)))
    print('global SPs count: ' + str(len(globalFilteredPoints)))

    rankedStaypoints=rankingManager.RankStayPoints(
        globalFilteredPoints, globalFilteredLabels)
    for item in rankedStaypoints:
        print('label: ' + str(item.label) + ', pointsCount: ' +
              str(item.pointsCount)+', totalTime_seconds: ' + str(item.totalTime.total_seconds())+', rankingDegree: ' + str(item.rankingDegree))
    # print(rankedStaypoints)



def main():
    result = '\\textbf{Appendix}\n'
    for i in range(1, 30):
        result += '\\begin{figure}[htb]  \\centering  \\includegraphics[width=0.5\\textwidth]{content/images/plots/plottt ('+str(i)+').png }'
        result += '\\caption{Plot '+str(i)+' of Radius 10}\\end{figure}\n'
    clear()
    print(result)
    return
    for i in range(699,702):# 728):
        StartApplication(i)

if __name__ == "__main__":
    main()
