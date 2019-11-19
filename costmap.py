#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 2 13:57:11 2019

@author: qiaoran li
@author: sudheeksha garg
@content: HW09 - PCA
@prof: Dr. Kinsman
@due: 4/21/2019
"""


def generate_kml_tags(centroids, color, description):
    """
    generating the kml tags given the coordinates, color and description
    :param centroids: centroid of the agglomerated stop or turn coordinates
    :param color: the color of the kml tags
    :param description: the description of the kml file
    :return: kml tags in string format
    """

    if description == 'Stop Signs':
        style = ''
    elif description == 'Right Turn':
        style = "<Style id=\"greenStyle\"> \
                <IconStyle> \
                <Icon> \
                <href> http://maps.google.com/mapfiles/kml/pushpin/grn-pushpin.png</href> \
                </Icon> \
                </IconStyle> \
                </Style> "
    else:
        style = "<Style id=\"redStyle\"> \
                <IconStyle> \
                <Icon> \
                <href> http://maps.google.com/mapfiles/kml/pushpin/red-pushpin.png</href> \
                </Icon> \
                </IconStyle> \
                </Style> "

    created_tags = ''

    for c in centroids:
        created_tags += "<Placemark>" + style + " <Point><coordinates>" + str(c[0]) + "," + str(c[1]) + "," + str(0) \
        + "</coordinates></Point></Placemark>\n"

    return created_tags


def detect_turns(df):
    """
    Detect the left and right turns based on a threshold classifier
    :param df: the processed data frame
    :return: lists of turns
    """

    # book-keeping
    left_turns_list = []
    right_turns_list = []

    # increment the slow pointer 15 point at a time
    for slow_pt in range(0, df.shape[0], 15):

        fast_pt = slow_pt + 1 # update the fast point

        # increment the fast pointer if not at the end or 15 step
        # further than the slow pointer
        while (fast_pt < df.shape[0] and fast_pt != slow_pt + 14):

            # obtain the attributes at both pointers
            previous_angle = df.iloc[fast_pt]['track_true']
            current_angle = df.iloc[slow_pt]['track_true']
            longitude = df.iloc[fast_pt]['lon']
            latitude = df.iloc[fast_pt]['lat']
            speed = df.iloc[fast_pt]['speed_Kn']

            # detect left turns
            if (-50 >= (previous_angle - current_angle) >= -90):
                left_turns_list.append([longitude, latitude, speed])
            # detect right turns
            elif (100 >= (current_angle - previous_angle) >= 40):
                right_turns_list.append([longitude, latitude, speed])

            fast_pt += 1 # increment the fast pointer

    return left_turns_list, right_turns_list


def time_in_hours(time):
    """
    convert utc time to hour format
    :param time: time in utc format
    :return: time in hour format
    """
    time = float(time)
    minutes = int((time - int(time / 10000) * 10000) / 100)
    seconds = int(time - int(time / 100) * 100)
    hour = int(time / 10000)
    result = hour + minutes / float(60) + seconds / float(360)
    return result*3600


def time_difference(start_time, end_time):
    """
    compute the absolute duration between 2 times
    :param start_time: time 1
    :param end_time: time 2
    :return: duration
    """
    return abs(time_in_hours(end_time) - time_in_hours(start_time))


def detect_stops(df):
    """
    threshold classifier detect stops
    :param df: the processed dataframe
    :return: stops in kml tags, stops in numpy array
    """

    # book-keeping variables
    stop_lights_list = []
    slow_pt, fast_pt = 0, 0

    # iterate the slow point as long as it is not at the end
    while slow_pt < df.shape[0]:

        # initialize the time variables
        start_time, end_time = -1, -1

        # update the start time with slow pointer if it's < 10 mph
        if df.iloc[slow_pt]['speed_Kn'] <= 10:
            start_time = df.iloc[slow_pt]['utc']
        else:
            slow_pt += 1
            continue

        # increment the faster point as long the data point speed < 10mph, and update the end time
        for fast_pt in range(slow_pt+1, df.shape[0]):
            if df.iloc[fast_pt]['speed_Kn'] <= 10:
                end_time = df.iloc[fast_pt]['utc']
            else:
                break

        # compute the time duration between the 2 times
        duration = time_difference(end_time = end_time, start_time = start_time)

        # if the duration is less than 30 second, record the stopping coordinate
        if duration >= 30:
            stop_lights_list.append([df.iloc[fast_pt-1]['lon'], df.iloc[fast_pt-1]['lat'], df.iloc[fast_pt-1]['speed_Kn']])

        # update the slow point for next windowing
        slow_pt = fast_pt + 1

    point_lines = ''
    for index in range(0, len(stop_lights_list)):
        point_lines += "<Placemark> <Point><coordinates>"+str(stop_lights_list[index]).strip('[]')+ "</coordinates></Point></Placemark>\n"

    return point_lines, stop_lights_list
