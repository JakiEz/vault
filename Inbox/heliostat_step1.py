"""
Heliostat — CUMCM 2023 Problem A
Step 1: solar geometry -> sun altitude + DNI for the 60 sample timestamps.

Milestone snapshot (2026-06-21). Validated on December:
  sin alpha: 0.249 / 0.403 / 0.457 / 0.403 / 0.249
  DNI (kW/m^2): 0.739 / 0.875 / 0.910 / 0.875 / 0.739   (noon = peak)

Next: build the sun 3D unit vector, then Step 2 (cosine / atmospheric / reflectivity).
See Inbox/Heliostat_StudyLog.md for the running log.
"""

import numpy as np
import math

# hour angle variables
ST = [9.0, 10.5, 12.0, 13.5, 15.0]

# declination variables
month = ["January", "February", "March", "April", "May", "June",
         "July", "August", "September", "October", "November", "December"]
monthDist = [-59, -28, 0, 31, 61, 92, 122, 153, 183, 214, 245, 275]  # days from spring equinox
pie = np.pi
latitude = math.radians(39.4)   # site latitude, 39.4 N (must be radians)

# DNI section variables — a, b, c depend only on altitude H (3 km), so compute once
H = 3.0
G0 = 1.366
a = 0.4237 - 0.00821 * (6 - H)**2
b = 0.5055 + 0.00595 * (6.5 - H)**2
c = 0.2711 + 0.01858 * (2.5 - H)**2


def hourAngleF(time):
    hourAngle = (pie / 12) * (float(time) - 12)
    hourAngle = round(hourAngle, 3)
    print("Sun Angle at " + str(time) + " is: " + str(hourAngle))
    return hourAngle


def season(month):
    sin_dec = np.sin((2 * pie * month) / 365) * np.sin((2 * pie * 23.45) / 360)  # sin(declination)
    declination = math.asin(sin_dec)   # real declination angle (radians)
    return round(declination, 3)


def altitude(hourAngle, declination, latitude):
    # returns sin(altitude)
    sunAltitude = (math.cos(declination) * math.cos(latitude) * math.cos(hourAngle)
                   + math.sin(declination) * math.sin(latitude))
    return sunAltitude


def dni(sin_altitude):
    dni = G0 * (a + (b * math.exp(-c / sin_altitude)))
    return round(dni, 3)


for g in range(len(month)):
    print("For month " + month[g] + ":")
    for h in range(len(ST)):
        sunAngle = round(altitude(hourAngleF(ST[h]), season(monthDist[g]), latitude), 3)  # this is sin(altitude)
        print("Sun Altitude at " + month[g] + " at " + str(ST[h]) + " is: " + str(sunAngle))
        print("DNI at " + month[g] + " at " + str(ST[h]) + " is: " + str(dni(sunAngle)))
    print("\n")
