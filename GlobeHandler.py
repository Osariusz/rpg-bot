import pyvista as pv
from pyvista import examples, read_texture, Plotter
from math import sin, cos, radians

class GlobeHandler():

    def __init__(self, the_map_path: str):
        self.the_map_path = the_map_path
    
    def generate_planet_image(self, coords: list[float], out_file_path: str):
        latitude: float = coords[0]
        longitude: float = coords[1]

        RADIUS: float = 6378.1
        BIG_RADIUS: float = 10000
        mesh = examples.planets.load_venus(radius=RADIUS)
        earth_texture = read_texture(self.the_map_path)
        #x - prawo lewo (longitude) drugi arg
        #y - gora dol (latitude) pierwszy arg
        mesh.rotate_x(angle=-90, inplace=True, transform_all_input_vectors=True)
        mesh.rotate_y(angle=180, inplace=True, transform_all_input_vectors=True)
        mesh.translate((0, 0, 0), inplace=True)
        longitude = -longitude
        was_modified =  False
        if latitude == 90:
            latitude = 89.999999999
            was_modified = True
        p = pv.Plotter(off_screen=True)
        camera_position = [
            (
                BIG_RADIUS*sin(radians(90-latitude))*cos(radians(longitude)), 
                BIG_RADIUS*cos(radians(90-latitude)), 
                BIG_RADIUS*sin(radians(90-latitude))*sin(radians(longitude))
            ), 
            (0, 0, 0),
            (0, 1, 0)
        ]
        
        p.view_yx()
        p.camera_position = camera_position
        p.add_mesh(mesh, texture=earth_texture, lighting=False)
        p.camera.zoom(0.3775)
        p.show(auto_close=False)
        if was_modified:
            latitude = 90
        p.screenshot(out_file_path,transparent_background=True)
        p.close()