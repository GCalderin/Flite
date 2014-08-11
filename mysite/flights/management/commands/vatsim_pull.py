import csv
import requests
from flights.Models import Personal, ActiveFlights, Flights, ActiveControllers, Controllers
from decimal import Decimal
from django.db.models import F

def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        #decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')

def pilotInsert(row):
    

    call_sign = row[0]
    pilotId = row[1]
    flight_rating = int(row[16])
    real_name = row[2]
    date_time = updateTime
    flight_date = updateTime[0:11]
    client_type = "Pilot"
    alt = row[7]
    lon = Decimal(row[6])
    lat = Decimal(row[5])
    serv = row[14]
    ground_speed = row[8]
    transpond = row[17]
    flight_heading = row[37]
    aircraft = row[9]
    tascruise = row[10]
    depairport = row[11]
    altitude = row[12]
    destairport = row[13]
    flighttype = row[20]
    deptime = row[21][0:2] + ":" + row[21][2:4]
    actdeptime = row[22][0:2] + ":" + row[22][2:4]
    altairport = row[27]
    flight_remarks= row[28]
    flight_route = row[29]
    timelogon = row[36]
    route = row[]
    Route_String = lat + "," + lon + ";"

    user = Personal.objects.get(cid=pilotId)
    if Personal.objects.filter(cid=pilotId).exists() == false:
        newPersonal = Personal(cid = pilotId, realname = real_name, rating = flight_rating)
        newPersonal.save()

    
    if Flights.objects.filter(date = flight_date, callsign = call_sign, cid = cid).exists() == false:
        newFlight = Flights(date = flight_date, callsign = call_sign, cid = pilotId, planned_aircraft = aircraft, planned_tascruise = tascruise, planned_depairport = depairport, planned_altitude = altitude, planned_destairport = destairport, planned_flighttype = flighttype, planned_deptime = deptime, planned_actdepttime = actdeptime, plannedaltairport = altairport, planned_remarks = remarks, planned_route = route, time_logon = timelogon, RouteString = Route_String)
        newFlight.save()
    else:
        flight = Flights.objects.get(date = flight_date, callsign = call_sign, cid = cid)
        flight.RouteString = F('RouteString') + Route_String
        flight.save()

    if ActiveFlights.objects.filter(datetime = date_time, cid = pilotId, callsign = call_sign).exists() == false:
        newActive = ActiveFlights(datatime = date_time, cid = pilotId, callsign = call_sign, clienttype = client_type, latitude = lat, longitude = lon, server  = serv, altitude = alt, groundspeed = ground_speed, transponder = transpond, heading = flight_heading)
        newActive.save()


def atcInsert(row):
    datetime = updateTime
    callsign = row[0]
    cid = row[1]
    clienttype = "ATC"
    frequency = row[4]
    latitude = row[5]
    longitude = row[6]
    server = row[14]
    facilitytype = row[18]
    visualrange = row[19]
    time_logon = row[36]
    date =
    totaltime

    print name


client_rows = []        
r = requests.get('http://info.vroute.net/vatsim-data.txt')
data = r.text.splitlines()
update = ""
updateTime = ""
#with open('samplevatsim.txt', 'rb') as data:

reader = unicode_csv_reader(data,delimiter=":")

for row in reader:
    if (row != []):
        if "UPDATE = " in row[0]:
                date = row[0]
                update = date[9:]

        elif (row[0] == u'!CLIENTS'):
            for row in reader:
                if (row[0] == ";"):
                    break
                client_rows.append(row)

for row in client_rows:
    if (row[3] == 'PILOT'):
        pilotInsert(row)
    elif (row[3] == 'ATC'):
        atcInsert(row) 

updateTime = update[0:4] + "-" + update[4:6] + "-" + update[6:8] + "T" + update[8:10] + ":" + update[10:12] + ":" + update[11:13] + "-03:00"
print updateTime 
    
    
