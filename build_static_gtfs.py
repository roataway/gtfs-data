import datetime
import json
import os
import pandas as pd
import shutil

STOPS_TXT = "stops.txt"
ROUTES_TXT = "routes.txt"
SHAPES_TXT = "shapes.txt"
STOP_TIMES_TXT = "stop_times.txt"
TRIPS_TXT = "trips.txt"

GTFS_PATH = "./GTFS_static/"
STATIONS_INFORMATION = "./stations_routes/"

files = [f for f in os.listdir(STATIONS_INFORMATION) if os.path.isfile(os.path.join(STATIONS_INFORMATION, f))]
routes_relations = pd.read_csv(STATIONS_INFORMATION+"routes.csv")
concise_names = routes_relations[["id_upstream", "name_concise"]].set_index("id_upstream").to_dict()["name_concise"]

def build_stops_txt() -> None:
    finish_stop = []
    d = {}
    written = []
    file = open(GTFS_PATH+STOPS_TXT, "w")
    file.write("stop_id,stop_name,stop_lat,stop_lon,location_type,parent_station\n")
    for f in files:
        print(f)
        with open(STATIONS_INFORMATION + f) as json_file:
            if "ordered" in f and "stations" in f:
                data = json.load(json_file)
                print(data)
                df = pd.json_normalize(data['features'])
                try:
                    finish_stop.append(df[df["properties.order_forward"] == 0]["properties.id"].values[0])
                    finish_stop.append(df[df["properties.order_backward"] == 0]["properties.id"].values[0])
                except Exception as e:
                    parent_id = 0
                    print("cannot retrieve parent id for " + f)
                    print(e)
                for index, row in df.iterrows():
                    if str(row["properties.id"]) not in d.keys():
                        d[str(row["properties.id"])] = row.to_dict()
                print(df)
    for k, v in d.items():
        print(v)
        if k not in written:
            written.append(k)
            if v["properties.tags.name"] and v['properties.id'] != 1558999570 and v['properties.id'] != parent_id:
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

def build_stop_time_txt() -> None:
    stop_times = open(GTFS_PATH+STOP_TIMES_TXT, "w")
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
                    df1 = df1.sort_values(by=["properties.order_forward"])
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

def build_trips_and_routes_txt()->None:
    routes = open(GTFS_PATH+ROUTES_TXT, "w")
    trips = open(GTFS_PATH+TRIPS_TXT, "w")

    trips.write("route_id,service_id,trip_id,trip_short_name,shape_id,direction_id\n")
    routes.write("route_id,agency_id,route_short_name,route_long_name,route_type\n")
    for index, row in routes_relations.iterrows():
        routes.write(str(row["name_concise"]) + ",RTEC," + str(row["name_concise"]) + "," + str(row["name_long"]) + ",3\n")
        trips.write(str(row["name_concise"]) + "," + "FULLW," + str(row["name_concise"]) + "," + str(row["name_long"]) + "," + str(row["name_concise"]) + ",0\n")

    routes.close()
    trips.close()


build_stops_txt()
build_stop_time_txt()
build_trips_and_routes_txt()

print("removing existing zip file")

GTFS_ZIP = GTFS_PATH+"Archive.zip"
try:
    os.remove(GTFS_ZIP)
except:
    print("I tried to remove "+GTFS_ZIP)

print("Creating gtfs static zip")
shutil.make_archive("GTFS_static", 'zip', GTFS_PATH)

print("Gtfs static location = " + GTFS_PATH+"GTFS_static.zip")




