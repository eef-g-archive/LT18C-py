from pihawk_template import Pihawk

drone = Pihawk()
drone.arm()
drone.takeoff(1)
time.sleep(5)
drone.land()
drone.disarm()
