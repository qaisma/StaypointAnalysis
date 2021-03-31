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
    cmap = get_cmap(len(distinctLabels))
    colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(distinctLabels))]
    XY = np.array(pointsMatrix)

    print('Filtering Data...')
    i=0
    fig, axs = plt.subplots()
    xRange= np.arange(0,650)
    yRange= np.arange(0,650)
    axs.plot(xRange,yRange)

    for distinctLabel, color in zip(distinctLabels, colors):
        i+=1
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
        xy = XY[class_member_mask]
        if distinctLabel == -1:
            # Black used for noise.
            axs.scatter(xy[:, 0], xy[:, 1], alpha=0.2,edgecolors='none',label='noise',color=[0, 0, 0, 1])
        else:
            axs.scatter(xy[:, 0], xy[:, 1], alpha=settings.PLOT_SETTINGS.ALPHA_VALUE_CORE,label='cluster-' + str(distinctLabel),color=color)

    axs.legend(loc='center left', bbox_to_anchor=(1.0, 0.5),prop=dict(size=7))
    axs.set_xlabel('X-Axis', fontsize=settings.PLOT_SETTINGS.FONTSIZE)
    axs.set_ylabel('Y-Axis', fontsize=settings.PLOT_SETTINGS.FONTSIZE)
    axs.invert_yaxis()
    axs.set_aspect('equal', adjustable='box')

    plotTitle = 'Date: ' + str(data[0].arrivaltime) + ' (' + \
        GetDayName(data[len(data)-1].leavetime) + ') | Points count: ' + str(len(data))

    plotTitle += ' | Radius= ' + str(settings.DBSCAN_PARAMETERS.RADIUS) + \
        ' | Min samples= ' + str(settings.DBSCAN_PARAMETERS.MINIMUM_SAMPLES)

    plt.title(plotTitle, fontsize=5)
    print('saving plot...')
    dirName=os.path.dirname(os.path.abspath(__file__)) + '/plots/'
    dirName +='SPAnalyze/'
    if not (os.path.isdir(dirName)):
        os.makedirs(dirName)

    filename=str(expID) + '_'+str(datetime.now()).replace(':', '_').replace('.', '_') + '.png'

    plt.tight_layout()
    plt.savefig(dirName + filename, dpi=800, format='png')
    
    #clears the entire current figure
    plt.clf()
    plt.close('all')



def main():
    for i in range(277, 309):
        StartApplication(i)


if __name__ == "__main__":
    main()
