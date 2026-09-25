import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# 1. Load and process data
ds = xr.open_dataset("bandung_era5.nc")
if 'valid_time' in ds.coords:
    ds = ds.rename({'valid_time': 'time'})

ds['tp_mm'] = ds['tp'] * 1000.0
diurnal_cycle = ds['tp_mm'].groupby('time.hour').mean(dim='time')

# 15:00 WIB = 08:00 UTC
rain_at_3pm = diurnal_cycle.sel(hour=8)

# 2. Setup the Map
fig = plt.figure(figsize=(10, 7))
ax = plt.axes(projection=ccrs.PlateCarree())

# Plot the rainfall (zorder=1 keeps it at the bottom layer)
plot = rain_at_3pm.plot.contourf(
    ax=ax,
    transform=ccrs.PlateCarree(),
    cmap='Blues',
    levels=15,
    zorder=1,
    cbar_kwargs={'label': 'Average Rainfall Rate (mm/hour)'}
)

# 3. Add Geographic Features ON TOP of the rain (zorder=2)
ax.add_feature(cfeature.COASTLINE, linewidth=1.5, zorder=2)

# Add Latitude/Longitude gridlines
gl = ax.gridlines(draw_labels=True, linestyle='--', color='black', alpha=0.5, zorder=3)
gl.top_labels = False
gl.right_labels = False

# 4. Plot specific city reference points
cities = {
    'Jakarta': (106.82, -6.17),
    'Bandung': (107.61, -6.91),
    'Jatinangor': (107.77, -6.93),
    'Pelabuhan Ratu': (106.55, -6.98)
}

for city, (lon, lat) in cities.items():
    ax.plot(lon, lat, marker='o', color='red', markersize=5, transform=ccrs.PlateCarree(), zorder=4)
    # Offset the text slightly so it doesn't overlap the dot
    ax.text(lon + 0.05, lat + 0.05, city, color='black', fontweight='bold', 
            fontsize=10, transform=ccrs.PlateCarree(), zorder=4)

plt.title("West Java Average Convective Rainfall at 15:00 WIB", fontweight="bold", fontsize=14)
plt.tight_layout()
plt.show()
