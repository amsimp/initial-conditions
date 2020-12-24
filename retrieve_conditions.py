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
date = datetime.now() - timedelta(hours=6)
str_date = date.strftime('%Y%m%d') + "%2F"

# Retrieve forecast hour.
current_time = int(date.strftime('%H'))
nearest_forecast_hour = 6 * np.floor(current_time / 6)
forecast_hour = '%02d' % nearest_forecast_hour

# Retrieve current conditions.
files = []
def download_var(href):
    # Define output cube list.
    cubelist = iris.cube.CubeList([])

    for i in range(2):
        # Define hour.
        hour = '%03d' % (i + 4)

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

        # Delete file.
        os.remove(file)

        # Append to cube list.
        cubelist.append(var_data)

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
t.update()

# 850 hPa temperature.
t850 = download_var(t850_url)
t.update()

# 500 hPa geopotential height.
g = 9.80665
z500 = download_var(z500_url) * g
z500.units = 'm2 s-2'
z500.standard_name = 'geopotential'
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

# Combine variables into single cube list.
# Initial cube list.
data = iris.cube.CubeList([])

# Add.
# 2-m temperature.
data.append(tmp)
# 850 hPa temperature.
data.append(t850)
# 500 hPa geopotential height.
data.append(z500)
# Total precipitation.
data.append(tp)

# Save.
iris.save(data, 'initialisation_conditions.nc')
