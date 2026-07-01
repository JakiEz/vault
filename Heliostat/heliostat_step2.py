"""
Heliostat — CUMCM 2023 Problem A
Steps 2 + 3: per-mirror optical efficiency (cosine, atmospheric, reflectivity)
and field power, for all 60 sample timestamps. η_sb = η_trunc = 1 (not yet modeled).

Milestone snapshot (2026-06-23). Inflated result (sb=trunc=1):
  annual average ≈ 41 MW, per-unit-area ≈ 0.65 kW/m².
  Hand-check Dec noon ≈ 37 MW. Will fall to realistic ~35 MW once shadow/block + truncation added.

Reads mirror positions from 附件.csv. Receiver at (0,0,80); Q1 mirrors 6×6 m, install height 4 m.
See Inbox/Heliostat_StudyLog.md for the running log. Next: Step 4, shadow & blocking.
"""

import numpy as np
import csv
import math

# --- load mirror positions (附件.csv: columns x (m), y (m)) ---
x_coords = []
y_coords = []
with open('附件.csv', mode='r', encoding='utf-8') as file:
    csvFile = csv.reader(file)
    next(csvFile)  # skip header row
    for row in csvFile:
        if not row:
            continue
        x_coords.append(float(row[0]))
        y_coords.append(float(row[1]))

# --- sample timestamps ---
ST = [9.0, 10.5, 12.0, 13.5, 15.0]
month = ["January", "February", "March", "April", "May", "June",
         "July", "August", "September", "October", "November", "December"]
monthDist = [-59, -28, 0, 31, 61, 92, 122, 153, 183, 214, 245, 275]  # days from spring equinox

pie = np.pi
latitude = math.radians(39.4)

# --- DNI constants (depend only on altitude H = 3 km) ---
H = 3.0
G0 = 1.366
a = 0.4237 - 0.00821*(6 - H)**2
b = 0.5055 + 0.00595*(6.5 - H)**2
c = 0.2711 + 0.01858*(2.5 - H)**2

# --- field constants ---
mirrorHeight = 4
height = 80 - mirrorHeight   # 76 m: vertical gap mirror-center -> receiver-center
rho = 0.92                   # reflectivity η_ref
area = 6*6                   # A_i = 36 m² per mirror (Q1)


def hourAngleF(time):
    return round((pie/12) * (float(time) - 12), 3)

def declination(monthDist):
    sin_dec = np.sin((2*pie*monthDist)/365) * np.sin((2*pie*23.45)/360)
    return round(math.asin(sin_dec), 3)        # real declination angle (radians)

def altitudeAngle(hourAngle, declination, latitude):
    return (math.cos(declination)*math.cos(latitude)*math.cos(hourAngle)
            + math.sin(declination)*math.sin(latitude))   # returns sin(altitude)

def asimuth(sinAltitude, hourAngle, declination, latitude):
    cosAltitude = np.cos(np.arcsin(sinAltitude))
    cosGamma = (math.sin(declination) - sinAltitude*math.sin(latitude)) \
               / (cosAltitude*math.cos(latitude))
    cosGamma = max(-1, min(1, cosGamma))       # clamp before acos
    gamma0 = math.acos(cosGamma)
    return gamma0 if hourAngle <= 0 else 2*pie - gamma0   # east/west sign fix; radians from north

def dni(sin_altitude):
    return round(G0 * (a + b*math.exp(-c/sin_altitude)), 3)

def sunVector(sin_alt, A):
    cos_alt = math.sqrt(1 - sin_alt**2)
    return (cos_alt*math.sin(A), cos_alt*math.cos(A), sin_alt)   # (East, North, Up)

def dotProduct(s_x, s_y, s_z, x, y, z):
    L = math.sqrt(x**2 + y**2 + z**2)
    t = (-x/L, -y/L, z/L)                      # unit mirror->receiver
    return s_x*t[0] + s_y*t[1] + s_z*t[2]

def cosineEfficiency(dot_product):
    return math.sqrt((1 + dot_product) / 2)

def atmospheric(d_HR):
    return 0.99321 - 0.0001176*d_HR + 1.97e-8*d_HR**2


all_powers = []
for g in range(len(month)):
    declinated = declination(monthDist[g])
    for h in range(len(ST)):
        hourAngle    = hourAngleF(ST[h])
        sin_altitude = altitudeAngle(hourAngle, declinated, latitude)
        azimuth      = asimuth(sin_altitude, hourAngle, declinated, latitude)
        sv           = sunVector(sin_altitude, azimuth)
        DNI          = dni(sin_altitude)

        field_power = 0.0
        for i in range(len(x_coords)):
            x, y    = x_coords[i], y_coords[i]
            d_HR    = math.sqrt(x**2 + y**2 + height**2)
            eta_cos = cosineEfficiency(dotProduct(sv[0], sv[1], sv[2], x, y, height))
            eta_at  = atmospheric(d_HR)
            eta_sb, eta_trunc = 1.0, 1.0        # TODO Step 4/5
            eta     = eta_cos * rho * eta_at * eta_sb * eta_trunc
            field_power += DNI * area * eta     # kW

        all_powers.append(field_power / 1000)   # MW

annual_avg = sum(all_powers) / len(all_powers)         # MW
total_area = len(x_coords) * area                       # m²
per_area   = annual_avg * 1000 / total_area             # kW/m²
print("Annual Average Power: " + str(round(annual_avg, 3)) + " MW")
print("Per unit mirror area: " + str(round(per_area, 3)) + " kW/m^2")
