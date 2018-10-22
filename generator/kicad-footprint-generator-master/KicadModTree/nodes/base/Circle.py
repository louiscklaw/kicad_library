# KicadModTree is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# KicadModTree is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with kicad-footprint-generator. If not, see < http://www.gnu.org/licenses/ >.
#
# (C) 2016 by Thomas Pointhuber, <thomas.pointhuber@gmx.at>

from KicadModTree.Vector import *
from KicadModTree.nodes.Node import Node


class Circle(Node):
    r"""Add a Circle to the render tree

    :param \**kwargs:
        See below

    :Keyword Arguments:
        * *center* (``Vector2D``) --
          center of the circle
        * *radius* (``float``) --
          radius of the circle
        * *layer* (``str``) --
          layer on which the circle is drawn (default: 'F.SilkS')
        * *width* (``float``) --
          width of the circle line (default: None, which means auto detection)

    :Example:

    >>> from KicadModTree import *
    >>> Circle(center=[0, 0], radius=1.5, layer='F.SilkS')
    """

    def __init__(self, **kwargs):
        Node.__init__(self)
        self.center_pos = Vector2D(kwargs['center'])
        self.radius = kwargs['radius']

        self.end_pos = Vector2D([self.center_pos.x+self.radius, self.center_pos.y])

        self.layer = kwargs.get('layer', 'F.SilkS')
        self.width = kwargs.get('width')

    def calculateBoundingBox(self):
        min_x = self.center_pos.x-self.radius
        min_y = self.center_pos.y-self.radius
        max_x = self.center_pos.x+self.radius
        max_y = self.center_pos.y+self.radius

        return Node.calculateBoundingBox({'min': ParseXY(min_x, min_y), 'max': ParseXY(max_x, max_y)})

    def _getRenderTreeText(self):
        render_strings = ['fp_circle']
        render_strings.append(self.center_pos.render('(center {x} {y})'))
        render_strings.append(self.end_pos.render('(end {x} {y})'))
        render_strings.append('(layer {layer})'.format(layer=self.layer))
        render_strings.append('(width {width})'.format(width=self.width))

        render_text = Node._getRenderTreeText(self)
        render_text += ' ({})'.format(' '.join(render_strings))

        return render_text
