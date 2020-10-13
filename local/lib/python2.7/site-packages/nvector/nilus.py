'''
Created on 27. feb. 2017

@author: pab
'''

import numpy as np
import nvector as nv


def main():
    wgs84 = nv.FrameE(name='WGS84')
    distance = 7000

    # sensor pos
    N5 = wgs84.GeoPoint(59.4668193, 10.5243751, degrees=True)
    N9 = wgs84.GeoPoint(59.4687048, 10.5254233, degrees=True)

    # print("node;pos")
    # print("NILUS5;POINT({} {})".format(N5.longitude_deg, N5.latitude_deg))
    # print("NILUS9;POINT({} {})".format(N9.longitude_deg, N9.latitude_deg))

    # sensor bearing reports
    N5_bearings = [140.82275390625]
    N9_bearings = [-32.684326171875, 152.545166015625]

    # create points from bearings and distance
    B1 = N5.geo_point(distance, N5_bearings[0], degrees=True)[0]
    B2 = N9.geo_point(distance, N9_bearings[0], degrees=True)[0]
    B3 = N9.geo_point(distance, N9_bearings[1], degrees=True)[0]

    # create paths from points
    N5B1 = nv.GeoPath(N5, B1)
    N9B2 = nv.GeoPath(N9, B2)
    N9B3 = nv.GeoPath(N9, B3)

    # do intersect on paths
    I1 = N5B1.intersect(N9B2)
    I2 = N5B1.intersect(N9B3)

    print("INTER1;POINT({} {})".format(I1.longitude_deg, I1.latitude_deg))
    print("INTER2;POINT({} {})".format(I2.longitude_deg, I2.latitude_deg))

    # print("node;line")
    # print("N5B1;LINESTRING({} {}, {} {})".format(N5B1.positionA.latitude_deg, N5B1.positionA.longitude_deg,
    #                                              N5B1.positionB.latitude_deg, N5B1.positionB.longitude_deg))
    # print("N9B2;LINESTRING({} {}, {} {})".format(N9B2.positionA.latitude_deg, N9B2.positionA.longitude_deg,
    #                                              N9B2.positionB.latitude_deg, N9B2.positionB.longitude_deg))
    # print("N9B3;LINESTRING({} {}, {} {})".format(N9B3.positionA.latitude_deg, N9B3.positionA.longitude_deg,
    #                                              N9B3.positionB.latitude_deg, N9B3.positionB.longitude_deg))

    # check intersect point using bearing and distance as input
    def check_path_intersect(origin_point, intersect_point, bearing, distance):
        s_AB, _azia, _azib = origin_point.distance_and_azimuth(intersect_point)
        return distance >= s_AB and np.all(
            np.sign([np.rad2deg(_azia), bearing]) == 1)

    # check intersect point using only path and intersect point as input
    def check_path_intersect2(path, point):
        b_AB, b_azia, b_azib = path.positionA.distance_and_azimuth(path.positionB)
        i_AB, i_azia, i_azib = path.positionA.distance_and_azimuth(point)
        return b_AB >= i_AB and np.all(
            np.sign([np.rad2deg(i_azia), b_azia]) == 1)

    # check if the intersect point lies on the path
    x = check_path_intersect2(N5B1, I1) and check_path_intersect2(N9B2, I1)
    print("I1 is %s" % str(x))
    x = check_path_intersect2(N5B1, I2) and check_path_intersect2(N9B3, I2)
    print("I2 is %s" % str(x))

    x = N5B1.on_path(I1) and N9B2.on_path(I1)
    print("I1 is %s with on_path" % str(x))
    x = N5B1.on_path(I2) and N9B3.on_path(I2)
    print("I2 is %s with on_path" % str(x))

    # same thing different input parameters
    # (check_path_intersect(N5, I1, N5_bearings[0], distance) and
    #  check_path_intersect(N9, I1, N9_bearings[0], distance))
    # (check_path_intersect(N5, I2, N5_bearings[0], distance) and
    #  check_path_intersect(N9, I2, N9_bearings[1], distance))


if __name__ == '__main__':
    main()
