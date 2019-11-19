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
import csv
import sys
import os
import pandas as pd
import numpy as np
from haversine import haversine
import costmap


kml_file_name = ''


def read_data(file_name):
    """
    the function reads a dataset from a csv file
    :param file_name: name of the csv file
    :return: dataframe with values from the csv file
    """
    gps_data = None
    try:
        gps_data = csv.reader(open(file_name), delimiter=',')
        # gps_data = pd.DataFrame(gps_data)
    except FileNotFoundError:
        print(file_name + "not found, please check again.")
        sys.exit()
    return gps_data


def get_haversion(pos1, pos2):
    haver = haversine(pos1, pos2, unit='mi')
    return haver


def initialize(train_file_name):
    """
    initialize the file
    :param train_file_name:
    :return:
    """
    gps_data = read_data(train_file_name)

    # create dataframe and extract only the necessary columns
    twodArray = []
    for row in gps_data:
        if len(row) != 0:
            # -------------------------------------------------------------------------------------------------------------
            #  The Arduino sometimes burps, and writes two GPS sentences to the same line of the data file.
            #  You must detect and ignore these anomalies. Otherwise it looks like the car jumps from one side of the
            #  planet to the other side.
            # -------------------------------------------------------------------------------------------------------------
            # take the first entry if there are 2 entries per line and A represent valid data points
            if row[0] == '$GPRMC' and row[2] == 'A' and len(row) == 13:
                # print(row[2])
                twodArray.append(row[:13])

    # $GPRMC,233554.400,A,4305.1642,N,07740.8665,W,0.01,195.70,040319,,,D*75
    df = pd.DataFrame(twodArray, columns=['GPRMC', 'utc', 'pos_status', 'lat', 'lat_dir', 'lon', 'lon_dir', 'speed_Kn',
                                          'track_true', 'date', 'mag_var', 'var_dir', 'checksum'])

    # sub_dataframe
    sub_df = df[['lon', 'lat', 'speed_Kn', 'utc', 'pos_status', 'track_true', 'date']]

    # convert the units
    sub_df['lon'] =  -1 * sub_df['lon'].apply(func=cov_nmea_to_decimal_degrees)
    sub_df['lat'] = sub_df['lat'].apply(func=cov_nmea_to_decimal_degrees)
    sub_df['speed_Kn'] = sub_df['speed_Kn'].apply(func=cov_knot_to_mile_per_hour)
    sub_df['utc'] = sub_df['utc'].apply(lambda x: float(x))
    sub_df['track_true'] = sub_df['track_true'].apply(lambda x: float(x))

    # create the kml file names
    kml_file_name = train_file_name.replace('.txt', '.kml')
    kml_file_name = kml_file_name.replace('.TXT', '.kml')
    kml_file_name = kml_file_name.replace('../gps_data', '../gen_kmls')

    # return the results
    return sub_df, kml_file_name


def cov_knot_to_mile_per_hour(measure):
    return float(measure) * 1.15078


def cov_nmea_to_decimal_degrees(measure):
    """
    https://www.raspberrypi.org/forums/viewtopic.php?t=175163
    :param measure: measures in nmea format
    :return: measure in degree format
    """
    DD = int(float(measure)/100)
    SS = float(measure)-DD*100
    measure_in_degree = DD + SS/60

    return round(measure_in_degree, 6)


def create_kml(filename, coordinates, points):
    """
    This function create the kml file
    :param filename: the filename needed for kml
    :param coordinate_list: the coordinate list needed for the file
    :return:
    """
    print(filename)

    f = open(filename, 'a')

    f.write("<?xml version='1.0' encoding='UTF-8'?>\n "
            "<kml xmlns='http://www.opengis.net/kml/2.2'> \n"
            "\t   <Document>\n"
            "\t\t       <name> Paths for KML file </name>\n"
            "\t\t       <description>" + filename + "</description> \n "
            "\t\t       <Style id='yellowLineGreenPoly'>\n "
            "\t\t\t           <LineStyle> \n "
            "\t\t\t\t               <color>7f00ffff</color> \n"
            "\t\t\t\t               <width>4</width> \n"
            "\t\t\t           </LineStyle>\n "
            "\t\t\t           <PolyStyle> \n "
            "\t\t\t\t               <color>7f00ff00</color> \n "
            "\t\t\t           </PolyStyle> \n "
            "\t\t       </Style> \n "
            "\t\t       <Placemark>\n"
            "\t\t\t           <name> 2019_03_04_RIT_to_Home </name>\n "
            "\t\t\t           <description> kml file for 2019_03_04_RIT_to_Home </description>\n"
            "\t\t\t           <styleUrl>#yellowLineGreenPoly</styleUrl>\n "
            "\t\t\t           <LineString> \n "
            "\t\t\t\t               <extrude>1</extrude>\n"
            "\t\t\t\t               <tessellate>1</tessellate>\n"
            "\t\t\t\t               <altitudeMode>absolute</altitudeMode>\n")
    f.write("\t\t\t\t               <coordinates>" + coordinates + "\n")
    f.write("\t\t\t\t               </coordinates>\n")
    f.write("\t\t\t           </LineString>\n")
    f.write("\t\t       </Placemark>\n")
    f.write("\t\t\t   " + points + "\n")
    f.write("\t   </Document>\n")
    f.write("</kml>\n")
    f.close()


def process_data(df, file_name):

    # -------------------------------------------------------------------------------------------------------------
    #  The Arduino sometimes loses its mind, and starts recording GPS values that jump all over the place.
    # -------------------------------------------------------------------------------------------------------------
    old_longitude, old_latitude = df.iloc[0]['lon'], df.iloc[0]['lat']
    for index, row in df.iterrows():
        longitude, latitude, speed = row['lon'], row['lat'], row['speed_Kn']
        temp = get_haversion(pos1=[latitude, longitude], pos2=[old_latitude, old_longitude])
        if temp > 5:
            # print(old_latitude, old_longitude, latitude, longitude, temp)
            df.drop(index, inplace=True)
        # book-keeping for the last
        old_longitude = longitude
        old_latitude = latitude

    # -------------------------------------------------------------------------------------------------------------
    #  If the vehicle is parked, you do not need multiple data points at that same location.
    # -------------------------------------------------------------------------------------------------------------
    # create a columns that flags all duplicates as false (except for the 1 occurrence)
    coordinate_duplicate = df.duplicated(subset=['lon', 'lat'], keep='first')
    df['flag'] = coordinate_duplicate
    # drop all the duplicated coordinates, keep the first and last occurrences.
    df = df.drop_duplicates(['lon', 'lat', 'flag'], keep='last')


    # -------------------------------------------------------------------------------------------------------------
    #  If the vehicle is traveling in a straight line, you could ignore some points.
    # -------------------------------------------------------------------------------------------------------------
    # book-keeping variables
    list_of_straight_index = []
    old_speed = df.iloc[0]['speed_Kn']
    # loop through the dataframe
    for index, row in df.iterrows():
        speed = row['speed_Kn']
        # keep track of the indexes where the speed was constant
        if speed == old_speed:
            list_of_straight_index.append(index)
        else:
            old_speed = speed # update the old speed
    # stepping through the list
    SAMPLE_STEPS = 3 # drop 1 data point for every 3
    for index in range(0, len(list_of_straight_index), 3):
        df.drop(list_of_straight_index[index], inplace=True)


    # -------------------------------------------------------------------------------------------------------------
    # make sure it still has enough data
    # copy the df to perserve the begining and ending for paths
    # -------------------------------------------------------------------------------------------------------------
    if df.shape[0] < 4:  return df, df, False
    df_with_begining_and_ending = df


    # -------------------------------------------------------------------------------------------------------------
    #  When the trip first starts up, the GPS device is not moving. Do not worry about the data points when the
    # vehicle has not started moving yet.
    # -------------------------------------------------------------------------------------------------------------
    first_coordinate = df.iloc[0,:2].tolist()
    second_coordinate = df.iloc[1,:2].tolist()
    if first_coordinate == second_coordinate:
        df = df.drop(df.index[0])

    # -------------------------------------------------------------------------------------------------------------
    # When the vehicle parks, the GPS device stops moving. Do not worry about these non-moving data points
    # at the end of a drive.
    # -------------------------------------------------------------------------------------------------------------
    last_coordinate = df.iloc[-1, :2].tolist()
    second_last_coordinate = df.iloc[-2, :2].tolist()
    if last_coordinate == second_last_coordinate:
        df = df.drop(df.index[-1])
    # -------------------------------------------------------------------------------------------------------------

    # save dataframe to csv for more processes.
    path = '../gen_kmls'
    if not os.path.isdir(path):
        try:
            os.mkdir(path)
        except OSError:
            print("Creation of the directory %s failed" % path)
        else:
            print("Successfully created the directory %s " % path)


    # df_with_begining_and_ending.to_csv(file_name.replace('../gps_data','..').replace('.txt', '') +
    #                                    '_preprocessed.csv', sep=',', encoding='utf-8', index=True)

    return df_with_begining_and_ending, df, True


def get_path_coordinates(df):

    # create the coordinates for kml file as a string
    coordinates = ''

    for index, row in df.iterrows():

        longitude, latitude, speed = row['lon'], row['lat'], row['speed_Kn']

        # # create the list of coordinates
        temp = str(longitude) + ',' + str(latitude) + ',' + str(speed)
        coordinates += temp.replace(' ', '') + ' '

    return coordinates


def test(filename):
    """
    The main function setup test cases and called the associated functions
    :return: None
    """

    # initialize the dataframe, kml filename and path coordinates
    sub_df, kml_file_name = initialize(filename)

    # process the dataframe

    df_with_begining_and_ending, df, bool = process_data(sub_df, filename)

    if bool == True:

        # call the function to get the path coordinates
        coordinates = get_path_coordinates(df)

        # # call the function to get stop points
        stops, stop_lights_list = costmap.detect_stops(df_with_begining_and_ending)
        left_turn_list, right_turn_list = costmap.detect_turns(df_with_begining_and_ending)

        # call the function to create kml files
        create_kml(kml_file_name, coordinates= coordinates, points='')

        print("Finished, Thanks for Using Our Program. ")

        return stop_lights_list, left_turn_list, right_turn_list

    else:
        print("Failed, file not long enough. ")
        return [], [], []


if __name__ == "__main__":
    test_file = '../gps_data/2019_03_04__RIT_to_HOME.TXT'

    if len(sys.argv) == 2:
        test_file = sys.argv[1]

    test(test_file)