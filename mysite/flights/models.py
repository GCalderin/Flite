from django.db import models

class Personal(models.Model):
	cid = models.ForeignKey('Users.cid')
	realname = models.CharField(maxlength=30)
	rating = models.IntegerField

class ActiveFlights(models.Model):
	datetime = models.DateTimeField
	callsign = models.CharField(max_length=10)
	cid = models.ForeignKey('Users.cid')
	clienttype = models.CharField(max_length=10)
	latitude = models.DecimalField(max_digits=7, decimal_places=5)
	longitude = models.DecimalField(max_digits=8, decimal_places=5)
	server = models.CharField(max_length=15)
	altitude = models.IntegerField
	groundspeed = models.IntegerField
	transponder = models.IntegerField
	heading = models.IntegerField


class Flights(models.Model):
	#autonumber
	date = models.DateField
	callsign = models.CharField(max_length=10)
	cid = models.ForeignKey('Users.cid')
	planned_aircraft = models.CharField(max_length=8)
	planned_tascruise = models.IntegerField
	planned_depairport = models.CharField(max_length=4)
	planned_altitude = models.IntegerField
	planned_destairport = models.CharField(max_length=4)
	planned_flighttype = models.CharField(max_length=1)
	planned_deptime = models.TimeField
	planned_actdeptime = models. TimeField
	planned_altairport = models.CharField(max_length=4)
	planned_remarks = models.CharField(max_length=255)
	planned_route = models.TextField
	time_logon = models.DateTimeField
	Routestring = models.TextField

class ActiveControllers(models.Model):
	datetime = models.DateTimeField
	callsign = models.CharField(max_length=10)
	cid = models.ForeignKey('Users.cid')
	clienttype = models.CharField(max_length=10)
	frequency = models.DecimalField(max_digits=6, decimal_places=3)
	latitude = models.DecimalField(max_digits=7, decimal_places=5)
	longitude = models.DecimalField(max_digits=8, decimal_places=5)
	server = models.CharField(max_length=15)
	facilitytype = models.CharField(max_digits=1)
	visualrange = models.IntegerField
	time_logon = models.DateTimeField

class Controllers(models.Model):
	date = models.DateField
	callsign = models.CharField(maxlength=10)
	cid = models.ForeignKey('Users.cid')
	facilitytype = models.CharField(max_digits=1)
	TotalTime = models.IntegerField
