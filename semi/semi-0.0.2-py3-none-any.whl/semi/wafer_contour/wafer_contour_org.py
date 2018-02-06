# -*- coding: utf-8 -*-

### imports ###################################################################
import matplotlib.pyplot as plt
import numpy as np

###############################################################################
r = 156. # wafer radius
ds = 5. # sensor range
s_min = -r - ds
s_max = r + ds

### wafer offset
dx = 1.
dy = -0.5
d_xy = np.sqrt(dx**2 + dy**2)
alpha_xy = np.arctan2(dy, dx)
alpha_xy_deg = np.rad2deg(alpha_xy)
print('alpha_xy = %6.2f deg' % alpha_xy_deg)
print('d_xy = %5.3f mm' % d_xy)

### flat @ 0 deg.
f = 32.5
d_flat = r - np.sqrt(r**2 - f**2 / 4)
h_flat = r - d_flat
alpha_flat_1 = np.arctan((f / 2  - dy) / (dx + h_flat))
alpha_flat_2 = np.arctan((f / 2  + dy) / (dx + h_flat))

### main flat @ 90 deg.
f_main = 50.
d_flat_main = r - np.sqrt(r**2 - f_main**2 / 4)
h_flat_main = r - d_flat_main
alpha_flat_main_1 = np.arctan((f_main / 2  + dx) / (dy + h_flat_main))
alpha_flat_main_2 = np.arctan((f_main / 2  - dx) / (dy + h_flat_main))


circle = plt.Circle((0., 0.), s_max, color='blue')
inner_circle = plt.Circle((0., 0.), r - ds, color='white')
wafer_contour = plt.Circle((dx, dy), r, color='k', fill=False)

flat = plt.Line2D(
    [h_flat + dx, h_flat + dx], [-f/2 + dy, f/2 + dy], color='k')

offset = plt.Line2D(
    [dx, dx + r * np.cos(alpha_xy)], [dy, dy + r * np.sin(alpha_xy)])

plt.close('all')

# fig, ax = plt.subplots()
ax = plt.subplot(211)

# ax.add_artist(circle)
# ax.add_artist(inner_circle)
ax.add_artist(wafer_contour)
ax.add_artist(offset)
ax.add_artist(flat)

plt.xlim((1.1 * s_min, 1.1 * s_max))
plt.ylim((1.1 * s_min, 1.1 * s_max))
ax.set_aspect('equal')

plt.subplot(212)
alpha_deg =  np.linspace(-180., 180., num=361)
alpha = np.radians(alpha_deg)
y = r + d_xy * np.cos(alpha - alpha_xy)

plt.plot(alpha_deg, y - r)

# plt.subplot(2,2,3)
alpha = np.linspace(-alpha_flat_1, alpha_flat_2, 100)
alpha_deg = np.rad2deg(alpha)
r_flat = (h_flat + dx) / np.cos(alpha)

plt.plot(alpha_deg, r_flat - r)

# main flat
alpha = np.linspace(-alpha_flat_main_1, alpha_flat_main_2, 100)
alpha_deg = np.rad2deg(alpha) + 90
r_flat = (h_flat_main + dy) / np.cos(alpha)

plt.plot(alpha_deg, r_flat - r)


