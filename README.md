# AMSIMP Initial Conditions Repository

This repository contains initialisation conditions to generate a near real-time weather forecast. This functionality is embedded within AMSIMP.

The [GDAS](https://nomads.ncep.noaa.gov/txt_descriptions/GFS_doc.shtml) is a model to place observations into a gridded model space for the purpose of initialising weather forecasts with observed data. This system is utilised by the National Center for Environmental Prediction for such a purpose. GDAS adds the following types of observations to a gridded, 3-D, model space: surface observations, balloon data, wind profiler data, aircraft reports, buoy observations, radar observations, and satellite observations\cite{gdas}. The initial conditions provided by the GDAS to the software have a vertical pressure co-ordinate, or the vertical co-ordiante is pressure. This co-ordinate system is known as isobaric co-ordinates.

## License
This code is available under the MIT License.
