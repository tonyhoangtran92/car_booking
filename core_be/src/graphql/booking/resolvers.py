from math import cos, asin, sqrt, pi

def resolve_distance(lat1, lon1, lat2, lon2):
    p = pi/180
    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p) * cos(lat2*p) * (1-cos((lon2-lon1)*p))/2
    distance = 12742 * asin(sqrt(a)) #2*R*asin...
    return round(distance * 1000, 2)

