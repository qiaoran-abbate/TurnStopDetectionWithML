#!interpreter [optional-arg]
# -*- coding: utf-8 -*-

"""
{Description}
{License_info}
"""

# Futures
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster import hierarchy
from sklearn.neighbors import kneighbors_graph
from collections import defaultdict

# Built-in/Generic Imports
import os
import sys
import pickle

# Libs
import pandas as pd  # Or any other
import numpy as np
import matplotlib.pyplot as plt


# Own modules
import GPS_Data_Project_by_Li_Garg
import costmap

__author__ = 'Qiaoran Li, Sudheeksha Garg'
__copyright__ = 'Copyright 2019, GPS Data Visualization'
__version__ = '0.1.0'
__email__ = 'qxl8365@rit.edu'


def compute_cluster_centroids(numpy_array, labels):
    """
    compute the centroids of agglomerative clusters
    :param numpy_array: the data set
    :param labels: the label for the data set
    :return: list of centroids
    """

    # key: label
    # value: [points, points ... ]
    clusters = defaultdict(list)
    centroids = []

    # populate the clusters by key
    for index in range(len(labels)):
        clusters[labels[index]].append(numpy_array[index])

    # compute the means for each clusters
    for label, points in clusters.items():
        c = np.mean(points, axis=0)
        centroids.append(c)

    return centroids


def perform_clustering(X, connectivity, title,  num_clusters=130, linkage='single'):
    """
    perform the agglomerate clustering, and visualize the clusters in scatter-plot
    :param X: the dataset containing the coordinates
    :param connectivity: the k-nearest neighbor graph
    :param title: the title of the plot
    :param num_clusters: number of clusters for agg
    :param linkage: the linkage method for agg
    :return: a list of centroids.
    """

    plt.figure()
    model = AgglomerativeClustering(linkage=linkage, connectivity=connectivity, n_clusters=num_clusters)
    model.fit(X)

    # extract labels
    labels = model.labels_

    # compute the centroids for each cluster
    centroids = compute_cluster_centroids(X, labels)

    # plot the centroids
    for c in centroids:
        # plot the points belong to the current cluster
        plt.scatter(c[0], c[1], s=1)

    plt.title(title)
    plt.ylabel('Latitude')
    plt.xlabel('Longitude')
    plt.show()

    return centroids


def do_clustering(numpy_array, title):
    """
    compute the dendrogram, connectivity, and then call the clustering algorithm.
    :param numpy_array: the dataset containing the coordinates
    :param title: title of the plot
    :return: list of centroids
    """

    # dendrogram stuff
    z = hierarchy.linkage(numpy_array, 'single')
    plt.figure()
    dn = hierarchy.dendrogram(z)
    plt.show()

    # clustering stuff
    connectivity = kneighbors_graph(numpy_array, 3, include_self=False)
    centroids = perform_clustering(numpy_array, connectivity, title)

    return centroids


def remove_stop_that_are_turns(stop_light_list, right_light_list, left_light_list):
    """
    iterative algorithms that remove stops that are turns.
    :param stop_light_list: list of stops
    :param right_light_list: list of right turns
    :param left_light_list: list of left turns
    :return: new stop list
    """

    i = 0
    # loop through the stop list, if stop is with in 0.03 miles of radius of a left turn, remove it
    while i < len(stop_light_list):
        i_list = stop_light_list[i]
        lon1 = i_list[0]
        lat1 = i_list[1]
        for j in range(0, len(left_light_list)):
            j_list = left_light_list[j]
            lon2 = j_list[0]
            lat2 = j_list[1]
            if GPS_Data_Project_by_Li_Garg.haversine((lat1, lon1), (lat2, lon2)) <= 0.03:
                del stop_light_list[i]
                i = i - 1
                continue
        i = i + 1

    i = 0
    # loop through the stop list, if stop is with in 0.03 miles of radius of a right turn, remove it
    while i < len(stop_light_list):
        i_list = stop_light_list[i]
        lon1 = i_list[0]
        lat1 = i_list[1]
        for j in range(0, len(right_light_list)):
            j_list = right_light_list[j]
            lon2 = j_list[0]
            lat2 = j_list[1]
            if GPS_Data_Project_by_Li_Garg.haversine((lat1, lon1), (lat2, lon2)) <= 0.03:
                del stop_light_list[i]
                i = i - 1
                continue
        i = i + 1
    return stop_light_list


def main():

    global_stop_list = []
    global_right_list = []
    global_left_list = []

    fname = "global_stop_list.p"

    if os.path.isfile(fname):
        global_stop_list = pickle.load(open(fname, "rb" ))
        global_right_list = pickle.load(open(fname.replace('stop', 'right'), "rb"))
        global_left_list = pickle.load(open(fname.replace('stop', 'left'), "rb"))
    else:
        path = '../gps_data'

        for file in os.listdir(path):
            current = os.path.join(path, file)
            if os.path.isfile(current):
                if current.endswith(('.TXT', '.txt')):
                    # print(current)
                    stop_lights_list, left_turn_list, right_turn_list = GPS_Data_Project_by_Li_Garg.test(current)

                    global_stop_list += stop_lights_list
                    global_right_list += right_turn_list
                    global_left_list += left_turn_list

        global_stop_list = np.array(global_stop_list)
        global_right_list = np.array(global_right_list)
        global_left_list = np.array(global_left_list)

        # save the list objects to prevent recomputation
        pickle.dump(global_stop_list, open(fname, "wb"))
        pickle.dump(global_right_list, open(fname.replace('stop', 'right'), "wb"))
        pickle.dump(global_left_list, open(fname.replace('stop','left'), "wb"))


    # take just the longitute and latitute attributes
    global_stop_list = global_stop_list[:, 0:2]
    global_right_list = global_right_list[:, 0:2]
    global_left_list = global_left_list[:, 0:2]

    # remove duplicated coordinates
    # global_stop_list = np.unique(global_stop_list, axis=0)
    # global_right_list = np.unique(global_right_list, axis=0)
    # global_left_list = np.unique(global_left_list, axis=0)

    # do the clustering
    stop_centroids = do_clustering(global_stop_list, 'Stop Signs')
    right_centroids = do_clustering(global_right_list, 'Right Turn')
    left_centroids = do_clustering(global_left_list, 'Left Turn')

    # if a stop sign and a turn are close in proximity, then remove the stop sign
    stop_centroids = remove_stop_that_are_turns(stop_centroids, right_centroids, left_centroids)

    # create kml tags
    stop_centroids_in_kml_tags = costmap.generate_kml_tags(stop_centroids, '6414F0FA', 'Stop Signs')
    right_centroids_in_kml_tags = costmap.generate_kml_tags(right_centroids, '6400FF14', 'Right Turn')
    left_centroids_in_kml_tags = costmap.generate_kml_tags(left_centroids, 'ff0000ff', 'Left Turn')

    # create kml files
    GPS_Data_Project_by_Li_Garg.create_kml('Stop Signs' + '.kml', '', stop_centroids_in_kml_tags)
    GPS_Data_Project_by_Li_Garg.create_kml('Right Turn' + '.kml', '', right_centroids_in_kml_tags)
    GPS_Data_Project_by_Li_Garg.create_kml('Left Turn' + '.kml', '', left_centroids_in_kml_tags)


if __name__ == '__main__':
    main()