# coding=utf-8
from __future__ import division
import math

WEB_MERCATOR_COORDINATE_RANGE = (-20037508.3427892, 20037508.3427892)
WEB_MERCATOR_LENGTH_HALF = 20037508.3427892

PI = math.pi
x_PI = PI * 3000.0 / 180.0
a = 6378245.0  # 长半轴
f = 0.00669342162296594323  # 扁率

Math = math
Math.abs = Math.fabs


# 百度坐标系 (BD-09) 与 火星坐标系 (GCJ-02)的转换
def bd09_to_gcj02(lng, lat):
    x = lng - 0.0065
    y = lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_PI)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_PI)

    transformed = [0, 0]
    transformed[0] = z * math.cos(theta)
    transformed[1] = z * math.sin(theta)
    return transformed;


# 火星坐标系 (GCJ-02) 与百度坐标系 (BD-09) 的转换
def gcj02_to_bd09(lng, lat):
    z = Math.sqrt(lng * lng + lat * lat) + 0.00002 * Math.sin(lat * x_PI)
    theta = Math.atan2(lat, lng) + 0.000003 * Math.cos(lng * x_PI)
    transformed = [0, 0]
    transformed[0] = z * Math.cos(theta) + 0.0065
    transformed[1] = z * Math.sin(theta) + 0.006
    return transformed


# WGS84 转 GCj02

def wgs84_to_gcj02(lng, lat):
    if out_of_china(lng, lat):
        return [lng, lat]

    dlat = transform_latitude(lng - 105.0, lat - 35.0)
    dlng = transfor_longitude(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * PI
    magic = Math.sin(radlat)
    magic = 1 - f * magic * magic
    sqrtmagic = Math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - f)) / (magic * sqrtmagic) * PI)
    dlng = (dlng * 180.0) / (a / sqrtmagic * Math.cos(radlat) * PI)
    transformed = [0, 0]
    transformed[0] = lng + dlng
    transformed[1] = lat + dlat
    return transformed


# GCJ02 转 WGS84
def gcj02_to_wgs84(lng, lat):
    if out_of_china(lng, lat):
        return [lng, lat]

    dLat = transform_latitude(lng - 105.0, lat - 35.0)
    dLon = transfor_longitude(lng - 105.0, lat - 35.0)
    radLat = lat / 180.0 * PI
    magic = Math.sin(radLat)
    magic = 1 - f * magic * magic
    sqrtMagic = Math.sqrt(magic)
    dLat = (dLat * 180.0) / ((a * (1 - f)) / (magic * sqrtMagic) * PI)
    dLon = (dLon * 180.0) / (a / sqrtMagic * Math.cos(radLat) * PI)
    mgLat = lat + dLat
    mgLon = lng + dLon
    transformed = [0, 0]
    transformed[0] = lng * 2 - mgLon
    transformed[1] = lat * 2 - mgLat
    return transformed


# WGS84 转 BD-09
def wgs84_to_bd09(lng, lat):
    lngLatGcj02 = wgs84_to_gcj02(lng, lat)
    return gcj02_to_bd09(lngLatGcj02[0], lngLatGcj02[1])


# BD-09 转 WGS84
def bd09_to_wgs84(lng, lat):
    lngLatGcj02 = bd09_to_gcj02(lng, lat)
    return gcj02_to_wgs84(lngLatGcj02[0], lngLatGcj02[1])


def transform_latitude(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * Math.sqrt(
        Math.abs(lng))
    ret += (20.0 * Math.sin(6.0 * lng * PI) + 20.0 * Math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret += (20.0 * Math.sin(lat * PI) + 40.0 * Math.sin(lat / 3.0 * PI)) * 2.0 / 3.0
    ret += (160.0 * Math.sin(lat / 12.0 * PI) + 320 * Math.sin(lat * PI / 30.0)) * 2.0 / 3.0
    return ret


def transfor_longitude(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * Math.sqrt(
        Math.abs(lng))
    ret += (20.0 * Math.sin(6.0 * lng * PI) + 20.0 * Math.sin(2.0 * lng * PI)) * 2.0 / 3.0
    ret += (20.0 * Math.sin(lng * PI) + 40.0 * Math.sin(lng / 3.0 * PI)) * 2.0 / 3.0
    ret += (150.0 * Math.sin(lng / 12.0 * PI) + 300.0 * Math.sin(lng / 30.0 * PI)) * 2.0 / 3.0
    return ret


def out_of_china(lng, lat):
    if lng < 72.004 or lng > 137.8347:
        return True
    elif lat < 0.8293 or lat > 55.8271:
        return True
    return False


def lnglat_to_webmercator(lnglat):
    localMapPoint = [0, 0]
    localMapPoint[0] = lnglat[0] * WEB_MERCATOR_LENGTH_HALF / 180
    localMapPoint[1] = Math.log(Math.tan((90 + lnglat[1]) * PI / 360)) / (PI / 180) * (
            WEB_MERCATOR_LENGTH_HALF / 180)
    return localMapPoint


def webmercator_to_lnglat(point):
    lnglat = [0, 0]
    lnglat[0] = point[0] / WEB_MERCATOR_LENGTH_HALF * 180
    lnglat[1] = point[1] / WEB_MERCATOR_LENGTH_HALF * 180
    lnglat[1] = 180 / PI * (2 * Math.atan(Math.exp(lnglat[1] * PI / 180)) - PI / 2)
    return lnglat


def webmercator_to_image(point, level, tilesize):
    img_size = 2 ** level * tilesize
    img_point = [0, 0]
    img_point[0] = (point[0] + WEB_MERCATOR_LENGTH_HALF) / (WEB_MERCATOR_LENGTH_HALF * 2) * img_size
    img_point[1] = (-point[1] + WEB_MERCATOR_LENGTH_HALF) / (
            WEB_MERCATOR_LENGTH_HALF * 2) * img_size
    return img_point


def image_to_webmecator(img_point, level, tilesize):
    img_size = 2 ** level * tilesize
    wm_point = [0, 0]
    wm_point[0] = img_point[0] / img_size * (
            WEB_MERCATOR_LENGTH_HALF * 2) - WEB_MERCATOR_LENGTH_HALF
    wm_point[1] = -(img_point[1] / img_size * (
            WEB_MERCATOR_LENGTH_HALF * 2) - WEB_MERCATOR_LENGTH_HALF)
    return wm_point


# lnglat project point to image point
def lnglat_projecion_to_image(point, level, tilesize):
    img_height = 2 ** (level - 1) * tilesize
    img_width = img_height * 2
    img_point = [0, 0]
    img_point[0] = (point[0] + 180) / 360 * img_width
    img_point[1] = (-point[1] + 90) / 180 * img_height
    return img_point


def image_to_lnglat_projection(img_point, level, tilesize):
    img_height = 2 ** (level - 1) * tilesize
    img_width = img_height * 2
    lnglat_point = [0, 0]
    lnglat_point[0] = img_point[0] / img_width * 360 - 180
    lnglat_point[1] = -(img_point[1] / img_height * 180 - 90)
    return lnglat_point


if __name__ == "__main__":
    lnglatWgs84 = [116.40387397, 39.91488908]
    lnglatGcj02 = wgs84_to_gcj02(lnglatWgs84[0], lnglatWgs84[1])
    lnglatBd09 = gcj02_to_bd09(lnglatGcj02[0], lnglatGcj02[1])
    print("wgs84:" + str(lnglatWgs84))
    print("gcj02:" + str(lnglatGcj02))
    print("bd09:" + str(lnglatBd09))
    print()
    print("wgs84ToGcj02:" + str(lnglatGcj02))
    print("gcj02ToWgs84:" + str(gcj02_to_wgs84(lnglatGcj02[0], lnglatGcj02[1])))
    print()
    print("gcj02ToBd09:" + str(lnglatBd09))

    print()
    print("wgs84ToBd09:" + str(wgs84_to_bd09(lnglatWgs84[0], lnglatWgs84[1])))
    print("bd09ToGcj02:" + str(bd09_to_gcj02(lnglatBd09[0], lnglatBd09[1])))
    print("bd09ToWgs84:" + str(bd09_to_wgs84(lnglatBd09[0], lnglatBd09[1])))

    print()
    print("lngLat2WebMercatorPoint:" + str(lnglat_to_webmercator(lnglatGcj02)))
    print(
            "WebMercatorPoint2Lnglat:" + str(
        webmercator_to_lnglat(lnglat_to_webmercator(lnglatGcj02))))

    print("lnglat_to_image:" + str(lnglat_projecion_to_image((-180, 90), 1, 256)))
