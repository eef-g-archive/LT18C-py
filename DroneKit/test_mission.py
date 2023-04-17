from pihawk_template import Pihawk

waypoints = { "grimm_grass_sw_corner": (33.653957, -117.812063, 10),
              "grimm_grass_se_corner": (33.653939, -117.811485, 10),
              "grimm_grass_ne_corner": (33.654386, -117.811511, 10) }

drone = Pihawk()
drone.arm()
drone.takeoff(1)
time.sleep(3)
drone.land()
drone.disarm()
