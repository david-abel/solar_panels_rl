# Python imports.
import math as m
import numpy

# Misc. imports.
from pysolar import solar, radiation

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
    Needs to be fixed.
    '''
    sun_alt_radians, sun_az_radians = m.radians(sun_altitude_deg), m.radians(sun_azimuth_deg)
    x = m.sin(sun_alt_radians)
    y = - m.sin(sun_az_radians)
    z = m.cos(m.pi - sun_az_radians)
    
    return _normalize(x, y, z)

def _compute_panel_normal_vector(panel_ns_deg, panel_ew_deg):
    '''
    Needs to be fixed.
    '''
    panel_ns_radians, panel_ew_radians = m.radians(panel_ns_deg), m.radians(panel_ew_deg)

    x = m.sin(panel_ew_radians)
    y = m.sin(panel_ns_radians)
    z = m.cos(panel_ns_radians)*m.cos(panel_ew_radians)

    return _normalize(x, y, z)

def _normalize(x, y, z):
    tot = m.sqrt(x**2 + y**2 + z**2)
    return numpy.array([x / tot, y / tot, z / tot])

def _compute_diffuse_radiation_tilt_factor(panel_ns_deg, panel_ew_deg):
    dave_method = (1 - abs(panel_ns_deg) / 90.0) * (1 - abs(panel_ew_deg) / 90.0)
    masters_method = (m.cos(m.radians(abs(panel_ns_deg))) + m.cos(m.radians(abs(panel_ew_deg)))) / 2.0

    return dave_method

def _compute_reflective_radiation_tilt_factor(panel_ns_deg, panel_ew_deg):
    return (2 - m.cos(m.radians(panel_ns_deg)) - m.cos(m.radians(panel_ew_deg)))

# --- Misc. ---

def _compute_declination(day):
    '''
    Args:
        day (int): Day of the year (1:365)

    Notes:
        Computation from Appendix of:
            Gholam Ali et al, "Estimating solar radiation on tilted surfaces with various orientations: A study case in Karaj (Iran)"
            Theoretical and Applied Climatology, 2006.
    '''
    day_const = 360.0 / 365.0 * (day - 1)
    delta = 180.0 / m.pi * (0.006918 - 0.399912 * m.cos(day_const) + 0.070257 * m.sin(day_const) - 0.006758 * m.cos(2 * day_const) + \
        0.000907 * m.sin(2*day_const) - 0.002697 * m.cos(3 * day_const) + 0.00148 * m.sin(3 * day_const))
    return delta


def _compute_a_b(latitude, panel_az, panel_alt, delta):
    '''
    Args:
        latitude (float)
        panel_az (float): Tilted plane azimuth (radians) (alpha_T)
        panel_alt (float): Tilted plane slope angle (radians) (S)
        delta (float): solar declination
    '''
    if panel_alt == 0.0 or panel_az == 0.0:
        # Division by Zero issues.
        A = 0
        B = 0
    else:
        A = m.cos(latitude) / (m.sin(panel_az) * m.tan(panel_alt)) + m.sin(latitude) / m.tan(panel_az)
        B = m.tan(delta) * (m.cos(latitude) / m.tan(panel_az) - m.sin(latitude) / (m.sin(panel_az) * m.tan(panel_alt)))

    return A, B

def _compute_omega_r_s(omega_s, A, B, panel_az):
    '''
    Args:
        omega_s (float): sunrise hour angle
    '''
    try:
        if panel_az < 0.0:
            omega_rt = - min(omega_s, numpy.arccos((A*B + m.sqrt(A**2 - B**2 + 1)) / (A**2 + 1)))
            omega_st = min(omega_s, numpy.arccos((A*B - m.sqrt(A**2 - B**2 + 1)) / (A**2 + 1)))
        else:
            omega_rt = - min(omega_s, numpy.arccos((A*B - m.sqrt(A**2 - B**2 + 1)) / (A**2 + 1)))
            omega_st = min(omega_s, numpy.arccos((A*B + m.sqrt(A**2 - B**2 + 1)) / (A**2 + 1)))
    except:
        omega_rt, omega_st = -omega_s, omega_s

    return omega_rt, omega_st

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