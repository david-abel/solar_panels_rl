# Python imports.
import math as m
import numpy

# Misc. imports.
from Pysolar import solar, radiation

def _compute_sun_altitude(latitude_deg, longitude_deg, time):
    return solar.GetAltitude(latitude_deg, longitude_deg, time)

def _compute_sun_azimuth(latitude_deg, longitude_deg, time):
    return solar.GetAzimuth(latitude_deg, longitude_deg, time)

# --- Radiation hitting the surface of the Earth ---

def _compute_radiation_direct(time, sun_altitude_deg):
    return _get_radiation_direct(time, sun_altitude_deg)

def _compute_radiation_diffuse(time, day, sun_altitude_deg):
    sky_diffus = _compute_sky_diffusion(day)
    return sky_diffus * _compute_radiation_direct(time, sun_altitude_deg)

def _compute_radiation_reflective(time, day, reflective_index, sun_altitude_deg):
    sky_diffus = _compute_sky_diffusion(day)
    rad_direct = _compute_radiation_direct(time, sun_altitude_deg)
    return reflective_index * rad_direct * (m.sin(m.radians(sun_altitude_deg)) + sky_diffus)
    
def _compute_sky_diffusion(day):
    return 0.095 * m.sin(0.99*day - 99)

# MAIN TODO: compute cloud effects.
def _compute_direct_cloud_cover(clouds, sun_x, sun_y, img_dims):
    sun_dim = img_dims / 8.0

    total = 0.0
    for cloud in clouds:
        euc_dist = m.sqrt((sun_x - cloud.x)**2 + (sun_y - cloud.y)**2)

        # if euc_dist <= m.sqrt(cloud.rx**2 + cloud.ry**2):
            # print "overlap:", cloud.x, cloud.y, sun_x, sun_y, cloud.rx, cloud.ry, "amount:", m.sqrt(cloud.rx**2 + cloud.ry**2) - euc_dist
        # else:
            # print "NONE", cloud.x, cloud.y, sun_x, sun_y, cloud.rx, cloud.ry

    return total / 1000.0

    

# --- Tilt Factors ---

def _compute_direct_radiation_tilt_factor(panel_ns_deg, panel_ew_deg, sun_altitude_deg, sun_azimuth_deg):
    '''
    Args:
        panel_ns_deg (float): in the range [-90, 90], 0 is facing up.
        panel_ew_deg (float): in the range [-90, 90], 0 is facing up.

    Summary:
        Per the model of:

    '''
    sun_vector = _compute_sun_vector(sun_altitude_deg, sun_azimuth_deg)
    panel_normal = _compute_panel_normal_vector(panel_ns_deg, panel_ew_deg)

    cos_diff = numpy.dot(sun_vector, panel_normal)

    return abs(cos_diff)

def _compute_sun_vector(sun_altitude_deg, sun_azimuth_deg):
    '''
    Args:
        sun_altitude_deg (float)
        sun_azimuth_deg (float)

    Notes:
        We assume x+ is North, x- is South, y+ is E, y- is South, z+ is up, z- is down.
    '''

    sun_alt_radians, sun_az_radians = m.radians(sun_altitude_deg), m.radians(sun_azimuth_deg)
    x = m.sin(m.pi - sun_az_radians) * m.cos(sun_alt_radians)
    y = m.cos(m.pi - sun_az_radians) * m.cos(sun_alt_radians)
    z = m.sin(sun_alt_radians)
    
    return _normalize(x, y, z)

def _compute_panel_normal_vector(panel_ns_deg, panel_ew_deg):
    panel_ns_radians, panel_ew_radians = m.radians(panel_ns_deg), m.radians(panel_ew_deg)

    # Compute panel normal.
    x = m.sin(panel_ns_radians)*m.cos(panel_ew_radians)
    y = m.sin(panel_ew_radians)*m.cos(panel_ns_radians)
    z = m.cos(panel_ns_radians)*m.cos(panel_ew_radians)

    return _normalize(x, y, z)

def _normalize(x, y, z):
    tot = m.sqrt(x**2 + y**2 + z**2)
    return numpy.array([x / tot, y / tot, z / tot])

def _compute_diffuse_radiation_tilt_factor(panel_ns_deg, panel_ew_deg):
    '''
    Args:
        panel_ns_deg (float)
        panel_ew_deg (float)

    Returns:
        (float): The diffuse radiation tilt factor.
    '''
    ns_radians = m.radians(abs(panel_ns_deg))
    ew_radians = m.radians(abs(panel_ew_deg))
    diffuse_radiation_angle_factor = (m.cos(ns_radians) + m.cos(ew_radians)) / 2.0

    return diffuse_radiation_angle_factor

def _compute_reflective_radiation_tilt_factor(panel_ns_deg, panel_ew_deg):
    return (2 - m.cos(m.radians(panel_ns_deg)) - m.cos(m.radians(panel_ew_deg))) / 2.0

# --- Misc. ---

# DIRECTLY FROM PYSOLAR (with different conditional)
def _get_radiation_direct(utc_datetime, sun_altitude_deg):
    # from Masters, p. 412
    if 0 < sun_altitude_deg < 180:
        day = solar.GetDayOfYear(utc_datetime)
        flux = radiation.GetApparentExtraterrestrialFlux(day)
        optical_depth = radiation.GetOpticalDepth(day)
        air_mass_ratio = radiation.GetAirMassRatio(sun_altitude_deg)
        return flux * m.exp(-1 * optical_depth * air_mass_ratio)
    else:
        return 0.0