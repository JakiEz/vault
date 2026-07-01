"""
Heliostat — CUMCM 2023 Problem A — Q1 COMPLETE (all 5 optical losses), Numba.
Steps 1-5: solar geometry, cosine, atmospheric, reflectivity, shadow/blocking,
and Monte-Carlo truncation. Hot path compiled with @njit.

Milestone snapshot (2026-06-28):
  slope 2 mrad -> 31.17 MW / 0.496 kW/m²
  slope 1 mrad -> 33.39 MW / 0.532 kW/m²   (Paper 2 ≈ 34.8 / 0.554)
  Implied optical efficiency ~0.55-0.57 (papers: 0.569-0.586).

Numba notes: no np.cross / np.linalg.norm inside @njit (scalar math instead);
frames stored as an (N,12) array; neighbor lists in CSR form (nbr_flat + nbr_start);
loops live inside the @njit kernel. MC truncation is random -> result wiggles slightly.

Reads 附件.csv. Receiver cylinder (0,0): Rc=3.5, z in [76,84]. Q1 mirrors 6x6, install 4 m.
See Inbox/Heliostat_StudyLog.md for the running log. Next: Table 1/2 reporting, then Q2/Q3.
"""

from numba import njit
import numpy as np
import csv
import math

# --- load mirror positions ---
x_coords, y_coords = [], []
with open('附件.csv', mode='r', encoding='utf-8') as file:
    csvFile = csv.reader(file)
    next(csvFile)
    for row in csvFile:
        if not row:
            continue
        x_coords.append(float(row[0]))
        y_coords.append(float(row[1]))

xs = np.array(x_coords)
ys = np.array(y_coords)

GRID = 5
offs = np.linspace(-3, 3, GRID)

ST = [9.0, 10.5, 12.0, 13.5, 15.0]
month = ["January", "February", "March", "April", "May", "June",
         "July", "August", "September", "October", "November", "December"]
monthDist = [-59, -28, 0, 31, 61, 92, 122, 153, 183, 214, 245, 275]
pie = np.pi
latitude = math.radians(39.4)

# DNI constants
H, G0 = 3.0, 1.366
a = 0.4237 - 0.00821*(6 - H)**2
b = 0.5055 + 0.00595*(6.5 - H)**2
c = 0.2711 + 0.01858*(2.5 - H)**2

# field constants
mirrorHeight = 4
height = 80 - mirrorHeight       # 76 m vertical gap
rho = 0.92
area = 6*6
R = 25.0                         # neighbor radius (shadow/block)

# receiver cylinder + beam spread (params [assumed], not in the doc)
Rc = 3.5
z_lo, z_hi = 76.0, 84.0
sigma_sun   = 0.00251            # ~2.51 mrad sun spread [standard]
sigma_slope = 0.001             # ~1 mrad mirror slope error [assumed, tunable knob]
sigma_beam  = math.sqrt(sigma_sun**2 + (2*sigma_slope)**2)
N_trunc = 200

# --- neighbor lists within R, then CSR form (once) ---
neighbors = [[] for _ in range(len(xs))]
for i in range(len(xs)):
    xi, yi = xs[i], ys[i]
    for j in range(len(xs)):
        if i != j and (xs[j]-xi)**2 + (ys[j]-yi)**2 <= R*R:
            neighbors[i].append(j)

nbr_start = np.zeros(len(xs)+1, dtype=np.int64)
for i in range(len(xs)):
    nbr_start[i+1] = nbr_start[i] + len(neighbors[i])
nbr_flat = np.empty(nbr_start[-1], dtype=np.int64)
idx = 0
for i in range(len(xs)):
    for j in neighbors[i]:
        nbr_flat[idx] = j; idx += 1

# --- solar geometry (plain Python, once per timestamp) ---
def hourAngleF(time):
    return round((pie/12) * (float(time) - 12), 3)

def declination(monthDist):
    sin_dec = np.sin((2*pie*monthDist)/365) * np.sin((2*pie*23.45)/360)
    return round(math.asin(sin_dec), 3)

def altitudeAngle(hourAngle, declination, latitude):
    return (math.cos(declination)*math.cos(latitude)*math.cos(hourAngle)
            + math.sin(declination)*math.sin(latitude))

def asimuth(sinAltitude, hourAngle, declination, latitude):
    cosAltitude = np.cos(np.arcsin(sinAltitude))
    cosGamma = (math.sin(declination) - sinAltitude*math.sin(latitude)) / (cosAltitude*math.cos(latitude))
    cosGamma = max(-1, min(1, cosGamma))
    gamma0 = math.acos(cosGamma)
    return gamma0 if hourAngle <= 0 else 2*pie - gamma0

def dni(sin_altitude):
    return round(G0 * (a + b*math.exp(-c/sin_altitude)), 3)

def sunVector(sin_alt, A):
    cos_alt = math.sqrt(1 - sin_alt**2)
    return (cos_alt*math.sin(A), cos_alt*math.cos(A), sin_alt)

# --- Numba kernels (scalar math, no np.cross/norm) ---
@njit
def compute_frames(xs, ys, sx, sy, sz, height):
    N = xs.shape[0]
    F = np.empty((N, 12))                        # n(0-2) u(3-5) v(6-8) t̂(9-11)
    for i in range(N):
        x, y = xs[i], ys[i]
        tx, ty, tz = -x, -y, height
        tl = math.sqrt(tx*tx+ty*ty+tz*tz); tx/=tl; ty/=tl; tz/=tl
        nx, ny, nz = sx+tx, sy+ty, sz+tz
        nl = math.sqrt(nx*nx+ny*ny+nz*nz); nx/=nl; ny/=nl; nz/=nl
        ux, uy = ny, -nx
        ul = math.sqrt(ux*ux+uy*uy); ux/=ul; uy/=ul; uz = 0.0
        vx = ny*uz - nz*uy
        vy = nz*ux - nx*uz
        vz = nx*uy - ny*ux
        F[i,0],F[i,1],F[i,2] = nx,ny,nz
        F[i,3],F[i,4],F[i,5] = ux,uy,uz
        F[i,6],F[i,7],F[i,8] = vx,vy,vz
        F[i,9],F[i,10],F[i,11] = tx,ty,tz
    return F

@njit
def hit_rect(Px,Py,Pz, dx,dy,dz, Cx,Cy,Cz, nx,ny,nz, ux,uy,uz, vx,vy,vz, half):
    denom = dx*nx + dy*ny + dz*nz
    if abs(denom) < 1e-9: return False
    s = ((Cx-Px)*nx + (Cy-Py)*ny + (Cz-Pz)*nz) / denom
    if s <= 1e-6: return False
    wx, wy, wz = Px+s*dx-Cx, Py+s*dy-Cy, Pz+s*dz-Cz
    return abs(wx*ux+wy*uy+wz*uz) <= half and abs(wx*vx+wy*vy+wz*vz) <= half

@njit
def hit_cyl(Px,Py,Pz, rx,ry,rz):
    A = rx*rx + ry*ry
    if A < 1e-12: return False
    B = 2.0*(Px*rx + Py*ry)
    C = Px*Px + Py*Py - Rc*Rc
    disc = B*B - 4.0*A*C
    if disc < 0.0: return False
    s = (-B - math.sqrt(disc)) / (2.0*A)
    if s <= 1e-6: return False
    z = Pz + s*rz
    return z_lo <= z <= z_hi

@njit
def timestep_power(xs, ys, F, sx, sy, sz, DNI, nbr_flat, nbr_start, mh, height, rho, area, offs):
    N = xs.shape[0]; G = offs.shape[0]
    total = 0.0
    for i in range(N):
        xi, yi = xs[i], ys[i]
        dot = sx*F[i,9] + sy*F[i,10] + sz*F[i,11]
        eta_cos = math.sqrt((1.0+dot)/2.0)
        dHR = math.sqrt(xi*xi + yi*yi + height*height)
        eta_at = 0.99321 - 0.0001176*dHR + 1.97e-8*dHR*dHR
        Cx,Cy,Cz = xi, yi, mh
        ux,uy,uz = F[i,3],F[i,4],F[i,5]
        vx,vy,vz = F[i,6],F[i,7],F[i,8]
        tx,ty,tz = F[i,9],F[i,10],F[i,11]

        # shadow & blocking
        clear = 0; totp = 0
        for aa in range(G):
            for bb in range(G):
                Px = Cx+offs[aa]*ux+offs[bb]*vx
                Py = Cy+offs[aa]*uy+offs[bb]*vy
                Pz = Cz+offs[aa]*uz+offs[bb]*vz
                totp += 1; blocked = False
                for k in range(nbr_start[i], nbr_start[i+1]):
                    j = nbr_flat[k]
                    if (hit_rect(Px,Py,Pz, sx,sy,sz, xs[j],ys[j],mh,
                                 F[j,0],F[j,1],F[j,2],F[j,3],F[j,4],F[j,5],F[j,6],F[j,7],F[j,8],3.0) or
                        hit_rect(Px,Py,Pz, tx,ty,tz, xs[j],ys[j],mh,
                                 F[j,0],F[j,1],F[j,2],F[j,3],F[j,4],F[j,5],F[j,6],F[j,7],F[j,8],3.0)):
                        blocked = True; break
                if not blocked: clear += 1
        eta_sb = clear/totp

        # truncation (Monte-Carlo)
        e1x, e1y, e1z = ty, -tx, 0.0                  # t̂ × ẑ
        e1l = math.sqrt(e1x*e1x + e1y*e1y); e1x/=e1l; e1y/=e1l
        e2x = ty*e1z - tz*e1y                         # t̂ × e1
        e2y = tz*e1x - tx*e1z
        e2z = tx*e1y - ty*e1x
        hits = 0
        for _ in range(N_trunc):
            r1 = (np.random.random()*2.0-1.0)*3.0
            r2 = (np.random.random()*2.0-1.0)*3.0
            Px = Cx + r1*ux + r2*vx
            Py = Cy + r1*uy + r2*vy
            Pz = Cz + r1*uz + r2*vz
            th1 = np.random.normal(0.0, sigma_beam)
            th2 = np.random.normal(0.0, sigma_beam)
            rx = tx + th1*e1x + th2*e2x
            ry = ty + th1*e1y + th2*e2y
            rz = tz + th1*e1z + th2*e2z
            rl = math.sqrt(rx*rx+ry*ry+rz*rz); rx/=rl; ry/=rl; rz/=rl
            if hit_cyl(Px,Py,Pz, rx,ry,rz):
                hits += 1
        eta_trunc = hits/N_trunc

        total += DNI * area * (eta_cos * rho * eta_at * eta_sb * eta_trunc)
    return total

# --- main loop ---
all_powers = []
for g in range(len(month)):
    declinated = declination(monthDist[g])
    for h in range(len(ST)):
        sin_alt = round(altitudeAngle(hourAngleF(ST[h]), declinated, latitude), 3)
        sv  = sunVector(sin_alt, asimuth(sin_alt, hourAngleF(ST[h]), declinated, latitude))
        DNI = dni(sin_alt)
        F = compute_frames(xs, ys, sv[0], sv[1], sv[2], height)
        fp = timestep_power(xs, ys, F, sv[0], sv[1], sv[2], DNI,
                            nbr_flat, nbr_start, mirrorHeight, height, rho, area, offs)
        all_powers.append(fp/1000)

# per-month (Table 1) averages
per_month_power = []
count = 0
for w in range(12):
    s = 0.0
    for u in range(5):
        s += all_powers[count]; count += 1
    per_month_power.append(round(s/5, 3))

annual_avg = sum(all_powers) / len(all_powers)
total_area = len(xs) * area
per_area   = annual_avg * 1000 / total_area
print("Annual Average Power is: " + str(round(annual_avg, 3)) + " MW")
print("Annual Average Power per Area is: " + str(round(per_area, 3)) + " kW/m^2")
