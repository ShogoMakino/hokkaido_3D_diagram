#! /usr/bin/python

import numpy as np
import xml.etree.ElementTree as ET
import cv2
import os

class xmlToImage:

    bottom_left = np.array([0, 0, 0, 0])
    top_right = np.array([0, 0, 0, 0])
    xml_size = np.array([750, 1125])
    cells_in_group = np.array([8,8])
    img_elem_size = np.array([xml_size[0] / 15, xml_size[1] / 15])
    group_to_elem = np.array([[cells_in_group[0], 0], [0, cells_in_group[1]], [1, 0], [0, 1]])
    dst_image = False
    img_size = False

    def __init__(self, bottom_left_index, top_right_index):
        self.set_rect(bottom_left_index, top_right_index)
        self.create_image()

    def load_and_put(self, filename):
        gray_image = self.load_xml(filename)
        map_id = self.get_map_id(filename)
        self.put_image(gray_image, map_id)

    def load_and_put_from_filelist(self, filelist):
        i = 0
        for filename in open(filelist, 'r'):
            self.load_and_put(filename[:-1])
            i += 1
            print(i)

    def load_xml(self, filename):
        tuplelist_xpath = './/{http://www.opengis.net/gml/3.2}tupleList'
        startpoint_xpath = './/{http://www.opengis.net/gml/3.2}startPoint'
        return_code = '\n'
        root = ET.parse(filename)
        tuplelist = root.find(tuplelist_xpath)
        startpoint_list = root.find(startpoint_xpath).text.split(' ')
        startpoint_index = int(startpoint_list[1]) * self.xml_size[1] + int(startpoint_list[0])
        int_list = [255 if float(l.split(',')[1]) >= -9000 else 0 for l in tuplelist.text.split('\n') if l != '']
        int_list_offset = np.zeros(self.xml_size.prod())
        int_list_offset[startpoint_index: startpoint_index + len(int_list)] = int_list
        gray_image = np.reshape(int_list_offset, self.xml_size)
        return gray_image

    def create_image(self):
        self.img_size = (np.dot(self.top_right - self.bottom_left, self.group_to_elem) + np.array([1, 1])) * self.img_elem_size
        self.dst_image = np.zeros(self.img_size, np.uint8)

    def get_image(self):
        return self.dst_image

    def set_rect(self, bottom_left_index, top_right_index):
        bottom_left_group = int(bottom_left_index / 100)
        top_right_group = int(top_right_index / 100)
        bottom_left_elem = int(bottom_left_index % 100)
        top_right_elem = int(top_right_index % 100)
        self.bottom_left = np.array([bottom_left_group / 100, bottom_left_group % 100,
                                     bottom_left_elem / 10, bottom_left_elem % 10])
        self.top_right = np.array([top_right_group / 100, top_right_group % 100,
                                   top_right_elem / 10, top_right_elem % 10])

    def get_map_id(self, filename):
        split_filename = filename.split('-')
        map_id = np.array([int(split_filename[2]) / 100, int(split_filename[2]) % 100,
                           int(split_filename[3]) / 10, int(split_filename[3]) % 10])
        return map_id

    def put_image(self, gray_image, map_id):
        relative_map_id = map_id - self.bottom_left
        relative_elem_num = np.dot(relative_map_id, self.group_to_elem)
        roi_left = self.img_elem_size[1] * relative_elem_num[1]
        roi_right = self.img_elem_size[1] * (relative_elem_num[1] + 1)
        roi_bottom = self.img_size[0] - self.img_elem_size[0] * relative_elem_num[0]
        roi_top = self.img_size[0] - self.img_elem_size[0] * (relative_elem_num[0] + 1)
        # print(relative_elem_num)
        # print(map_id)
        # print(roi_left)
        # print(roi_right)
        # print(roi_bottom)
        # print(roi_top)
        self.dst_image[roi_top:roi_bottom, roi_left:roi_right] = cv2.resize(gray_image, tuple(reversed(self.img_elem_size)))


if __name__ == '__main__':
    xml_to_img = xmlToImage(623900, 684877)
    xml_to_img.load_and_put_from_filelist('file_list.txt')
    cv2.imwrite("hokkaido.png", xml_to_img.get_image())
