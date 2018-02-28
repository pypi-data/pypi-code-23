# coding=utf-8
import requests
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Polygon
from matplotlib.font_manager import FontProperties
import re
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def get_coordinate(location):
    url_format = "http://api.map.baidu.com/geocoder/v2/?output=json&ak=SjDhGSaC0GTQfhL7ezS9Qb0MoTWk49hO&address=%s"
    url = url_format % location
    response = requests.get(url)
    answer = response.json()
    try:
        x, y = answer['result']['location']['lng'], answer['result']['location']['lat']
        return x, y
    except:
        print 'query location %s fail, %s, %s' % (location, answer, answer['message'])
        return None, None


def draw_cn_map(location_file):
    plt.figure(figsize=(16, 8))
    m = Basemap(llcrnrlon=77, llcrnrlat=14, urcrnrlon=140, urcrnrlat=51, projection='lcc', lat_1=33, lat_2=45, lon_0=100)
    m.drawcoastlines()
    m.drawcountries(linewidth=1.5)

    base_dir = os.path.dirname(__file__).replace("\\", "/")

    m.readshapefile('%s/CHN_adm_shp/CHN_adm1' % base_dir, 'states', drawbounds=True)
    ax = plt.gca()
    for nshape, seg in enumerate(m.states):
        poly = Polygon(seg, facecolor='#96CDCD')
        ax.add_patch(poly)

    m.readshapefile('%s/TWN_adm_shp/TWN_adm0' % base_dir, 'taiwan', drawbounds=True)
    for nshape, seg in enumerate(m.taiwan):
        poly = Polygon(seg, facecolor='#96CDCD')
        ax.add_patch(poly)

    location_coord = {}
    location_cache = "location_cache.txt"

    fail_cache = "fail_cache.txt"
    fail_list = []
    if os.path.exists(fail_cache):
        for line in open(fail_cache):
            line = line.strip()
            fail_list.append(line)

    if os.path.exists(location_cache):
        for line in open(location_cache):
            line = line.strip()
            location = line.split("|")[0].strip()
            posx = line.split("|")[1].split(" ")[0]
            posy = line.split("|")[1].split(" ")[1]
            location_coord[location] = (float(posx), float(posy))

    location_cache_file = open(location_cache, "a+")

    fail_cache_file = open(fail_cache, "a+")

    for line in open(location_file):
        location = re.split(",\s;", line)[0]
        location = location.replace(";", "").strip()
        if location in location_coord:
            x, y = location_coord[location]
        else:
            if location in fail_list:
                continue
            x, y = get_coordinate(location)
            if x is None:
                fail_cache_file.write(location+"\n")
                continue
            x, y = m(x, y)
            print "query location: %s, x:%d, y:%d" % (location, x, y)
            location_cache_file.write("%s|%f %f\n" % (location, x, y))
            location_cache_file.flush()

        m.plot(x, y, marker='o', color='r', markersize=3, alpha=0.8, zorder=10)

    province = []
    for shapedict in m.states_info:
        statename = shapedict['NL_NAME_1']
        p = statename.split('|')
        if len(p) > 1:
            s = p[1]
        else:
            s = p[0]

        if s not in province:
            province.append(s)

    for shapedict in m.taiwan_info:
        s = shapedict['NAME_CHINE']
        if s not in province:
            province.append(s)

    province.append(u"黑龙江")
    font = FontProperties(fname="%s/fonts/simsun.ttc" % base_dir, size=14)
    for pro in province:
        print "pro", pro
        try:
            if pro == u"海南" or pro == u"河南":
                pro = pro + u"省"
            if pro in location_coord:
                x, y = location_coord[pro]
            else:
                if pro in fail_list:
                    continue

                x, y = get_coordinate(pro)
                x, y = m(x, y)
                location_cache_file.write("%s|%f %f\n" % (location, x, y))
                location_cache_file.flush()

            plt.text(x, y, pro, fontsize=8, color='#000000', zorder=100, fontproperties=font)
            print "add text %s" % pro
        except:
            pass

    fail_cache_file.close()
    location_cache_file.close()
    plt.show()


if __name__ == '__main__':
    draw_cn_map("author_location.txt")
