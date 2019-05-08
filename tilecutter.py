# coding=utf-8
from __future__ import division
import sys
import argparse
import math
import os
from PIL import Image
import geoutil

curdir = os.path.dirname(__file__)
PROJECTION_WM = "wm"
PROJECTION_LL = "lnglat"


class TileCutter:
    tile_size = None
    path = None
    compress = False
    bgcolor = None

    _min_level = None
    _max_level = None
    _src_img_level = None
    _fullmap_width = None  # full map size in the src img level
    _fullmap_heght = None  # full map size in the src img level
    _upperleft = None  # The upper left location of image in full map
    _projection = None
    _output = None
    _showinfo = None

    def __init__(self, path, compress=False, bgcolor="#00000000", tile_size=256,
                 src_level=None,
                 min_level=0,
                 max_level=None,
                 upperleft=(0, 0),
                 projection=PROJECTION_WM,
                 output=None,
                 showinfo=False):

        if bgcolor is None:
            bgcolor = "#00000000"
        if upperleft is None or not isinstance(upperleft, tuple):
            upperleft = (0, 0)
        if tile_size is None:
            tile_size = 256

        self.tile_size = tile_size
        self.path = path
        self.compress = compress
        self.bgcolor = bgcolor
        self._src_img_level = src_level
        self._min_level = max(min_level, self._get_projection_min_level())
        self._max_level = max_level
        self._upperleft = upperleft
        self._projection = projection
        self._output = output
        self._showinfo = showinfo

        if self._src_img_level is not None and self._src_img_level < 0:
            raise RuntimeError("source image level must be equal or greater than 0")

        if self._max_level is not None and self._max_level < self._min_level:
            raise RuntimeError("max_level must be equal or greater than min_level")

    def showinfo(self, info):
        if self._showinfo:
            print(info)

    def mkdir(self, path):
        # if os.path.exists(path):
        #     shutil.rmtree(path)

        os.makedirs(path)

    def _get_max_row(self, level):
        if projection == PROJECTION_LL:
            return 2 ** (level - 1)
        else:
            return 2 ** level

    def _get_max_col(self, level):
        if projection == PROJECTION_LL:
            return 2 ** (level - 1) * 2
        else:
            return 2 ** level

    def _get_projection_min_level(self):
        if projection == PROJECTION_LL:
            return 1
        else:
            return 0

    def __find_max_level(self, image):
        img_width, img_height = image.size
        level = self._get_projection_min_level()
        maxwidth = self._get_max_col(level) * self.tile_size
        maxheight = self._get_max_row(level) * self.tile_size
        while maxwidth < img_width or maxheight < img_height:
            level += 1
            maxwidth = self._get_max_col(level) * self.tile_size
            maxheight = self._get_max_row(level) * self.tile_size
        return level

    def generate_tiles(self, level, image, upperleft, root_dir):
        tile_dir = os.path.join(root_dir, str(level))
        self.mkdir(tile_dir)
        img_width, img_height = image.size
        max_row = self._get_max_row(level)
        max_col = self._get_max_col(level)
        # (row, col)
        starttile = (int(upperleft[1] / self.tile_size), int(upperleft[0] / self.tile_size))
        offset = (int(upperleft[0] % self.tile_size), int(upperleft[1] % self.tile_size))
        self.showinfo("start tile = %s, offset = %s, max index = %s, scaled img size = %s"
                      % (str(starttile), str(offset), str((max_row, max_col)), str(image.size)))
        for row in range(starttile[0], max_row):
            relative_row = row - starttile[0]
            if (relative_row * self.tile_size - offset[1]) > img_height:
                return

            for col in range(starttile[1], max_col):
                relative_col = col - starttile[1]
                if (relative_col * self.tile_size - offset[0]) > img_width:
                    break

                # crop rect range
                start = (relative_col * self.tile_size - offset[0],
                         relative_row * self.tile_size - offset[1])
                end = (min(start[0] + self.tile_size, img_width),
                       min(start[1] + self.tile_size, img_height))
                start = (max(start[0], 0), max(start[1], 0))

                if start[0] >= end[0] or start[1] >= end[1]:  # no image
                    break

                self.showinfo("tile = %d %d %d, crop = %s" % (level, row, col, str(start + end)))

                region = image.crop(start + end)
                original_mode = image.mode
                tile = Image.new("RGBA", (self.tile_size, self.tile_size), color=self.bgcolor)
                drawstart = [0, 0]
                # consider offset
                if region.size != (self.tile_size, self.tile_size):
                    if start[0] == 0:
                        drawstart[0] = offset[0]
                    if start[1] == 0:
                        drawstart[1] = offset[1]
                tile.paste(region, tuple(drawstart))
                if region.size == (self.tile_size, self.tile_size):
                    if original_mode == "RGBA":
                        if self.compress:
                            tile = tile.convert("RGB")
                            tile.save(os.path.join(tile_dir, "%d_%d.png" % (col, row)), "JPEG")
                        else:
                            tile.save(os.path.join(tile_dir, "%d_%d.png" % (col, row)), "PNG")
                    else:
                        tile = tile.convert("RGB")
                        tile.save(os.path.join(tile_dir, "%d_%d.png" % (col, row)), "JPEG")
                else:  # Not a full tile of size equal to tile_size
                    tile.save(os.path.join(tile_dir, "%d_%d.png" % (col, row)), "PNG")

    def cut(self):
        if not os.path.isfile(self.path):
            raise RuntimeError("invalid image file")

        try:
            image = Image.open(self.path)
        except IOError:
            raise RuntimeError("Can't open the image file: " + self.path)

        if self._output is None:
            dir_path = os.path.splitext(self.path)[0]
            self._output = dir_path
        else:
            self._output = os.path.join(self._output,
                                        (os.path.splitext(os.path.split(self.path)[1]))[0])
        self.mkdir(os.path.abspath(self._output))

        if self._src_img_level is None:
            self._src_img_level = self.__find_max_level(image)
        if self._max_level is None:
            self._max_level = max(self._src_img_level, self._min_level)

        self._fullmap_width = self._get_max_col(self._src_img_level) * self.tile_size
        self._fullmap_heght = self._get_max_row(self._src_img_level) * self.tile_size
        img_width, img_height = image.size
        for lvl in range(self._min_level, self._max_level + 1):
            print(lvl)
            width_scale = (self._get_max_col(lvl) * self.tile_size * 1.0) / self._fullmap_width
            height_scale = (self._get_max_row(lvl) * self.tile_size * 1.0) / self._fullmap_heght
            scaled_w = math.ceil(img_width * width_scale)  # 向上取整
            scaled_h = img_height * height_scale
            if scaled_w < 1 or scaled_h < 1:
                self.showinfo("%s is too small, skip it! " % str((scaled_w, scaled_h)))
                continue

            size = (int(scaled_w), int(math.ceil(scaled_h)))
            scaled_img = image.resize(size, Image.ANTIALIAS)
            scaled_upperleft = (self._upperleft[0] * width_scale, self._upperleft[1] * height_scale)

            self.showinfo("scaled size = %s %s, upper left = %s"
                          % (str((width_scale, height_scale)), str(scaled_img.size),
                             str(scaled_upperleft)))

            self.generate_tiles(lvl, scaled_img, scaled_upperleft, self._output)

        print("Finished!")
        print("Level=[%s, %s]" % (self._min_level, self._max_level))
        print(
                "Source image: size = %s, level = %s, upper left location = %s, mode = %s" % (
            str(image.size), self._src_img_level, str(self._upperleft), image.mode))
        print("Output: " + self._output)
        if self._src_img_level < self._max_level:
            print(
                    "Warnings: The max level %s is greater than source image level %s, which will lead to blurred tiles above level %s" \
                    % (self._max_level, self._src_img_level, self._src_img_level))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Cut a image into tiles.")
    parser.add_argument('filename')
    parser.add_argument('-c', '--compress', action='store_true',
                        help='Compress the image size by ignoring transparency.')
    parser.add_argument('-i', '--info', action='store_true', default=False,
                        help='''Show more info.''')
    parser.add_argument('-b', '--bgcolor',
                        help='''Tile background color, given as #rgba or #rrggbbaa.
                    The default color is transparent (#00000000).''')
    parser.add_argument('-lv', '--srclevel', type=int,
                        help='''The source image level. 
                    The default value is computed by the image size.''')
    parser.add_argument('-min', '--minlevel', type=int, default=0,
                        help='''The min level for cutting tiles. 
                    The default value is 0.''')
    parser.add_argument('-max', '--maxlevel', type=int,
                        help='''The max level for cutting tiles.
                     The default value is the source image level.''')
    parser.add_argument('-ul', '--upperleft', default="0,0",
                        help='''The upper left location of image in full map, given as "x,y",\
                         in px by default.
                     The default value is 0,0.''')
    parser.add_argument('-t', '--tilesize', type=int, default=256,
                        help='''The tile size, in px.
                     The default value is 256.''')
    parser.add_argument('-o', '--output',
                        help='''The output tiles dir path.
                     The default path is the same with the input path.''')

    # 使用Web墨卡托投影切图，参数-ul表示经纬度，基于WGS84坐标系，中国境内会进行WGS84到GCJ02的转换
    parser.add_argument('-wm', '--webmercator', action='store_true', default=False,
                        help='''Web mercator projection.
                        If true, the argument -ul is (longitude, latitude), the coordinates of WGS84''')
    # 使用经纬度投影切图，参数-ul表示经纬度
    parser.add_argument('-ll', '--lnglat', action='store_true', default=False,
                        help='''Latitude / Longitude Projection.
                        If true, the argument -ul is (longitude, latitude)''')
    # 使用国测局坐标（火星坐标），中国境内无需进行WGS84到GCJ02的转换
    parser.add_argument('-gcj', '--gcj02', action='store_true', default=False,
                        help='''Whether to use the coordinates of GCJ02.
                        If true, the argument -ul is the coordinates of GCJ02''')

    args = parser.parse_args()
    upperleft = [0, 0]
    projection = PROJECTION_WM
    if args.upperleft is not None:
        strs = args.upperleft.split(",")
        if args.webmercator or args.lnglat:
            if args.srclevel is None:
                raise RuntimeError(
                    "Please tell me the source image level by setting the param -lv.")

            if len(strs) > 0:
                upperleft[0] = float(strs[0])
            if len(strs) > 1:
                upperleft[1] = float(strs[1])

            print("origin lnglat:" + str(upperleft))
            if args.webmercator:
                if not args.gcj02:
                    upperleft = geoutil.wgs84_to_gcj02(upperleft[0], upperleft[1])

                print("transformed:" + str(upperleft))
                upperleft = geoutil.lnglat_to_webmercator(upperleft)
                print("wm:" + str(upperleft))
                upperleft = geoutil.webmercator_to_image(upperleft, args.srclevel, args.tilesize)
            else:  # lnglat
                projection = PROJECTION_LL
                upperleft = geoutil.lnglat_projecion_to_image(upperleft, args.srclevel,
                                                              args.tilesize)
            upperleft = [int(round(upperleft[0])), int(round(upperleft[1]))]  # 四舍五入准确点。。。
        else:
            if len(strs) > 0:
                upperleft[0] = float(strs[0])
            if len(strs) > 1:
                upperleft[1] = float(strs[1])

    cutter = TileCutter(path=os.path.abspath(args.filename), compress=args.compress,
                        bgcolor=args.bgcolor,
                        src_level=args.srclevel, min_level=args.minlevel,
                        max_level=args.maxlevel,
                        upperleft=tuple(upperleft),
                        tile_size=args.tilesize,
                        projection=projection,
                        output=args.output,
                        showinfo=args.info)
    print("\n++++++++++++++++ begin ++++++++++++++++++++")
    cutter.cut()
    print("+++++++++++++++++ end +++++++++++++++++++++\n")
