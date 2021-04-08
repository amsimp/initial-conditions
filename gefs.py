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
# 850 hPa temperature.
t850_url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gefs_atmos_0p50a.pl?file=ge{}.t{}z.pgrb2a.0p50.f{}&lev_850_mb=on&var_TMP=on&leftlon=0&rightlon=360&toplat=90&bottomlat=-90&dir=%2Fgefs.{}"
# 500 hPa geopotential height.
z500_url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gefs_atmos_0p50a.pl?file=ge{}.t{}z.pgrb2a.0p50.f{}&lev_500_mb=on&var_HGT=on&leftlon=0&rightlon=360&toplat=90&bottomlat=-90&dir=%2Fgefs.{}"

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
    # Define output cube list.
    cubelist = iris.cube.CubeList([])

    # Retrieve forecast hour.
    str_date = date.strftime('%Y%m%d') + "%2F"
    forecast_hour = date.strftime('%H')

    # Define hour.
    hour = '%03d' % 0

    for i in range(31):
        # Define ensemble members.
        if i == 0:
            member = "c%02d" % i
        else:
            member = "p%02d" % i

        # Define download file.
        url = href.format(
            member, forecast_hour, hour, str_date
        ) + forecast_hour
        url += '%2Fatmos%2Fpgrb2ap5'

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

        # Append to cube list.
        cubelist.append(cube)

    # Merge.
    cube = cubelist.merge()[0]

    # Return cube.
    return cube

# Download.
# Progress bar.
t = tqdm(total=2, desc='Downloading')

# 850 hPa temperature.
t850 = download_var(t850_url)
t850.var_name = 't'
iris.save(t850, 'gefs/t.nc')
t.update()

# 500 hPa geopotential height.
g = 9.80665
z500 = download_var(z500_url) * g
z500.units = 'm2 s-2'
z500.standard_name = 'geopotential'
z500.var_name = 'z'
iris.save(z500, 'gefs/z.nc')
t.update()
