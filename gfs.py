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
# 2-m temperature.
tmp_url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_1p00.pl?file=gfs.t{}z.pgrb2.1p00.f{}&lev_2_m_above_ground=on&var_TMP=on&leftlon=0&rightlon=360&toplat=90&bottomlat=-90&dir=%2Fgfs.{}"
# 850 hPa temperature.
t850_url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_1p00.pl?file=gfs.t{}z.pgrb2.1p00.f{}&lev_850_mb=on&var_TMP=on&leftlon=0&rightlon=360&toplat=90&bottomlat=-90&dir=%2Fgfs.{}"
# 500 hPa geopotential height.
z500_url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_1p00.pl?file=gfs.t{}z.pgrb2.1p00.f{}&lev_500_mb=on&var_HGT=on&leftlon=0&rightlon=360&toplat=90&bottomlat=-90&dir=%2Fgfs.{}"

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
t = tqdm(total=3, desc='Downloading')

# 2-m temperature.
tmp = download_var(tmp_url)
tmp.standard_name = None
tmp.long_name = '2m_temperature'
tmp.var_name = 't2m'
iris.save(tmp, 'gfs/t2m.nc')
t.update()

# 850 hPa temperature.
t850 = download_var(t850_url)
t850.var_name = 't'
iris.save(t850, 'gfs/t.nc')
t.update()

# 500 hPa geopotential height.
g = 9.80665
z500 = download_var(z500_url) * g
z500.units = 'm2 s-2'
z500.standard_name = 'geopotential'
z500.var_name = 'z'
iris.save(z500, 'gfs/z.nc')
t.update()
