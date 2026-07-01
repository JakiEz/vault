"""
Heliostat — CUMCM 2023 Problem A
Step 4: adds shadow & blocking (η_sb) via ray geometry. η_trunc still = 1.

Milestone snapshot (2026-06-28):
  annual average 41 → 37.245 MW, per-unit-area 0.65 → 0.593 kW/m²  (≈9% shadow/block loss).
  Next: Step 5 truncation → expect ~35 MW (validate vs Paper 2 ≈ 34.8).

Geometry engine (all standard vector geometry, not in the problem doc):
  mirror_frame  — a mirror as a tilted rectangle (center + normal + two surface axes)
  ray_hits_rect — ray→plane intersect + in-rectangle test
  shadow_block_eff — 5×5 sample grid, cast rays toward sun (shadow) & receiver (block)
  neighbors — precomputed once, mirrors within R=25 m (avoid all-pairs)

Reads 附件.csv. Receiver (0,0,80); Q1 mirrors 6×6 m, install height 4 m.
See Inbox/Heliostat_StudyLog.md for the running log.
"""

import numpy as np
import csv
import math

# --- load mirror positions ---
x_coords, y_coords = [], []
with open('附件.csv', mode='r', encoding='utf-8') as file:
    csvFile = csv.reader(file)
    next(csvFile)                                  # skip header
    for row in csvFile:
        if not row:
            continue
        x_coords.append(float(row[0]))
        y_coords.append(float(row[1]))

# --- sample timestamps ---
ST = [9.0, 10.5, 12.0, 13.5, 15.0]
month = ["January", "February", "March", "April", "May", "June",
         "July", "August", "September", "October", "November", "December"]
monthDist = [-59, -28, 0, 31, 61, 92, 122, 153, 183, 214, 245, 275]

pie = np.pi
latitude = math.radians(39.4)

# --- DNI constants (H = 3 km) ---
H, G0 = 3.0, 1.366
a = 0.4237 - 0.00821*(6 - H)**2
b = 0.5055 + 0.00595*(6.5 - H)**2
c = 0.2711 + 0.01858*(2.5 - H)**2

# --- field constants ---
mirrorHeight = 4
height = 80 - mirrorHeight        # 76 m vertical gap mirror-center -> receiver-center
rho = 0.92                        # η_ref
area = 6*6                        # A_i = 36 m² (Q1)


def hourAngleF(time):
    return round((pie/12) * (float(time) - 12), 3)

def declination(monthDist):
    sin_dec = np.sin((2*pie*monthDist)/365) * np.sin((2*pie*23.45)/360)
    return round(math.asin(sin_dec), 3)

def altitudeAngle(hourAngle, declination, latitude):
    return (math.cos(declination)*math.cos(latitude)*math.cos(hourAngle)
            + math.sin(declination)*math.sin(latitude))          # sin(altitude)

def asimuth(sinAltitude, hourAngle, declination, latitude):
    cosAltitude = np.cos(np.arcsin(sinAltitude))
    cosGamma = (math.sin(declination) - sinAltitude*math.sin(latitude)) \
               / (cosAltitude*math.cos(latitude))
    cosGamma = max(-1, min(1, cosGamma))
    gamma0 = math.acos(cosGamma)
    return gamma0 if hourAngle <= 0 else 2*pie - gamma0          # radians from north

def dni(sin_altitude):
    return round(G0 * (a + b*math.exp(-c/sin_altitude)), 3)

def sunVector(sin_alt, A):
    cos_alt = math.sqrt(1 - sin_alt**2)
    return (cos_alt*math.sin(A), cos_alt*math.cos(A), sin_alt)   # (East, North, Up)

def dotProduct(s_x, s_y, s_z, x, y, z):
    L = math.sqrt(x**2 + y**2 + z**2)
    t = (-x/L, -y/L, z/L)
    return s_x*t[0] + s_y*t[1] + s_z*t[2]

def cosineEfficiency(dot_product):
    return math.sqrt((1 + dot_product) / 2)

def atmospheric(d_HR):
    return 0.99321 - 0.0001176*d_HR + 1.97e-8*d_HR**2

# ---- geometry engine ----
def mirror_frame(x, y, sv):
    C = np.array([x, y, mirrorHeight])
    t = np.array([-x, -y, height]); t = t/np.linalg.norm(t)
    n = np.array(sv) + t;           n = n/np.linalg.norm(n)      # normal (reflection law)
    u = np.cross(n, [0, 0, 1]);     u = u/np.linalg.norm(u)      # width axis (horizontal)
    v = np.cross(n, u)                                           # height axis
    return C, n, u, v

def ray_hits_rect(P, d, C, n, u, v, half=3.0):
    denom = np.dot(d, n)
    if abs(denom) < 1e-9:                 # parallel to the plane
        return False
    s = np.dot(C - P, n) / denom
    if s <= 1e-6:                         # crossing behind the start
        return False
    X = P + s*d
    w = X - C
    return abs(np.dot(w, u)) <= half and abs(np.dot(w, v)) <= half

GRID = 5
sample_offsets = np.linspace(-3, 3, GRID)

def shadow_block_eff(i, sv, frames, neighbors):
    C, n, u, v = frames[i]
    s_hat = np.array(sv)                                          # toward sun (shadow)
    t = np.array([-x_coords[i], -y_coords[i], height])
    t = t/np.linalg.norm(t)                                      # toward receiver (block)
    total = clear = 0
    for du in sample_offsets:
        for dv in sample_offsets:
            P = C + du*u + dv*v
            total += 1
            blocked = False
            for j in neighbors[i]:
                Cj, nj, uj, vj = frames[j]
                if ray_hits_rect(P, s_hat, Cj, nj, uj, vj) or ray_hits_rect(P, t, Cj, nj, uj, vj):
                    blocked = True
                    break
            if not blocked:
                clear += 1
    return clear / total


# ---- neighbor lists: ONCE (geometry doesn't depend on the sun) ----
R = 25.0
neighbors = []
for i in range(len(x_coords)):
    near = []
    xi, yi = x_coords[i], y_coords[i]
    for j in range(len(x_coords)):
        if i != j and (x_coords[j]-xi)**2 + (y_coords[j]-yi)**2 <= R*R:
            near.append(j)
    neighbors.append(near)

# ---- main loop ----
all_powers = []
for g in range(len(month)):
    declinated = declination(monthDist[g])
    for h in range(len(ST)):
        hourAngle    = hourAngleF(ST[h])
        sin_altitude = round(altitudeAngle(hourAngle, declinated, latitude), 3)
        azimuth      = asimuth(sin_altitude, hourAngle, declinated, latitude)
        sv  = sunVector(sin_altitude, azimuth)
        DNI = dni(sin_altitude)
        frames = [mirror_frame(x_coords[k], y_coords[k], sv) for k in range(len(x_coords))]

        field_power = 0.0
        for i in range(len(x_coords)):
            d_HR      = math.sqrt(x_coords[i]**2 + y_coords[i]**2 + height**2)
            eta_cos   = cosineEfficiency(dotProduct(sv[0], sv[1], sv[2], x_coords[i], y_coords[i], height))
            eta_at    = atmospheric(d_HR)
            eta_sb    = shadow_block_eff(i, sv, frames, neighbors)
            eta_trunc = 1.0                                        # TODO Step 5
            eta = eta_cos * rho * eta_at * eta_sb * eta_trunc
            field_power += DNI * area * eta

        all_powers.append(field_power / 1000)                     # MW

annual_avg = sum(all_powers) / len(all_powers)
total_area = len(x_coords) * area
per_area   = annual_avg * 1000 / total_area
print("Annual Average Power: " + str(round(annual_avg, 3)) + " MW")
print("Per unit mirror area: " + str(round(per_area, 3)) + " kW/m^2")
