from time import sleep

from e_drone.drone import *
from e_drone.protocol import *
def eventAltitude(altitude):
    print("eventAltitude()")
    print("-  Temperature: {0:.3f}".format(altitude.temperature))
    print("-     Pressure: {0:.3f}".format(altitude.pressure))
    print("-     Altitude: {0:.3f}".format(altitude.altitude))
    print("- Range Height: {0:.3f}".format(altitude.rangeHeight))

if __name__=='__main__':
	
	drone = Drone()
	drone.open("COM5")
	drone.sendLostConnection(1000,1000,5000)
	drone.setEventHandler(DataType.Altitude, eventAltitude)
	print("TakeOff")
	drone.sendTakeOff()
	for i in range(3, 0, -1):
		print("{0}".format(i))
		drone.sendRequest(DeviceType.Drone, DataType.Altitude)
		sleep(1)

	drone.sendControlPosition(1.0, 1.0, 1.0, 0.5, 0, 0)
	sleep(1.0)
	print("Hovering")
	drone.sendControlWhile(0, 0, 0, 0, 6400)
	sleep(0.01)
	print("Return Home")
	drone.sendFlightEvent(FlightEvent.Return)
	for i in range(5, 0, -1):
		print("{0}".format(i))
		sleep(1)

	print("Landing")
	drone.sendLanding()
	for i in range(3, 0, -1):
		print("{0}".format(i))
		sleep(1)
	print("Stop")
	drone.sendStop()
	sleep(0.01)
	
drone.close()
print("All done")
