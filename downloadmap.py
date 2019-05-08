# coding=utf-8
from __future__ import division
import sys
import os
from PIL import Image

try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve
import argparse
import geoutil

curdir = os.path.dirname(__file__)
PROJECTION_WM = "wm"
PROJECTION_LL = "lnglat"
TILESIZE = 256


class MapDownload:
    tempfile = os.path.join(curdir, "__temptilefile__.png")

    def geturl(self, level, row, col, scale=1, type="y"):
        if self.projection == PROJECTION_LL:
            return "https://t0.tianditu.gov.cn/img_c/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=img&STYLE=default&TILEMATRIXSET=c&FORMAT=tiles&TILEMATRIX=%d&TILEROW=%d&TILECOL=%d&tk=b34f09c6586e9741629c42f716b7494b" % (
                level, row, col)
        else:
            return "https://mt0.google.cn/maps/vt?lyrs=%s&scale=%s&hl=zh-CN&x=%d&y=%d&z=%d" % (
                type, scale, col, row, level)

    def urllib_download(self, level, row, col, scale=1.0, imgtype="y"):
        url = self.geturl(level, row, col, scale, imgtype)
        print(url)
        urlretrieve(url, self.tempfile)

    def mergetile(self, row, col):
        image = Image.open(self.tempfile)
        width, height = image.size
        if self.mapimg is None:
            self.mapimg = Image.new("RGBA", (width * (self.end[1] - self.start[1] + 1),
                                             height * (self.end[0] - self.start[0] + 1)))
        self.mapimg.paste(image, (width * (col - self.start[1]), height * (row - self.start[0])))

    def __init__(self, level, start, end, projection=PROJECTION_WM, tilesize=TILESIZE, output=None):
        self.level = level
        self.start = start
        self.end = end
        self.mapimg = None
        self.projection = projection
        self.tilesize = tilesize
        self.output = output

    def download(self):
        for row in range(self.start[0], self.end[0] + 1):
            for col in range(self.start[1], self.end[1] + 1):
                self.urllib_download(self.level, row, col, scale=self.tilesize / TILESIZE)
                self.mergetile(row, col)

        if self.output is None:
            path = "%s-%s-%s_%s-%s_%s.png" % (
                self.projection, self.level, self.start[0], self.start[1], self.end[0], self.end[1]
            )
            path = os.path.join(curdir, path)
        else:
            path = self.output

        self.mapimg.save(path)
        os.remove(self.tempfile)

    def get_tile_lnglat(self, tile):
        img_point = [tile[1] * mapdownload.tilesize,
                     tile[0] * mapdownload.tilesize]
        if mapdownload.projection == PROJECTION_LL:
            lnglat = geoutil.image_to_lnglat_projection(img_point, mapdownload.level,
                                                        mapdownload.tilesize)
        else:
            wm_point = geoutil.image_to_webmecator(img_point, mapdownload.level,
                                                   mapdownload.tilesize)
            lnglat = geoutil.webmercator_to_lnglat(wm_point)
        return lnglat


def parseTileIndex(s):
    strs = s.split(",")
    index = [0, 0]
    if len(strs) > 0:
        index[0] = int(strs[0])
    if len(strs) > 1:
        index[1] = int(strs[1])
    return index


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Get a map by downloading tiles.")
    parser.add_argument('level', type=int,
                        help='''The tile level. ''')
    parser.add_argument('start',
                        help='''The start index of tile, given as "row,col". ''')
    parser.add_argument('end',
                        help='''The end index of tile, given as "row,col". ''')
    parser.add_argument('-t', '--tianditu', action='store_true', default=False,
                        help='''tiles source from Tianditu map.
                        The default source is Google map''')
    parser.add_argument('-s', '--tilesize', type=int, default=256,
                        help='''The tile size, in px.
                     The default value is 256.''')
    parser.add_argument('-o', '--output',
                        help='''The output map dir path.
                     The default path is the same with the input path.''')

    args = parser.parse_args()
    # MapDownload(4, (5, 11), (7, 14))

    projection = PROJECTION_WM
    if args.tianditu:
        projection = PROJECTION_LL

    mapdownload = MapDownload(level=args.level,
                              start=parseTileIndex(args.start),
                              end=parseTileIndex(args.end),
                              projection=projection,
                              tilesize=args.tilesize,
                              output=args.output)

    mapdownload.download()

    start_lnglat = mapdownload.get_tile_lnglat(mapdownload.start)
    print("The upper left lng/lat is %s" % (str(start_lnglat)))
