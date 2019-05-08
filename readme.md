# Tile cutter ***瓦片切割器***

```PowerShell
python tilecutter.py -h
```

Support for cutting images, cutting maps, display in tiled maps for Web Mercator projection and latitude and longitude projection.

***瓦片切割器，支持图片切割，地图切割，可用于Web墨卡托投影和经纬度投影的瓦片地图中显示。***

For example:

* Cut map ***地图切割***

```PowerShell
python tilecutter.py ./test_res/china.png -wm -t 512 -lv 4 -max 5 -ul "67.5000000,55.77657301866757"
```

[View results 查看生成的瓦片](https://github.com/1993hzw/tile-cutter/tree/master/test_res/china)

* Cut image ***图片切割***

```PowerShell
python tilecutter.py ./test_res/lol_crop.jpg -lv 6 -ul 4575,3840
```

[View results 查看生成的瓦片](https://github.com/1993hzw/tile-cutter/tree/master/test_res/lol_crop)

# Geo Util

```python
import geoutil  # geoutil.py
```

Commonly used projection coordinate system conversion, including wgs84 (GPS coordinates), gcj02 (Mars coordinates), bd09 (Baidu coordinates) coordinate conversion.

***常用的投影坐标系转换，包括wgs84（GPS坐标）,gcj02（火星坐标）,bd09（百度坐标）之间的坐标转换。***

# Download map ***地图下载***

```PowerShell
python downloadmap.py -h
```

Download tiles for a specific area under a specified level and combine them into a map.

***下载指定级别下特定区域的瓦片，并合成一张区域地图。***

For example:

```PowerShell
python downloadmap.py 4 5,11 7,14
```
表示下载级别4下，瓦片索引从(5,11)到(7,14)的区域地图。默认地图源为谷歌地图，加上参数`-t`表示切换到天地图。

After the download is completed, the starting point (ie, upper left corner) of the tile index will be output, which can be referenced when cutting the map.

***下载完成后会输出瓦片索引的起点（即左上角）经纬度坐标,可在切割地图时进行参考：***

```
The upper left lng/lat is [67.50000000000001, 55.7765730186677]

```

[View results 查看合成的地图](https://github.com/1993hzw/tile-cutter/blob/master/test_res/wm-4-5_11-7_14.png)

# [TiledMapView for Android](https://github.com/1993hzw/TiledMapView)

Tiled map loader for Android , supports a variety of projections, including Web Mercator projection, latitude and longitude projection and custom projection; supports locating, adding layers and overlays. 

***Android瓦片地图加载，支持多种投影，包括Web墨卡托投影，经纬度直投及自定义投影等；支持定位，添加图层和覆盖物。***


Tiles generated using the tile cutter cut above can be displayed directly in [TiledMapView](https://github.com/1993hzw/TiledMapView). For more information, please go to [TiledMapView](https://github.com/1993hzw/TiledMapView).

***上面使用瓦片切割器生成的瓦片可以直接在[TiledMapView](https://github.com/1993hzw/TiledMapView)中显示。想要了解更多请前往[TiledMapView](https://github.com/1993hzw/TiledMapView)。***

# The developer 开发者

154330138@qq.com  hzw19933@gmail.com

Q&A <a target="_blank" href="//shang.qq.com/wpa/qunwpa?idkey=9cef40e0b665e25745323941baa9f3cd89a75bba055b9922ce3779fb691ea5bc"><img border="0" src="//pub.idqqimg.com/wpa/images/group.png" alt="TiledMap交流群" title="TiledMap交流群"></a>  QQ Group ID: 885437848



