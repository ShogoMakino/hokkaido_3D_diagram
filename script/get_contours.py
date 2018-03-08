#! /usr/bin/python

import cv2
import numpy as np
import copy
import sqlite3

class Contours:
    bottom_left = np.array([0, 0])
    top_right = np.array([0, 0])
    imgsize = np.array([0, 0])
    image = None

    def __init__(self, image_filename, db_filename):
        self.db = sqlite3.connect(db_filename)
        self.cursor = self.db.cursor()
        self.load_image(image_filename)

    def run(self):
        contours = self.get_contours(self.image)
        for contour in contours:
            converted_contour = [self.convert_px_to_geometory(l) for l in contour]
            self.add_contour_to_db(converted_contour)

    def load_image(self, filename):
        self.image = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
        self.imgsize = np.array(self.image.shape)

    def get_contours(self, image):
        src_img = copy.copy(image)
        contours, hierarchy = cv2.findContours(src_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return [[l[0][::-1] for l in m] for m in contours]

    def convert_px_to_geometory(self, px_point):
        return self.top_left + (self.bottom_right - self.top_left) * (np.array(px_point) + np.array([0.5, 0.5])) / self.imgsize

    def add_contour_to_db(self, contour, index = -1):
        if index == -1:
            self.cursor.execute('SELECT DISTINCT contour_id FROM contours_points')
            index_list = [int(l[0]) for l in self.cursor.fetchall()]
            insert_index = 0
            while True:
                if insert_index in index_list:
                    insert_index += 1
                else:
                    break
        else:
            insert_index = index
        insert_data = [(insert_index, i, point[0], point[1]) for i, point in enumerate(contour)]
        self.cursor.executemany('INSERT INTO contours_points VALUES (?, ?, ?, ?)', insert_data)
        self.db.commit()

    def make_table_if_not_exist(self, table_name):
        self.cursor.execute('CREATE TABLES contours_points(contour_id, point_id, latitude, longitude)')
        self.cursor.commit()

if __name__ == '__main__':
    contours = Contours("hokkaido.png", "../db/contour.sqlite3")
    contours.top_left = np.array([46, 139])
    contours.bottom_right = np.array([41.333333333, 146])
    contours.run()
    contours.db.close()
