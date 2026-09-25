import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import io
from PIL import Image

print("Loading ERA5 dataset...")
ds = xr.open_dataset("bandung_era5.nc")

if 'valid_time' in ds.coords:
    ds = ds.rename({'valid_time': 'time'})

# Convert meters to mm
ds['tp_mm'] = ds['tp'] * 1000.0

# Calculate diurnal cycle (mean for each of the 24 UTC hours)
diurnal_cycle = ds['tp_mm'].groupby('time.hour').mean(dim='time')

# Fixed color levels from 0 to 2.5 mm/hr so colors stay consistent across frames
levels = np.linspace(0, 2.5, 16)

cities = {
    'Jakarta': (106.82, -6.17),
    'Bandung': (107.61, -6.91),
    'Jatinangor': (107.77, -6.93),
    'Pelabuhan Ratu': (106.55, -6.98)
}

frames = []

print("Generating 24 hourly frames...")

# Loop through all 24 hours of the day in WIB (00 to 23)
for wib_hour in range(24):
    # ERA5 is in UTC (WIB is UTC+7)
    utc_hour = (wib_hour - 7) % 24
    rain_data = diurnal_cycle.sel(hour=utc_hour)

    fig = plt.figure(figsize=(9, 6.5))
    ax = plt.axes(projection=ccrs.PlateCarree())

    # 1. Rain contours with fixed levels
    cf = rain_data.plot.contourf(
        ax=ax,
        transform=ccrs.PlateCarree(),
        cmap='Blues',
        levels=levels,
        extend='max',
        zorder=1,
        cbar_kwargs={'label': 'Rainfall Rate (mm/hour)', 'shrink': 0.8}
    )

    # 2. Map geography & gridlines
    ax.add_feature(cfeature.COASTLINE, linewidth=1.5, zorder=2)
    gl = ax.gridlines(draw_labels=True, linestyle='--', color='black', alpha=0.4, zorder=3)
    gl.top_labels = False
    gl.right_labels = False

    # 3. Reference markers
    for city, (lon, lat) in cities.items():
        ax.plot(lon, lat, marker='o', color='red', markersize=4, transform=ccrs.PlateCarree(), zorder=4)
        ax.text(lon + 0.05, lat + 0.05, city, color='black', fontweight='bold',
                fontsize=9, transform=ccrs.PlateCarree(), zorder=4)

    plt.title(f"West Java Rainfall Diurnal Cycle — {wib_hour:02d}:00 WIB ({utc_hour:02d}:00 UTC)", 
              fontweight="bold", fontsize=12)

    # Save current frame into memory buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    buf.seek(0)
    frames.append(Image.open(buf).copy())
    plt.close(fig)

    print(f"  Frame {wib_hour + 1}/24 done ({wib_hour:02d}:00 WIB)")

# Save all frames into an animated GIF
print("\nStitching frames into GIF...")
frames[0].save(
    "bandung_diurnal_cycle.gif",
    save_all=True,
    append_images=frames[1:],
    duration=350,  # Milliseconds per frame (~3 frames per second)
    loop=0         # Loop infinitely
)

print("Saved: bandung_diurnal_cycle.gif")
