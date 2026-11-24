import networkx as nx
import math

band_min=25.0
band_max=100.0
jitter_max=4.0
jitter_min=1.0
loss_max=1.5
loss_min=0.05

def clamp(val,min_val,max_val):
    return max(min_val, min(max_val,val))
    
def degToRad(deg):
    pi = math.pi
    return deg * pi / 180

"""
    input: (lat, long, alt)
    output: (x, y, z)
    algorithm borrowed from StarPerf's MATLAB codes; conversion of coordinate systems
"""
def lla2cbf(position):
    R = 6371 * (10 ** 3)
    pi = math.pi
    r = R + position[2]
    theta = pi / 2 - position[0] * pi / 180
    phi = 2 * pi + position[1] * pi / 180
    x = (r * math.sin(theta)) * math.cos(phi)
    y = (r * math.sin(theta)) * math.sin(phi)
    z = r * math.cos(theta)
    return (x, y, z)

"""
    get the ground converage limit L of a celestial object
    see README.md for more details
"""
def getCoverageLimitL(elevation, depression, altitude):
    R = 6378 * 10 ** 3
    gamma = 90 - (elevation + depression)
    l = R * math.sin(degToRad(gamma))
    theta = (180 - gamma) / 2
    d = l / (math.tan(degToRad(theta)))
    L = math.sqrt((altitude + d) ** 2 + l ** 2)
    return L

'''
    given coordinates of a satellite, a ground station, and coverage limit L, check 
    if the satellite can cover the ground station
'''
def checkSatCoverGroundStation(sat_position_cbf, gs_position_cbf, L):
    x1, y1, z1 = sat_position_cbf
    x2, y2, z2 = gs_position_cbf
    dist = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)
    return dist <= L

'''
    compute (electromagnetic) wave's propogation latency between two points in vacuum
'''
def computeLatency(point_a_cbf, point_b_cbf):
    dist = math.sqrt((point_a_cbf[0] - point_b_cbf[0])**2 + (point_a_cbf[1] - point_b_cbf[1])**2 + (point_a_cbf[2] - point_b_cbf[2])**2)
    return dist / (3 * 10**8)

'''
    given a source, destination, and the graph, check whether an e2e path exists
'''
def pathExists(gw1, gw2, G):
    if gw1 == -1 or gw2 == -1:
        return False
    return nx.has_path(G, gw1, gw2)
'''
    compute the elevation angles
'''
def elangle(gs_cbf,sat_cbf):
    dx=sat_cbf[0]-gs_cbf[0]
    dy=sat_cbf[1]- gs_cbf[1]
    dz=sat_cbf[2]-gs_cbf[2]
    dist=math.sqrt(math.pow(dx,2)+math.pow(dy,2)+math.pow(dz,2))
    ground_dist=math.sqrt(math.pow(gs_cbf[0],2)+math.pow(gs_cbf[1],2)+math.pow(gs_cbf[2],2))
    sen_teta=(dx*gs_cbf[0]+ dy*gs_cbf[1]+dz*gs_cbf[2])/(dist*ground_dist)
    angle_deg=math.asin(clamp(sen_teta,-1.0,1.0))*(180/math.pi)
    return angle_deg
def normalization(angle_deg,angle_min):
    if angle_min==90.0 : angle_min=0.5
    angle_max=1.0
    angle_norm=clamp((angle_deg-angle_min)/(90-angle_min),0,1)
    return angle_norm
def channel_paragrams(angle_norm,is_handover=False):
    btw_Mbps=band_min+((band_max-band_min)*angle_norm)
    jitter_miss=jitter_max+((jitter_min-jitter_max)*angle_norm)
    loss_pct=loss_max+((loss_min-loss_max)*angle_norm)
    if is_handover:
        jitter_miss+=3.0
        loss_pct=min(100.0, loss_pct+5.0)
    return round(btw_Mbps, 2), round(jitter_miss, 2), round(loss_pct, 3)






