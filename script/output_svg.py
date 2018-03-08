#! /usr/bin/python

import svgwrite
import sqlite3
import numpy as np

class outputSVG:

    def __init__(self, db_filename, svg_filename):
        self.dwg = svgwrite.Drawing(svg_filename)
        self.db = sqlite3.connect(db_filename)
        self.cursor = self.db.cursor()


    def run(self, select = None):
        self.cursor.execute('SELECT DISTINCT contour_id FROM contours_points')
        contour_id_list = [int(l[0]) for l in self.cursor.fetchall()]
        for contour_id in contour_id_list:
            if select is None or contour_id in select:
                points = self.get_points(contour_id)
                converted_points = [self.convert_points(l) for l in points]
                self.draw_path(converted_points)
        self.dwg.save()

    def draw_path(self, points, loop = True):
        d = [(['M'] if i == 0 else ['L']) + list(l[::-1]) for i, l in enumerate(points)]
        if loop:
            d.append('z')

        self.dwg.add(self.dwg.path(d, stroke = 'black', fill = 'none'))

    def get_points(self, contour_id):
        self.cursor.execute('SELECT latitude, longitude FROM contours_points WHERE contour_id = ?', (contour_id, ))
        return [(l[0], l[1]) for l in self.cursor.fetchall()]

    def convert_points(self, point, convert_method = None):
        return (np.array(point) - np.array([46, 139])) * np.array([-100, 100])


if __name__ == '__main__':
    output_svg = outputSVG('../db/contour.sqlite3', 'hokkaido.svg')
    output_svg.run(select=[135])
    output_svg.db.close()
