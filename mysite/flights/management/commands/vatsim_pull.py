import csv
import requests
import datetime
import math
import sys
from django.conf import settings
from django.core.management.base import NoArgsCommand, CommandError
from datetime import timedelta
from django.utils.timezone import utc
from flights.models import (Personal, ActiveFlights, Flights, ActiveControllers, Controllers, Airports)
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

def getNmFromLatLon(lat1, lon1, lat2, lon2):
        R = 3443.89849 # km
        theta1 = math.radians(lat1)
        theta2 = math.radians(lat2)
        dtheta = math.radians(lat2-lat1)
        dlon = math.radians(lon2-lon1)

        a = math.sin(dtheta/2) * math.sin(dtheta/2) + math.cos(theta1) * math.cos(theta2) * math.sin(dlon/2) * math.sin(dlon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        d = R * c

        return round(d)


class Command(NoArgsCommand):
    help = "Scrapes flight info from Vatsim"


    

    def pilotInsert(self, row, update_time):
        
        updateTime = update_time
        call_sign = row[0]
        pilotId = row[1]

        if (row[16] != ''):
            user_rating = int(row[16])
        else:
            user_rating = ''
        if (user_rating == 0):
            user_rating = 'Not Rated'
        elif (user_rating == 1):
            user_rating = 'VATSIM Online Pilot'
        elif (user_rating == 2):
            user_rating = 'VATSIM Airmanship Basics'
        elif (user_rating == 3):
            user_rating = 'VATSIM VFR Pilot'
        elif (user_rating == 4):
            user_rating = 'VATSIM IFR Pilot'
        elif (user_rating == 5):
            user_rating = 'VATSIM Advanced IFR Pilot'
        elif (user_rating == 6):
            user_rating = 'VATSIM International and Oceanic Pilot'
        elif (user_rating == 7):
            user_rating = 'Helicopter VFR and IFR Pilot'
        elif (user_rating == 8):
            user_rating = 'Military Special Operations Pilot'
        elif (user_rating == 9):
            user_rating = 'VATSIM Pilot Flight Instructor'

        #Turn these variables into blank strings if theyre missing from vatsim
        if (row[6] != ''):
            lon = Decimal(row[6])
        else:
            lon = ''

        if (row[5] != ''):
            lat = Decimal(row[5])
        else:
            lat = ''

        if (row[8] != ''):
            ground_speed = int(row[8])
        else:
            ground_speed = ''

        if (row[17] != ''):
            transpond = int(row[17])
        else:
            transpond = ''
        
        if (row[38] != ''):
            flight_heading = int(row[38])
        else:
            flight_heading = ''

        
        if (row[10] != ''):
            tascruise = int(row[10])
        else:
            tascruise = ''

        

        if (row[7] != ''):    
            altitude = int(row[7])
        else:
            altitude = ''

        real_name = row[2]
        date_time = updateTime
        just_date = date_time[0:10]
        flight_date = datetime.datetime.strptime(just_date, "%Y-%m-%d")
        client_type = "Pilot"
        serv = row[14]
        aircraft = row[9]
        depairport = row[11]
        destairport = row[13]

        deptime = row[22][0:2] + ":" + row[22][2:4]
        #Some of the deptimes come in in a format that gets screwy, so lets check for that
        try:
            fdeptime = datetime.datetime.strptime(deptime, "%H:%M")
            flight_duration = datetime.datetime.utcnow() - datetime.combine(date.today(), fdeptime)
            flight_duration = str(flight_duration) 
        except Exception, e:
            deptime = None
            flight_duration = "00:00"
        
            
        actdeptime = row[23][0:2] + ":" + row[23][2:4]
        #same issue here
        try:
            factdeptime = datetime.datetime.strptime(actdeptime, "%H:%M")
        except Exception, e:
            actdeptime = None


        altairport = row[28]
        flight_remarks= row[29]
        flight_route = row[30]
        Route_String = ";" + str(lat) + "," + str(lon) + ";"      
        flightStatus = ""
        logon = row[37]
        timelogon = logon[0:4] + "-" + logon[4:6] + "-" + logon[6:8] + " " + logon[8:10] + ":" + logon[10:12] + ":" + logon[12:14] + "+0000"




        #Deal with Personal Table
        #########################
        #########################
        if (Personal.objects.filter(cid=pilotId).exists() == False):
            newPersonal = Personal(cid = pilotId, realname = real_name, pilot_rating = user_rating)
            newPersonal.save()
        else:
            personal = Personal.objects.get(cid=pilotId)
            if (personal.pilot_rating != user_rating):
                personal.pilot_rating = user_rating
            
        #Deal with Flights Table
        #########################
        #########################
        if (Flights.objects.filter(date = flight_date, callsign = call_sign, cid = pilotId).exists() == False):
            try:
                origAirport = Airports.objects.get(icao=depairport)
                origLat = origAirport.lat
                origLon = origAirport.lon
                dist = getNmFromLatLon(lat, lon, origLat, origLon)
            except Exception, e:
                dist = 0
            
            newFlight = Flights(date = just_date, callsign = call_sign, cid = pilotId, planned_aircraft = aircraft, planned_tascruise = tascruise, planned_depairport = depairport, planned_altitude = altitude, planned_destairport = destairport, planned_deptime = deptime, planned_actdeptime = actdeptime, planned_altairport = altairport, planned_remarks = flight_remarks, planned_route = flight_route, Routestring = Route_String, duration=flight_duration, total_distance = dist, time_logon=timelogon, onGround = None, offGround = None, outRamp = None)
            newFlight.save()
        else:
            flight = Flights.objects.get(date = flight_date, callsign = call_sign, cid = pilotId)

            #Get last lat/lon
            colonCount = 0
            colon1 = 0
            colon2 = 0
            comma = 0
            rString = flight.Routestring
            try:
                for i in range(len(rString), 0, -1):
                    if ((flight.rString[i] == ";") and (colonCount == 0)):
                        colon1 = i
                        colonCount +=1
                    elif ((flight.rString[i] == ",") and (colonCount == 1)):
                        comma = i
                    elif ((flight.rString[i] == ";") and (colonCount == 1)):
                        colon2 = i
                prevLat = decimal(flight.rString[colon2+1:comma])
                prevLon = decimal(flight.rString[comma+1:colon1])

                #Update Total Distance
                flight.Routestring = F('total_distance') + getNmFromLatLon(lat, lon, prevLat, prevLon)

            except Exception, e:
                flight.Routestring = F('total_distance') + 0
            



            #Update Route String
            flight.Routestring = F('Routestring') + str(Route_String)
            if ((flight.outRamp == None) and (ground_speed < 50)):
                flight.outRamp = updateTime
                flightStatus = "On The Ground"
            if ((flight.offGround == None) and (ground_speed > 50)):
                flight.offGround = updateTime
                flightStatus = "Airborne"




            #Get Destination Airport Coords
            destAirport = Airports.objects.get(icao=destairport)
            destLat = destAirport.lat
            destlon = destAirport.lon

            if ((flight.onGround == None) and (ground_speed< 50) and (getNmFromLatLon(lat, lon, destLat, destlon) < 5)):
                flight.onGround = updateTime
                flightStatus = "Arrived"
                flight.duration = datetime.datetime.utcnow()

             #Update Total Duration
            if ((flight.offGround != None) and (flight.onGround == None)):
                dtfoffGround = datetime.datetime.strptime(flight.offGround[:len(flight.offGround)-5], "%Y-%m-%d %H:%M:%S")
                flight.duration = datetime.datetime.utcnow() - dtfoffGround
                flight_duration = str(flight_duration)

            flight.save()

        #Deal with ActiveFlights Table
        #########################
        #########################
        try:
            aflight = ActiveFlights.objects.filter(datetime = date_time, cid = pilotId, callsign = call_sign)
        except Exception, e:
            if (flightStatus == ""):
                try:
                    lastActive = ActiveFlights.objects.filter(cid = pilotId, callsign = call_sign).latest('datetime')
                    flightStatus = lastActive.flight_status
                except Exception, e:
                    flightStatus = " "
            newActive = ActiveFlights(datetime = date_time, cid = pilotId, callsign = call_sign, clienttype = client_type, latitude = lat, longitude = lon, server  = serv, altitude = alt, groundspeed = ground_speed, transponder = transpond, heading = flight_heading, flight_status=flightStatus)
            newActive.save()

        # if (ActiveFlights.objects.filter(datetime = date_time, cid = pilotId, callsign = call_sign).exists() == False):
        #     if (flightStatus == ""):
        #         if (ActiveFlights.objects.filter(cid = pilotId, callsign = call_sign).latest('datetime').exists() == True):
        #             lastActive = ActiveFlights.objects.filter(cid = pilotId, callsign = call_sign).latest('datetime')
        #             flightStatus = lastActive.flight_status
        #         else:
        #             flightStatus = " "

        #     newActive = ActiveFlights(datetime = date_time, cid = pilotId, callsign = call_sign, clienttype = client_type, latitude = lat, longitude = lon, server  = serv, altitude = alt, groundspeed = ground_speed, transponder = transpond, heading = flight_heading, flight_status=flightStatus)
        #     newActive.save()

            #Delete old active flight entry
            try:
                ActiveFlights.objects.filter(cid = pilotId, callsign = call_sign).exclude(datetime = updateTime)
                oldActive = ActiveFlights.objects.filter(cid = pilotId, callsign = call_sign).exclude(datetime = updateTime)
                oldActive.delete()
            except Exception, e:
                pass

            # if (ActiveFlights.objects.filter(cid = pilotId, callsign = call_sign).exclude(datetime = updateTime).exists() == True):
            #     oldActive = ActiveFlights.objects.filter(cid = pilotId, callsign = call_sign).exclude(datetime = updateTime)
            #     oldActive.delete()


    def atcInsert(self, row, update_time):
        updateTime = update_time
        date_time = updateTime
        _date = updateTime[0:10]
        call_sign = row[0]
        atc_id = row[1]

        if (row[16] != ''):
            user_rating = int(row[16])
        else:
            user_rating = ''

        if (user_rating == 0):
            user_rating = 'Ground Controller'
        elif (user_rating == 1):
            user_rating = 'Tower Controller'
        elif (user_rating == 2):
            user_rating = 'TMA Controller'
        elif (user_rating == 3):
            user_rating = 'Enroute Controller'
        elif (user_rating == 4):
            user_rating = 'Senior Controller'

        client_type = "ATC"
        freq = row[4]
        lat = row[5]
        lon = row[6]
        serv = row[15]
        facility_type = row[18]
        if (facility_type == 0):
            facility_type = 'Other'
        elif (facility_type == 1):
            facility_type = 'Observer'
        elif (facility_type == 2):
            facility_type = 'Clearance Delivery'
        elif (facility_type == 3):
            facility_type = 'Ground'
        elif (facility_type == 4):
            facility_type = 'Tower'
        elif (facility_type == 5):
            facility_type = 'Approach/Departure'
        elif (facility_type == 6):
            facility_type = 'Center'

        if (row[19] != ''):
            visual_range = int(row[19])
        else:
            visual_range = ''
        logon = row[37]
        timelogon = logon[0:4] + "-" + logon[4:6] + "-" + logon[6:8] + " " + logon[8:10] + ":" + logon[10:12] + ":" + logon[12:14] + "+0000"
        date = updateTime
        totaltime = datetime.datetime.utcnow() - datetime.datetime.strptime(timelogon, "%Y-%m-%d %H:%M:%S")
        totaltime = sr(totaltime)

        if (Personal.objects.filter(cid=atc_id).exists() == False):
            newPersonal = Personal(cid = atc_id, realname = real_name, atc_rating = user_rating)
            newPersonal.save()
        else:
            personal = Personal.objects.get(cid=atc_id)
            if (personal.atc_rating != user_rating):
                personal.atc_rating = user_rating

        if (ActiveControllers.objects.filter(cid=atc_id, callsign=call_sign, datetime=date_time).exists == False):
            newActiveATC = ActiveControllers(datetime=date_time, callsign=call_sign, cid=atc_id, clienttype=client_type, frequency=freq, latitude=lat, longitude=lon, server=serv, facilitytype=facility_type, visualrange=visual_range, time_logon=timelogon)
            #delete old active controller
            oldActiveATC = ActiveControllers.objects.filter(cid=atc_id, callsign = call_sign).exclude(datetime = updateTime)
            oldActiveATC.delete()

        if (Controllers.objects.filter(date=_date, callsign= call_sign, cid = atc_id).exists() == False):
            totaltime = datetime.datetime.utcnow() - time_logon
            newController(date=_date, callsign = call_sign, cid = atc_id, facilitytype = facility_type, TotalTime = totaltime)
        else:
            controller = Controllers.objects.get(date=date, callsign= call_sign, cid=atc_id)
            controller.TotalTime = controller.TotalTime + (updateTime - controller.lastUpdate)
            controller.lastUpdate = updateTime
            controller.save()




    def readVatsim(self):
        client_rows = []        
        r = requests.get('http://info.vroute.net/vatsim-data.txt')
        data = r.text.splitlines()
        update = ""
        newUpdate = True
        updateTime = ""

        reader = unicode_csv_reader(data,delimiter=":")

        for row in reader:
            if (row != []):
                if "UPDATE = " in row[0]:
                        date = row[0]
                        update = date[9:]
                        updateTime = update[0:4] + "-" + update[4:6] + "-" + update[6:8] + " " + update[8:10] + ":" + update[10:12] + ":" + update[12:14] + "+0000"
                        if (ActiveFlights.objects.filter(datetime=updateTime).exists() == True):
                            newUpdate = False

                elif (row[0] == u'!CLIENTS'):
                    for row in reader:
                        if (row[0] == ";"):
                            break
                        client_rows.append(row)
        if (newUpdate == True):
            for row in client_rows:
                if (row[3] == 'PILOT'):
                    self.pilotInsert(row, updateTime)
                elif (row[3] == 'ATC'):
                    self.atcInsert(row, updateTime) 

        ## Delete flights that have been missing for an hour

        notUpdated = ActiveFlights.objects.exclude(datetime = updateTime)
        for flight in notUpdated:
            if ((flight.datetime + timedelta(hours=1)) <= datetime.datetime.utcnow()):
                flight.delete()
        ## Delete missing controllers
        missingController = ActiveFlights.objects.exclude(datetime = updateTime)
        for controller in missingController:
            controller.delete()

    # CSV READING BEGINS
    #
    #
    #

    def handle(self, **options):

        self.readVatsim()

    
    
