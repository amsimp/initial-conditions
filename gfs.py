# Import dependices.
import wget
from datetime import datetime, timedelta
import numpy as np
import iris
import os
from tqdm import tqdm
from astropy import units
import sys

# Define preliminary urls.
# Air temperature.
t_url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_1p00.pl?file=gfs.t{}z.pgrb2.1p00.f{}&lev_1000_mb=on&lev_100_mb=on&lev_15_mb=on&lev_200_mb=on&lev_250_mb=on&lev_300_mb=on&lev_400_mb=on&lev_500_mb=on&lev_50_mb=on&lev_600_mb=on&lev_700_mb=on&lev_850_mb=on&lev_925_mb=on&var_TMP=on&leftlon=0&rightlon=360&toplat=90&bottomlat=-90&dir=%2Fgfs.{}"
# Geopotential height.
z_url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_1p00.pl?file=gfs.t{}z.pgrb2.1p00.f{}&lev_1000_mb=on&lev_100_mb=on&lev_15_mb=on&lev_200_mb=on&lev_250_mb=on&lev_300_mb=on&lev_400_mb=on&lev_500_mb=on&lev_50_mb=on&lev_600_mb=on&lev_700_mb=on&lev_850_mb=on&lev_925_mb=on&var_HGT=on&leftlon=0&rightlon=360&toplat=90&bottomlat=-90&dir=%2Fgfs.{}"

# Retrieve date.
date = datetime.now()
date = date.replace(
    hour=date.hour - (date.hour % 6),
    minute=0,
    second=0,
    microsecond=0
) - timedelta(hours=6)

# Retrieve current conditions.
def download_var(href):
    # Retrieve forecast hour.
    str_date = date.strftime('%Y%m%d') + "%2F"
    forecast_hour = date.strftime('%H')

    # Define hour.
    hour = '%03d' % 0

    # Define download file.
    url = href.format(
        forecast_hour, hour, str_date
    ) + forecast_hour
    url += "%2Fatmos"

    # Download file.
    file = wget.download(url, bar=None)

    # Load file.
    cube = iris.load(file)[0]
    cube.data

    # Remove forecast period coordinates.
    cube.remove_coord('forecast_period')

    # Remove forecast reference time.
    cube.remove_coord('forecast_reference_time')

    # Delete file.
    os.remove(file)

    # Return cube.
    return cube

# Download.
# Progress bar.
pbar = tqdm(total=2, desc='Downloading')

# Air temperature.
t = download_var(t_url)
t.var_name = 't'
iris.save(t, 'gfs/t.nc')
pbar.update()

# Geopotential.
g = 9.80665
z = download_var(z_url) * g
z.units = 'm2 s-2'
z.standard_name = 'geopotential'
z.var_name = 'z'
iris.save(z, 'gfs/z.nc')
pbar.update()
