#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vispy: gallery 2
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Multiple real-time digital signals with GLSL-based clipping.
"""

from vispy import gloo
from vispy import app
from vispy.color import Colormap
import numpy as np
import math


num_bins = 128
num_lines = 16


VERT_SHADER = """
#version 120


//attribute vec2 a_position;

attribute float index;
attribute float line;
//uniform float line;

uniform sampler2D heightmap;
uniform float map_offset;

uniform float num_bins;
uniform float num_lines;

varying float height;
varying float v_line;

void main() {
    // Compute the x coordinate from the time index.
    //float x = -1 + 2*a_index.z / (u_n-1);

    //vec2 position = vec2(x - (1 - 1), a_position + index / u_n);

    float y = line / num_lines - 1.0;
    float x = index / num_bins - 1.0 ;//+ y / 2;

    float u = index / num_bins;
    float v = mod(line + map_offset, num_lines) / num_lines;

    height = texture2D(heightmap, vec2(u, v)).x;

    gl_Position = vec4(x, y + height, 0.0, 1.0);
    v_line = line;
}
"""

FRAG_SHADER = """
#version 120

varying float height;
varying float v_line;

uniform sampler1D colormap;

void main() {
    gl_FragColor = texture1D(colormap, height);

    if (fract(v_line) > 0.) {
        discard;
    }

    // Discard the fragments between the signals (emulate glMultiDrawArrays).
    //if ((fract(v_index.x) > 0.) || (fract(v_index.y) > 0.))
    //    discard;
}
"""


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, title='Use your wheel to zoom!',
                            keys='interactive')
        self.program = gloo.Program(VERT_SHADER, FRAG_SHADER)
        self.program['index'] = [(x,) for x in range(num_bins)] * num_lines
        self.program['line'] = [(x,) * num_bins for x in range(num_lines)]
        self.program['map_offset'] = 0

        self.program['num_bins'] = num_bins
        self.program['num_lines'] = num_lines

        self.program['heightmap'] = np.random.random(size=(num_lines, num_bins)).astype('float32')
        #print (dir(self.program['heightmap']))
        self.program['heightmap'].interpolation = 'nearest'#'nearest'

        self.program['colormap'] = Colormap(['r', 'g', 'b']).map(np.linspace(0, 1, 64)).astype('float32')

        gloo.set_viewport(0, 0, *self.physical_size)

        gloo.set_state(clear_color='black', blend=True,
                       blend_func=('src_alpha', 'one_minus_src_alpha'))

        self.show()

    def on_resize(self, event):
        gloo.set_viewport(0, 0, *event.physical_size)

    def on_mouse_wheel(self, event):
        dx = np.sign(event.delta[1]) * .05
        self.update()

    def add_new_line(self, data):
        map_offset = self.program['map_offset']
        self.program['map_offset'] = (map_offset - 1) % num_lines
        map_offset = int(self.program['map_offset'])

        data = data.astype('float32')
        data = data[:128]
        print 'add_new_line', len(data), map_offset, data[::16]

        #data = np.random.random(num_bins).astype('float32')
        self.program['heightmap'].set_data([data], (map_offset, 0))
        self.update()

    def on_draw(self, event):
        gloo.clear()

        #self.program['a_position'] = 

        #for line in range(num_lines):
        #    self.program['line'] = line
        self.program.draw('line_strip')


if __name__ == '__main__':
    c = Canvas()
    app.run()
