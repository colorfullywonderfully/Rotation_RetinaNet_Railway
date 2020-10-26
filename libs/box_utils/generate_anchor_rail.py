# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 14:34:37 2020

@author: YUNPENGW
"""

# --------------------------------------------------------
# Faster R-CNN
# Copyright (c) 2015 Microsoft
# Licensed under The MIT License [see LICENSE for details]
# Written by Ross Girshick and Sean Bell
# --------------------------------------------------------
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np


# Verify that we compute the same anchors as Shaoqing's matlab implementation:
#
#    >> load output/rpn_cachedir/faster_rcnn_VOC2007_ZF_stage1_rpn/anchors.mat
#    >> anchors
#
#    anchors =
#
#       -83   -39   100    56
#      -175   -87   192   104
#      -359  -183   376   200
#       -55   -55    72    72
#      -119  -119   136   136
#      -247  -247   264   264
#       -35   -79    52    96
#       -79  -167    96   184
#      -167  -343   184   360

# array([[ -83.,  -39.,  100.,   56.],
#       [-175.,  -87.,  192.,  104.],
#       [-359., -183.,  376.,  200.],
#       [ -55.,  -55.,   72.,   72.],
#       [-119., -119.,  136.,  136.],
#       [-247., -247.,  264.,  264.],
#       [ -35.,  -79.,   52.,   96.],
#       [ -79., -167.,   96.,  184.],
#       [-167., -343.,  184.,  360.]])

def gereate_centering_anchor(
        base_size=16, ratios=[0.5, 1, 2],
        scales=2 ** np.arange(3, 6)):

    """
    Generate anchor (reference) windows by enumerating aspect ratios X
    scales wrt a reference (0, 0, 15, 15) window.
    """
    base_anchor = np.array([1, 1, base_size, base_size]) - (base_size // 2)
    ratio_anchors = _ratio_enum(base_anchor, ratios)
    anchors = np.vstack([_scale_enum(ratio_anchors[i, :], scales)
                         for i in range(ratio_anchors.shape[0])])
    return anchors.astype(np.float32)

def generate_anchors(base_size=16, ratios=[0.5, 1, 2],
                     scales=2 ** np.arange(3, 6)):
    """
    Generate anchor (reference) windows by enumerating aspect ratios X
    scales wrt a reference (0, 0, 15, 15) window.
    """

    base_anchor = np.array([1, 1, 4, base_size]) - 1
    ratio_anchors = _ratio_enum(base_anchor, ratios)
    anchors = np.vstack([_scale_enum(ratio_anchors[i, :], scales)
                         for i in range(ratio_anchors.shape[0])])
    return anchors.astype(np.float32)


def _whctrs(anchor):
    """
    Return width, height, x center, and y center for an anchor (window).
    """

    w = anchor[2] - anchor[0] + 1  #4       0 0 3 3
    h = anchor[3] - anchor[1] + 1  #4
    x_ctr = anchor[0] + 0.5 * (w - 1)   #1.5
    y_ctr = anchor[1] + 0.5 * (h - 1)   #1.5
    return w, h, x_ctr, y_ctr


def _mkanchors(ws, hs, x_ctr, y_ctr):
    """
    Given a vector of widths (ws) and heights (hs) around a center
    (x_ctr, y_ctr), output a set of anchors (windows).
    """

    ws = ws[:, np.newaxis]
    hs = hs[:, np.newaxis]
    anchors = np.hstack((x_ctr - 0.5 * (ws - 1),
                         y_ctr - 0.5 * (hs - 1),
                         x_ctr + 0.5 * (ws - 1),
                         y_ctr + 0.5 * (hs - 1)))
    return anchors


def _ratio_enum(anchor, ratios):
    """
    Enumerate a set of anchors for each aspect ratio wrt an anchor.
    """

    w, h, x_ctr, y_ctr = _whctrs(anchor)
    #size = w * h
    #size_ratios = size / ratios
    ws = np.round(w * ratios)  #np.round(np.sqrt(size_ratios)) np.sqrt(size_ratios)
    hs = np.round(ws*h/ws) # np.round(ws * ratios)    
    anchors = _mkanchors(ws, hs, x_ctr, y_ctr)
    return anchors


def _scale_enum(anchor, scales):
    """
    Enumerate a set of anchors for each scale wrt an anchor.
    """

    w, h, x_ctr, y_ctr = _whctrs(anchor)
    ws = w * scales
    hs = h * scales  # h * scales
    anchors = _mkanchors(ws, hs, x_ctr, y_ctr)
    return anchors


def generate_anchors_pre(height, width, feat_stride, anchor_scales=(8, 16, 32),
                         anchor_ratios=(0.5, 1, 2), base_size=16):
    """ A wrapper function to generate anchors given different scales
      Also return the number of anchors in variable 'length'
    """
    anchors = generate_anchors(
        base_size=base_size, ratios=np.array(anchor_ratios),
        scales=np.array(anchor_scales))
    A = anchors.shape[0]
    shift_x = np.arange(0, width) * feat_stride
    shift_y = np.arange(0, height) * feat_stride #
    shift_x, shift_y = np.meshgrid(shift_x, shift_y)
    shifts = np.vstack((shift_x.ravel(), shift_y.ravel(), shift_x.ravel(),
                        shift_y.ravel())).transpose()
    K = shifts.shape[0]
    #print(shifts[0:100])
    # width changes faster, so here it is H, W, C
    #print('12123',anchors.reshape((1, A, 4)))
    v = shifts.reshape((1, K, 4)).transpose((1, 0, 2))
    b = anchors.reshape((1, A, 4)) 
   # print('fgdfg',v.shape)
    #print('gfgfg',b.shape)
    anchors = anchors.reshape((1, A, 4)) + shifts.reshape((1, K, 4)).transpose(
        (1, 0, 2))
    #print('1232131',anchors)
    anchors = anchors.reshape((K * A, 4)).astype(np.float32, copy=False)
    #print('32132',anchors[11000:11100])
    return anchors


if __name__ == '__main__':
    anchors = generate_anchors_pre(64, 64, 8, anchor_scales=np.array([2 ** 0, 2 ** (1.0 / 3.0), 2 ** (2.0 / 3.0)]) * 8,
                                   anchor_ratios=(0.5,1.0,2.0), base_size=64)
    #print(anchors[:10])
   # print(2 ** (1.0 / 3.0))
    x_c = (anchors[:, 2] - anchors[:, 0]) / 2
    y_c = (anchors[:, 3] - anchors[:, 1]) / 2
    h = anchors[:, 2] - anchors[:, 0] + 1
    w = anchors[:, 3] - anchors[:, 1] + 1
    theta = -90 * np.ones_like(x_c)
    anchors = np.stack([x_c, y_c]).transpose()
    print(anchors)