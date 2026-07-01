"""
Heliostat - CUMCM 2023 Problem A - Step 6: Table 1 / Table 2 reporting.

Builds on heliostat_step5_numba.py (Q1 optical model complete, all 5 losses).
Adds: per-mirror sub-efficiencies (eta_cos, eta_sb, eta_at, eta_trunc) are now
accumulated inside the Numba kernel alongside power, so each timestamp yields
both a field power AND the mean of each efficiency term across all mirrors.

Table 1 = per-month average (5 daily times averaged) of: optical eta + the 4
sub-efficiencies + output power + per-unit-area power.
Table 2 = annual average (all 60 timestamps) of the same.

See Heliostat/Heliostat_StudyLog.md, Heliostat_Formulas.md (Step 6), and
Heliostat_CodeMap.md for the running log / derivations / function map.
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
sigma_slope = 0.001              # ~1 mrad mirror slope error [assumed, tunable knob]
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
    """Returns (field_power_kW, sum_eta_cos, sum_eta_sb, sum_eta_at, sum_eta_trunc,
    sum_eta_optical) - the sums are over all N mirrors for THIS timestamp; divide
    by N outside to get the timestamp's mean sub-efficiencies (Step 6)."""
    N = xs.shape[0]; G = offs.shape[0]
    total = 0.0
    sum_cos = 0.0; sum_sb = 0.0; sum_at = 0.0; sum_trunc = 0.0; sum_eta = 0.0
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

        eta = eta_cos * rho * eta_at * eta_sb * eta_trunc
        total += DNI * area * eta
        sum_cos += eta_cos
        sum_sb += eta_sb
        sum_at += eta_at
        sum_trunc += eta_trunc
        sum_eta += eta
    return total, sum_cos, sum_sb, sum_at, sum_trunc, sum_eta

# --- main loop: collect per-timestamp power + sub-efficiencies ---
N_mirrors = len(xs)
total_area = N_mirrors * area

ts_power = []       # field power [MW] per timestamp
ts_eta_cos = []
ts_eta_sb = []
ts_eta_at = []
ts_eta_trunc = []
ts_eta_opt = []      # overall optical efficiency per timestamp

for g in range(len(month)):
    declinated = declination(monthDist[g])
    for h in range(len(ST)):
        sin_alt = round(altitudeAngle(hourAngleF(ST[h]), declinated, latitude), 3)
        sv  = sunVector(sin_alt, asimuth(sin_alt, hourAngleF(ST[h]), declinated, latitude))
        DNI = dni(sin_alt)
        F = compute_frames(xs, ys, sv[0], sv[1], sv[2], height)
        fp, s_cos, s_sb, s_at, s_trunc, s_eta = timestep_power(
            xs, ys, F, sv[0], sv[1], sv[2], DNI,
            nbr_flat, nbr_start, mirrorHeight, height, rho, area, offs)
        ts_power.append(fp/1000)                    # kW -> MW
        ts_eta_cos.append(s_cos/N_mirrors)
        ts_eta_sb.append(s_sb/N_mirrors)
        ts_eta_at.append(s_at/N_mirrors)
        ts_eta_trunc.append(s_trunc/N_mirrors)
        ts_eta_opt.append(s_eta/N_mirrors)

# ---------- Table 1: per-month averages (5 daily times -> 1 row) ----------
def month_avg(series):
    out = []
    idx = 0
    for w in range(12):
        out.append(round(sum(series[idx:idx+5]) / 5, 4))
        idx += 5
    return out

t1_power   = month_avg(ts_power)
t1_cos     = month_avg(ts_eta_cos)
t1_sb      = month_avg(ts_eta_sb)
t1_at      = month_avg(ts_eta_at)
t1_trunc   = month_avg(ts_eta_trunc)
t1_opt     = month_avg(ts_eta_opt)
t1_perarea = [round(p*1000/total_area, 4) for p in t1_power]   # kW/m^2

print("=" * 100)
print("TABLE 1 - Per-month averages")
print("=" * 100)
header = f"{'Month':<10}{'eta_cos':>10}{'eta_sb':>10}{'eta_at':>10}{'eta_trunc':>10}{'eta_opt':>10}{'Power[MW]':>12}{'kW/m^2':>10}"
print(header)
for i in range(12):
    print(f"{month[i]:<10}{t1_cos[i]:>10}{t1_sb[i]:>10}{t1_at[i]:>10}{t1_trunc[i]:>10}{t1_opt[i]:>10}{t1_power[i]:>12}{t1_perarea[i]:>10}")

# ---------- Table 2: annual average (all 60 -> 1 row) ----------
annual_power   = round(sum(ts_power) / len(ts_power), 4)
annual_cos     = round(sum(ts_eta_cos) / len(ts_eta_cos), 4)
annual_sb      = round(sum(ts_eta_sb) / len(ts_eta_sb), 4)
annual_at      = round(sum(ts_eta_at) / len(ts_eta_at), 4)
annual_trunc   = round(sum(ts_eta_trunc) / len(ts_eta_trunc), 4)
annual_opt     = round(sum(ts_eta_opt) / len(ts_eta_opt), 4)
annual_perarea = round(annual_power*1000/total_area, 4)

print()
print("=" * 100)
print("TABLE 2 - Annual average")
print("=" * 100)
print(header)
print(f"{'Annual':<10}{annual_cos:>10}{annual_sb:>10}{annual_at:>10}{annual_trunc:>10}{annual_opt:>10}{annual_power:>12}{annual_perarea:>10}")
print()
print(f"Cross-check vs Paper 2 (trustworthy): optical eta ~0.569 (theirs) vs {annual_opt} (ours); power ~34.8 MW (theirs) vs {annual_power} MW (ours)")
