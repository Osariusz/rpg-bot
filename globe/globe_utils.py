def normalize_input(coords: list[float]) -> list[float]:
    latitude: float = coords[0]
    longitude: float = coords[1]
    
    latitude = latitude % 360
    longitude = longitude % 360
    if longitude > 180:
        longitude = -360+longitude
    if longitude < -180:
        longitude = 360+longitude
    
    if latitude > 90:
        latitude = 180-latitude
        if longitude < 0:
            longitude = 180 + longitude
        else:
            longitude = longitude - 180

    if latitude < -90:
        latitude = -180-latitude
        if longitude < 0:
            longitude = 180 + longitude
        else:
            longitude = longitude - 180
    return [latitude, longitude]

def coordinates_text(coords: list[float]) -> str:
    return f"{coords[0]}° {coords[1]}°"