# 瓦片切割器 

```PowerShell
python tilecutter.py -h
```

支持图片切割，地图切割，可用于Web墨卡托投影和经纬度投影的瓦片地图中显示。

举例:

* 地图切割

```PowerShell
python tilecutter.py ./test_res/china.png -wm -t 512 -lv 4 -max 5 -ul "67.5000000,55.77657301866757"
```

[查看生成的瓦片](https://github.com/1993hzw/tile-cutter/tree/master/test_res/china)

* 图片切割

```PowerShell
python tilecutter.py ./test_res/lol_crop.jpg -lv 6 -ul 4575,3840
```

[查看生成的瓦片](https://github.com/1993hzw/tile-cutter/tree/master/test_res/lol_crop)

# GEO工具类

```python
import geoutil  # geoutil.py
```

常用的投影坐标系转换，包括wgs84（GPS坐标）,gcj02（火星坐标）,bd09（百度坐标）之间的坐标转换。

# 地图下载

```PowerShell
python downloadmap.py -h
```

举例:

首先下载指定级别下特定区域的瓦片，并合成一张区域地图

```PowerShell
python downloadmap.py 4 5,11 7,14
```
表示下载级别4下，瓦片索引从(5,11)到(7,14)的区域地图。默认地图源为谷歌地图，加上参数`-t`表示切换到天地图。

下载完成后会输出瓦片索引的起点（即左上角）经纬度坐标：
```
The upper left lng/lat is [67.50000000000001, 55.7765730186677]

```

[查看合成的地图](https://github.com/1993hzw/tile-cutter/blob/master/test_res/wm-4-5_11-7_14.png)

# [TiledMapView for Android](https://github.com/1993hzw/TiledMapView)

Android瓦片地图加载，支持多种投影，包括Web墨卡托投影，经纬度直投及自定义投影等；支持定位，添加图层和覆盖物。

上面使用瓦片切割器切割的瓦片可以直接在[TiledMapView](https://github.com/1993hzw/TiledMapView)中显示。想要了解更多请前往[TiledMapView](https://github.com/1993hzw/TiledMapView)。


