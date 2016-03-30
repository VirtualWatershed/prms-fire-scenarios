import json
import netCDF4

from numpy import where

from ..models import VegetationMapByHRU, ProjectionInformation

LEHMAN_CREEK_CELLSIZE = 100  # in meters; should be in netCDF, but it's not


def propagate_single_vegetation_change(original_prms_params, veg_value, hrus):
    """
    Given a PRMS netCDF file, a PRMS vegetation code (0-4), and a list of
    HRU indices that should be changed, update the seven other
    vegetation-dependent parameters.

    Arguments:
        original_prms_params (netCDF4.Dataset): The original parameters file
        veg_value (int): The vegetation value, must be 0, 1, 2, 3, or 4
        hrus (list(int)): List of HRU indices that should get the value given
    """
    assert veg_value in range(5), \
        "PRMS Vegetation Values must be an integer from 0 to 4"

    mod_prms_params = netCDF4.Dataset()

    return mod_prms_params


def propagate_all_vegetation_changes(original_prms_params, veg_map_by_hru):
    """
    Given a vegetation_updates object and an original_parameters netcdf,
    propagate the updates through the original prms params netcdf and return
    an updated copy of the PRMS parameter netCDF

    Arguments:
        original_prms_params (netCDF4.Dataset): Base PRMS parameters for the
            watershed under investigation
        veg_map_by_hru (dict): Dictionary with structure
            {
                'bare_ground': [ (HRUs with bare_ground) ],
                'grasses': [ (HRUs with grasses) ],
                #  ... and so on with fields as given in app/models.py
            }

    Returns:
        (netCDF4.Dataset) netCDF Dataset with parameters updated according to
            the veg_map_by_hru
    """
    ret = original_prms_params
    return ret


def get_veg_map_by_hru(prms_params):
    """
    Create the vegetation map by HRU, which will also include the elevations
    in an array indexed by HRU.

    Arguments:
        prms_params (netCDF4.Dataset): PRMS parameters netCDF
    Returns:
        (VegetationMapByHRU): JSON representation of the vegetation and
            elevation by HRU
    """
    # latitudes read from top to bottom
    upper_right_lat = prms_params.variables['lat'][:][0]
    lower_left_lat = prms_params.variables['lat'][:][-1]

    # longitudes get increasingly negative from right to left
    lower_left_lon = prms_params.variables['lon'][:][0]
    upper_right_lon = prms_params.variables['lon'][:][-1]

    ctv = prms_params.variables['cov_type'][:].flatten()

    projection_information = ProjectionInformation(
        ncol=prms_params.number_of_columns,
        nrow=prms_params.number_of_rows,
        xllcorner=lower_left_lon,
        yllcorner=lower_left_lat,
        xurcorner=upper_right_lon,
        yurcorner=upper_right_lat,
        cellsize=LEHMAN_CREEK_CELLSIZE
    )

    vegmap = VegetationMapByHRU(
        bare_ground=where(ctv == 0)[0].tolist(),
        grasses=where(ctv == 1)[0].tolist(),
        shrubs=where(ctv == 2)[0].tolist(),
        trees=where(ctv == 3)[0].tolist(),
        conifers=where(ctv == 4)[0].tolist(),

        projection_information=projection_information
    )

    return json.loads(vegmap.to_json())
