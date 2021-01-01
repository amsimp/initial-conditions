# Import dependices.
import wget
from datetime import datetime, timedelta
import numpy as np
import iris
import os
from tqdm import tqdm
from astropy import units

# Define preliminary urls.
# 2-m temperature.
tmp_url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gdas_0p25.pl?file=gdas.t{}z.pgrb2.0p25.f{}&lev_2_m_above_ground=on&var_TMP=on&leftlon=0&rightlon=360&toplat=90&bottomlat=-90&dir=%2Fgdas.{}"
# 850 hPa temperature.
t850_url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gdas_0p25.pl?file=gdas.t{}z.pgrb2.0p25.f{}&lev_850_mb=on&var_TMP=on&leftlon=0&rightlon=360&toplat=90&bottomlat=-90&dir=%2Fgdas.{}"
# 500 hPa geopotential height.
z500_url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gdas_0p25.pl?file=gdas.t{}z.pgrb2.0p25.f{}&lev_500_mb=on&var_HGT=on&leftlon=0&rightlon=360&toplat=90&bottomlat=-90&dir=%2Fgdas.{}"
# Total precipitation.
prate_url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gdas_0p25.pl?file=gdas.t{}z.pgrb2.0p25.f{}&all_lev=on&var_PRATE=on&var_VGRD=on&leftlon=0&rightlon=360&toplat=90&bottomlat=-90&dir=%2Fgdas.{}"

# Retrieve date.
date = datetime.now()
current_date = date.replace(
    hour=date.hour - (date.hour % 6),
    minute=0,
    second=0,
    microsecond=0
) - timedelta(hours=12)

# Forecast hours.
hours = [[2, 4, 6], [2, 4, 6]]

# Retrieve current conditions.
files = []
def download_var(href):
    # Define output cube list.
    cubelist = iris.cube.CubeList([])

    # Define date.
    date = current_date

    for j in range(2):
        # Retrieve forecast hour.
        str_date = date.strftime('%Y%m%d') + "%2F"
        forecast_hour = date.strftime('%H')

        for i in range(3):
            # Define hour.
            hour = '%03d' % hours[j][i]

            # Define download file.
            url = href.format(
                forecast_hour, hour, str_date
            ) + forecast_hour

            # Download file.
            file = wget.download(url, bar=None)
            files.append(file)

            # Load file.
            var_data = iris.load(file)[0]
            var_data.data

            # Remove forecast period coordinates.
            var_data.remove_coord('forecast_period')

            # Remove forecast reference time.
            var_data.remove_coord('forecast_reference_time')

            # Delete file.
            os.remove(file)

            # Append to cube list.
            cubelist.append(var_data)

        # Increment time.
        date += timedelta(hours=6)

    # Concatenate.
    cubelist = cubelist.merge_cube()

    # Return cube.
    return cubelist

# Download.
# Progress bar.
t = tqdm(total=4, desc='Downloading')

# 2-m temperature.
tmp = download_var(tmp_url)
tmp.standard_name = None
tmp.long_name = '2m_temperature'
tmp.var_name = 't2m'
iris.save(tmp, 'initialisation_conditions/2m_temperature.nc')
t.update()

# 850 hPa temperature.
t850 = download_var(t850_url)
t850.var_name = 't'
iris.save(t850, 'initialisation_conditions/air_temperature.nc')
t.update()

# 500 hPa geopotential height.
g = 9.80665
z500 = download_var(z500_url) * g
z500.units = 'm2 s-2'
z500.standard_name = 'geopotential'
z500.var_name = 'z'
iris.save(z500, 'initialisation_conditions/geopotential.nc')
t.update()

# Precipitation rate.
prate = download_var(prate_url)
prate.convert_units('kg m-2 h-1')
t.update()
t.close()
# Convert precipitation rate to precipitation
# accumulation. 
tp = prate
tp.units = 'mm'
tp.standard_name = None
tp.long_name = 'total_precipitation'
tp.var_name = 'tp'
tp.convert_units('m')
iris.save(tp, 'initialisation_conditions/total_precipitation.nc')
