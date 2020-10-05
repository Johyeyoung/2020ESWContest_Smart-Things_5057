from time import sleep

from e_drone.drone import *
from e_drone.protocol import *

# 드론에게 data를 수신했을때 호출되는 함수
def eventAltitude(altitude):
    print("eventAltitude()")
    print("-  Temperature: {0:.3f}".format(altitude.temperature))
    print("-     Pressure: {0:.3f}".format(altitude.pressure))
    print("-     Altitude: {0:.3f}".format(altitude.altitude))
    print("- Range Height: {0:.3f}".format(altitude.rangeHeight))

if __name__=='__main__':
	
	drone = Drone()
	
	# COM5에 연결된 컨트롤러와 드론 연결
	drone.open("COM5")
	# 드론과 연결 끊기면 1초 후 착륙
	drone.sendLostConnection(1000,1000,5000)
	drone.setEventHandler(DataType.Altitude, eventAltitude)
	# 드론 이륙 명령 전송
	print("TakeOff")
	drone.sendTakeOff()
	for i in range(3, 0, -1):
		print("{0}".format(i))
		drone.sendRequest(DeviceType.Drone, DataType.Altitude)
		sleep(1)
	# 지정 위치로 이동 명령 전송
	drone.sendControlPosition(1.0, 0.2, 0.7, 0.5, 0, 0)
	# 10초간 호버링
	print("Hovering")
	drone.sendControlWhile(0, 0, 0, 0, 10000)
	sleep(0.01)
	# 최초 이륙한 위치로 복귀
	print("Return Home")
	drone.sendFlightEvent(FlightEvent.Return)
	for i in range(5, 0, -1):
		print("{0}".format(i))
		sleep(1)
	# 착륙
	print("Landing")
	drone.sendLanding()
	for i in range(3, 0, -1):
		print("{0}".format(i))
		sleep(1)
	# 종료
	print("Stop")
	drone.sendStop()
	sleep(0.01)

drone.close()
print("All done")
