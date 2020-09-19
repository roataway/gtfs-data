import operator
import os
import json
from collections import OrderedDict
from math import radians, cos, sin, atan2, sqrt

import pandas as pd
import datetime

destdir = '/Users/vasilecatana/PycharmProjects/untitled10/stations_routes/'
files = [f for f in os.listdir(destdir) if os.path.isfile(os.path.join(destdir, f))]

print(files)
d = {}
file = open("GTFS_Chisinau/stops.txt", "w")
file.write("stop_id,stop_name,stop_lat,stop_lon,location_type,parent_station\n")
written = []
finish_stop = []


def geoJson2shape(route_id, shapefile, shapefileRev=None):
    with open(shapefile, encoding='utf8') as f:
        # loading geojson, from https://gis.stackexchange.com/a/73771/44746
        data = json.load(f)
    print('Loaded', shapefile)

    output_array = []
    try:
        coordinates = data['features'][0]['geometry']['coordinates']
    except:
        print('Invalid geojson file ' + shapefile)
        return False

    prevlat = coordinates[0][1]
    prevlon = coordinates[0][0]
    dist_traveled = 0
    i = 0
    for item in coordinates:
        newrow = OrderedDict()
        newrow['shape_id'] = route_id
        newrow['shape_pt_lat'] = item[1]
        newrow['shape_pt_lon'] = item[0]
        calcdist = lat_long_dist(prevlat, prevlon, item[1], item[0])
        dist_traveled = dist_traveled + calcdist
        newrow['shape_dist_traveled'] = dist_traveled
        i = i + 1
        newrow['shape_pt_sequence'] = i
        output_array.append(newrow)
        prevlat = item[1]
        prevlon = item[0]

    # Reverse trip now.. either same shapefile in reverse or a different shapefile
    if (shapefileRev):
        with open(shapefileRev, encoding='utf8') as g:
            data2 = json.load(g)
        print('Loaded', shapefileRev)
        try:
            coordinates = data2['features'][0]['geometry']['coordinates']
        except:
            print('Invalid geojson file ' + shapefileRev)
            return False
    else:
        coordinates.reverse()

    prevlat = coordinates[0][1]
    prevlon = coordinates[0][0]
    dist_traveled = 0
    i = 0
    for item in coordinates:
        newrow = OrderedDict()
        newrow['shape_id'] = route_id
        newrow['shape_pt_lat'] = item[1]
        newrow['shape_pt_lon'] = item[0]
        calcdist = lat_long_dist(prevlat, prevlon, item[1], item[0])
        dist_traveled = float(format(dist_traveled + calcdist, '.2f'))
        newrow['shape_dist_traveled'] = dist_traveled
        i = i + 1
        newrow['shape_pt_sequence'] = i
        output_array.append(newrow)
        prevlat = item[1]
        prevlon = item[0]

    return output_array


def lat_long_dist(lat1, lon1, lat2, lon2):
    # function for calculating ground distance between two lat-long locations
    R = 6373.0  # approximate radius of earth in km.

    lat1 = radians(float(lat1))
    lon1 = radians(float(lon1))
    lat2 = radians(float(lat2))
    lon2 = radians(float(lon2))

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = float(format(R * c, '.2f'))  # rounding. From https://stackoverflow.com/a/28142318/4355695
    return distance

for f in files:
    print(f)
    with open("./stations_routes/" + f) as json_file:
        if "ordered" in f and "stations" in f:
            data = json.load(json_file)
            print(data)
            df = pd.json_normalize(data['features'])
            try:
                parent_id = df[df["properties.order_backward"] == 0]["properties.id"].values[0]
                finish_stop.append(parent_id)
            except:
                parent_id = 0
                print("error")
            for index, row in df.iterrows():
                if str(row["properties.id"]) not in d.keys():
                    d[str(row["properties.id"])] = row.to_dict()
            print(df)
for k, v in d.items():
    print(v)
    if k not in written:
        written.append(k)
        if v["properties.tags.name"] and v['properties.id'] != 1558999570 is not None and v[
            'properties.id'] != parent_id:
            if v['properties.id'] in finish_stop:
                file.write(str(v["properties.id"]) + ',' + str(v["properties.tags.name"]) + ',' + str(
                    v["geometry.coordinates"][1]) + "," + str(v["geometry.coordinates"][0]) + ',1,')
                file.write("\n")
            else:
                file.write(str(v["properties.id"]) + ',' + str(v["properties.tags.name"]) + ',' + str(
                    v["geometry.coordinates"][1]) + "," + str(v["geometry.coordinates"][0]) + ',3,' + str(
                    parent_id))
                file.write("\n")

        else:
            if v['properties.id'] == parent_id:
                file.write(str(v["properties.id"]) + ',' + str(v["properties.tags.name"]) + ',' + str(
                    v["geometry.coordinates"][1]) + "," + str(v["geometry.coordinates"][0]) + ',1,')
                file.write("\n")
    else:
        continue

print(d)

file.close()
d = {}
rute = pd.read_csv("stations_routes/routes.csv")
concise_names = rute[["id_upstream", "name_concise"]].set_index("id_upstream").to_dict()["name_concise"]
#
# d = {}
file = open("GTFS_Chisinau/routes.txt", "w")
trips = open("GTFS_Chisinau/trips.txt", "w")
trips.write("route_id,service_id,trip_id,trip_short_name,shape_id,direction_id\n")

file.write("route_id,agency_id,route_short_name,route_long_name,route_type\n")
for index, row in rute.iterrows():
    file.write(str(row["name_concise"]) + ",RTEC," + str(row["name_concise"]) + "," + str(row["name_long"]) + ",3\n")
    trips.write(
        str(row["name_concise"]) + "," + "FULLW," + str(row["name_concise"]) + "," + str(row["name_long"]) + "," + str(
            row["name_concise"]) + ",0\n")

file.close()
trips.close()

print(d)
d1 = {}
file = open("GTFS_Chisinau/shapes.txt", "w")
file.write("shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence\n")

lss = []
for f in files:
    print(f)
    with open("./stations_routes/" + f) as json_file:
        if "segments" in f:
            data = json.load(json_file)
            print(data)

            sorted(data["features"], key=lambda k: k["properties"]['id'])
            idd = f.split("_")[1]
            idd = str(concise_names[int(idd)])
            output = geoJson2shape(idd, "./stations_routes/" + f, "./stations_routes/" + f)
            df = pd.json_normalize(data['features'])
            print(df)

            geo_json_file = open("geojsons/" + f + ".geojson", "w")
            geo_d = {}
            lss.append(output)

            geo_d["type"] = "FeatureCollection"
            geo_d["crs"] = {"type": "name", "properties": {"name": idd}}
            geoms = {}
            geoms["type"] = "Feature"
            geoms["properties"] = {"id": 1}
            geometry = {}
            geometry["type"] = "LineString"
            vals = []
            for index, row in df.iterrows():
                for x in row["geometry.coordinates"]:
                    vals.append(x)
            geometry["coordinates"] = vals
            geoms["geometry"] = geometry

            geo_d["features"] = [geoms]

            json.dump(geo_d, geo_json_file, indent=4)
            geo_json_file.close()

            k1 = 1
            # for index, row in df.iterrows():
            #     for x in row["geometry.coordinates"]:
            #         print(type(x[0]))
            #         if isinstance(x[0], list) == False:
            #             file.write(idd + "," + str(x[1]) + "," + str(x[0]) + "," + str(k1) + "\n")
            #             k1 = k1 + 1
            #         else:
            #             for x1 in x:
            #                 file.write(idd + "," + str(x1[1]) + "," + str(x1[0]) + "," + str(k1) + "\n")
            #                 k1 = k1 + 1
for data in lss:
    pd.DataFrame(data).to_csv("./GTFS_Chisinau/shapes.txt", mode='a', header=False, index=False)

file.close()
stop_times = open("GTFS_Chisinau/stop_times.txt", "w")
stop_times.write("trip_id,arrival_time,departure_time,stop_id,stop_sequence\n")

for f in files:
    print(f)
    with open("./stations_routes/" + f) as json_file:
        if "ordered" in f and "stations" in f:
            idd = f.split("_")[1]
            idd = str(concise_names[int(idd)])
            data = json.load(json_file)

            print(data)
            df = pd.json_normalize(data['features'])
            df1 = df.copy(deep=True)
            df2 = df.copy(deep=True)
            t = "10:00"
            d = datetime.datetime.strptime(t, '%H:%M')
            counter = 0
            order = 1
            try:
                str_order_forward = "properties.order_forward"
                str_order_backward = "properties.order_backward"

                df1 = df.sort_values(by=["properties.order_forward"])
                df1 = df1[df1["properties.order_forward"].notnull()]

                print("processed")
                for index, row in df1.iterrows():
                    if row["properties.id"] != 1558999570:
                        d1 = (d + datetime.timedelta(minutes=counter)).strftime("%H:%M")
                        d2 = (d + datetime.timedelta(minutes=counter + 15)).strftime("%H:%M")
                        stop_times.write(
                            str(idd) + "," + d1 + ":00," + d2 + ":00," + str(row["properties.id"]) + "," + str(
                                order) + "\n")
                        order = order + 1
                        counter = counter + 15
            except:
                print("error no order_forward")

            try:
                str_order_forward = "properties.order_forward"
                str_order_backward = "properties.order_backward"

                df2 = df2.sort_values(by=["properties.order_backward"])
                df2 = df2[df2["properties.order_backward"].notnull()]

                print("processed")
                for index, row in df2.iterrows():
                    if row["properties.id"] != 1558999570:
                        d1 = (d + datetime.timedelta(minutes=counter)).strftime("%H:%M")
                        d2 = (d + datetime.timedelta(minutes=counter + 15)).strftime("%H:%M")
                        stop_times.write(
                            str(idd) + "," + d1 + ":00," + d2 + ":00," + str(row["properties.id"]) + "," + str(
                                order) + "\n")
                        order = order + 1
                        counter = counter + 15
            except:
                print("error no back_forward")
stop_times.close()


# reading shapes


