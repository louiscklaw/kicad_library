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


#
# This module Create a standard box in various layers including a pin 1 marker tap or chamfer
#
from KicadModTree import *
from KicadModTree.Point import *
from KicadModTree.PolygonPoints import *
from KicadModTree.nodes.Node import Node
from KicadModTree.nodes.base.Line import Line
from KicadModTree.nodes.base.Text import Text


class koaLine:

    def __init__(self, sx, sy, ex, ey, layer, width):
        self.sx = sx
        self.sy = sy
        self.ex = ex
        self.ey = ey
        self.k = 0.0
        self.m = 0.0
        self.l = 0.0
        self.IsVertical = False
        self.layer = layer
        self.width = width

        if ex != sx:
            self.k = (ey - sy) / (ex - sx)
            self.m = sy - (self.k * sx)
        else:
            self.IsVertical = True

        #
        # Get the line lenght
        #
        x1 = min(self.sx, self.ex)
        x2 = max(self.sx, self.ex)
        y1 = min(self.sy, self.ey)
        y2 = max(self.sy, self.ey)

        x1 = x2 - x1
        y1 = y2 - y1

        self.l = sqrt((x1 * x1) + (y1 * y1))


class StandardBox(Node):
    r"""Add a Polygone Line to the render tree

    :param \**kwargs:
        See below

    :Keyword Arguments:
        * *footprint* (``list(Point)``) --
          The foot print
        * *description* (``str``) --
          The description
        * *datasheet* (``str``) --
          The url to the data sheet
        * *at* (``Point``) --
          Where is upper left corner, in cartesian cordinate system (minus y below x axis)
        * *size* (``Point``) --
          The width and height of the rectangle
        * *tags* (``str``) --
          A foot prints tag attribute
        * *SmdTht* (``str``) --
          A foot prints tht/smd attribute
        * *extratexts* (``list(x, y, 'text', layer, sizex, sizey)``) --
          A list of extra txts to be placed on the footprint
        * *pins* (``list(type, number, x, y, sizex, sizey, drill)``) --
          List of tht/smd/npth holes
        * *file3Dname* (``str``) --
          The path to the 3D model name

    :Example:

    #
    # pycodestyle complain over long lines so the complete on is placed in a comment instead
    #
    # StandardBox(footprint=f, description=description, datasheet=datasheet, at=at, size=size, tags=fptag, SmdTht=SmdTht,
    # extratexts=extratexts, pins=pins, file3Dname = "${KISYS3DMOD}/" + dir3D + "/" + footprint_name + ".wrl")))
    #
    >>> from KicadModTree import *
    >>> StandardBox(footprint=f, description=description, ....)
    """

    def __init__(self, **kwargs):
        Node.__init__(self)

        #
        self.virtual_childs = []
        #
        self._initPosition(**kwargs)
        self._initSize(**kwargs)
        self._initFootPrint(**kwargs)
        #
        #
        #
        self._initDesriptionNode(**kwargs)
        self._initTagNode(**kwargs)
        self._initAttributeNode(**kwargs)
        self._initFile3DNameNode(**kwargs)
        self._initExtraTextNode(**kwargs)

        self.extraffablines = kwargs.get('extraffablines')
        self.typeOfBox = str(kwargs.get('typeOfBox'))
        self.pins = kwargs.get('pins')

        #
        # Create foot print parts
        #
        #
        self._createPinsNode()
        self._createFFabLine()
        self._createPin1MarkerLine()
        self._createFSilkSLine()
        self._createFCrtYdLine()
        #

    def getVirtualChilds(self):
        #
        #
        return self.virtual_childs

    def _initPosition(self, **kwargs):
        if not kwargs.get('at'):
            raise KeyError('Upper left position not declared (like "at: [0,0]")')
        self.at = Point2D(kwargs.get('at'))
        self.at.y = 0.0 - self.at.y

    def _initSize(self, **kwargs):
        if not kwargs.get('size'):
            raise KeyError('Size not declared (like "size: [1,1]")')
        if type(kwargs.get('size')) in [int, float]:
            # when the attribute is a simple number, use it for x and y
            self.size = Point2D([kwargs.get('size'), kwargs.get('size')])
        else:
            self.size = Point2D(kwargs.get('size'))

    def _initFootPrint(self, **kwargs):
        if not kwargs.get('footprint'):
            raise KeyError('footprint node is missing')

        self.footprint = kwargs.get('footprint')
        #
        self.footprint_name = self.footprint.name
        #
        self.FFabWidth = 0.10
        self.FSilkSWidth = 0.12
        self.FCrtYdWidth = 0.05
        #
        self.p1m = 3.0
        self.REF_P_w = 1.0
        self.REF_P_h = 1.0
        #
        if self.size.x < 2.0 or self.size.y < 2.0:
            dd = self.size.y / 3.0
            if self.size.x < self.size.y:
                dd = self.size.x / 3.0

            self.p1m = dd
            self.REF_P_w = dd
            self.REF_P_h = self.REF_P_w

        new_node = Text(type='user', text='%R', at=[self.at.x + (self.size.x / 2.0),
                        self.at.y + (self.size.y / 2.0)], layer='F.Fab', size=[self.REF_P_w, self.REF_P_h])
        new_node._parent = self
        self.virtual_childs.append(new_node)
        #
        #
        new_node = Text(type='reference', text='REF**', at=[self.at.x + 2.5, self.at.y - 1.2], layer='F.SilkS')
        new_node._parent = self
        self.virtual_childs.append(new_node)
        #
        #
        new_node = Text(type="value", text=self.footprint_name,
                        at=[self.at.x + (self.size.x / 2.0), self.at.y + self.size.y + 1.0], layer="F.Fab")
        new_node._parent = self
        self.virtual_childs.append(new_node)

    def _initDesriptionNode(self, **kwargs):
        if not kwargs.get('description'):
            raise KeyError('Description not declared (like description: "Bul Holder )')
        if not kwargs.get('datasheet'):
            raise KeyError('datasheet not declared (like datasheet: http://www.bulgin.com/media/bulgin/data/Battery_holders.pdf)')
        self.description = str(kwargs.get('description')) + " (Script generated with StandardBox.py) (" + str(kwargs.get('datasheet')) + ")"
        self.footprint.setDescription(self.description)

    def _initTagNode(self, **kwargs):
        if not kwargs.get('tags'):
            raise KeyError('tags not declared (like "tags: "Bulgin Battery Holder, BX0033, Battery Type 1xPP3")')
        self.tags = str(kwargs.get('tags'))
        self.footprint.setTags(self.tags)

    def _initAttributeNode(self, **kwargs):
        if kwargs.get('smd'):
            self.SmdTht = str(kwargs.get('SmdTht'))
            if SmdTht == "smd":
                self.footprint.setAttribute("smd")

    def _initFile3DNameNode(self, **kwargs):
        if not kwargs.get('file3Dname'):
            raise KeyError('file3Dname not declared')
        self.file3Dname = str(kwargs.get('file3Dname'))
        self.footprint.append(Model(filename=self.file3Dname,
                                    at=[0.0, 0.0, 0.0],
                                    scale=[1.0, 1.0, 1.0],
                                    rotate=[0.0, 0.0, 0.0]))

    def _initExtraTextNode(self, **kwargs):
        if kwargs.get('extratexts'):
            self.extratexts = kwargs.get('extratexts')
            #
            for n in self.extratexts:
                at = [n[0], 0.0-n[1]]
                stss = n[2]
                new_node = Text(type="user", text=stss, at=at)
                #
                if len(n) > 3:
                    new_node.layer = n[3]
                if len(n) > 5:
                    new_node.size = Point2D([n[4], n[5]])
                new_node._parent = self
                self.virtual_childs.append(new_node)

    def _createFFabLine(self):
        ffabline = []
        self.boxffabline = []
        #
        #
        x = self.at.x
        y = self.at.y
        w = self.size.x
        h = self.size.y
        self.boxffabline.append(koaLine(x, y, x + w, y, 'F.Fab', self.FFabWidth))
        self.boxffabline.append(koaLine(x + w, y, x + w, y + h, 'F.Fab', self.FFabWidth))
        self.boxffabline.append(koaLine(x + w, y + h, x, y + h, 'F.Fab', self.FFabWidth))
        self.boxffabline.append(koaLine(x, y + h, x, y, 'F.Fab', self.FFabWidth))
        #
        # Add a chamfer
        #
        dd = 0.5
        if w < 2.0:
            dd = w / 3.0
        if h < 2.0:
            dd = h / 3.0
        #
        x1 = x + dd
        y1 = y + dd
        w1 = w - dd

        ffabline.append(koaLine(x1, y, x1 + w1, y, 'F.Fab', self.FFabWidth))
        ffabline.append(koaLine(x1 + w1, y, x1 + w1, y + h, 'F.Fab', self.FFabWidth))
        ffabline.append(koaLine(x + w, y + h, x, y + h, 'F.Fab', self.FFabWidth))
        ffabline.append(koaLine(x, y + h, x, y1, 'F.Fab', self.FFabWidth))
        ffabline.append(koaLine(x, y1, x1, y, 'F.Fab', self.FFabWidth))
        #
        #
        for n in ffabline:
            new_node = Line(start=Point2D(n.sx, n.sy), end=Point2D(n.ex, n.ey), layer=n.layer, width=n.width)
            if n.width < 0.0:
                new_node = Line(start=Point2D(n.sx, n.sy), end=Point2D(n.ex, n.ey), layer=n.layer)
            new_node._parent = self
            self.virtual_childs.append(new_node)

    def _createPin1MarkerLine(self):
        #
        # Add pin 1 marker line
        #
        x1 = self.at.x - 0.5
        y1 = self.at.y - 0.5
        #
        new_node = Line(start=Point2D(x1, y1 + self.p1m), end=Point2D(x1, y1), layer='F.SilkS', width=self.FSilkSWidth)
        new_node._parent = self
        self.virtual_childs.append(new_node)
        #
        new_node = Line(start=Point2D(x1, y1), end=Point2D(x1 + self.p1m, y1), layer='F.SilkS', width=self.FSilkSWidth)
        new_node._parent = self
        self.virtual_childs.append(new_node)

    def _createFSilkSLine(self):
        self.fsilksline = []
        #
        #
        #
        # Check all holes and pads, if a pad or hole is on the silk line
        # then jump over the pad/hole
        #
        for n in self.boxffabline:
            x1 = min(n.sx, n.ex)
            y1 = min(n.sy, n.ey)
            x2 = max(n.sx, n.ex)
            y2 = max(n.sy, n.ey)
            #
            #
            if (x1 < 0.0 and y1 < 0.0 and y2 < 0.0) or (x1 < 0.0 and y1 > 0.0 and y2 > 0.0):
                #
                # Top and bottom line
                #
                x1_t = x1 - 0.12
                x2_t = x2 + 0.12
                #
                if y1 < 0.0:
                    # Top line
                    y1_t = y1 - 0.12
                    y2_t = y2 - 0.12
                else:
                    # Bottom line
                    y1_t = y1 + 0.12
                    y2_t = y2 + 0.12
                #
                EndLine = True
                while EndLine:
                    px1 = 10000000.0
                    px2 = 10000000.0
                    foundPad = False
                    for n in self.pad:
                        n_min_x = n.at.x - (n.size.x / 2.0)
                        n_min_y = n.at.y - (n.size.y / 2.0)
                        n_max_x = n_min_x + n.size.x
                        n_max_y = n_min_y + n.size.y
                        dd = max(0.25, n.solder_mask_margin)

                        if (n_min_y - 0.25) <= y1_t and (n_max_y + 0.25) > y1_t and n_max_x > x1_t and n_min_x < x2_t:
                            #
                            # This pad is in SilkS line's path
                            #
                            if n_min_x < px1:
                                px1 = n_min_x
                                px2 = n_max_x
                                foundPad = True
                    if foundPad:
                        #
                        # Found at least one pad that is in SilkS's line
                        #
                        if (px1 - 0.25) > x1_t:
                            #
                            # It does not cover the start point
                            #
                            self.fsilksline.append(koaLine(x1_t, y1_t, px1 - 0.25, y2_t, 'F.SilkS', self.FSilkSWidth))
                        x1_t = px2 + 0.25
                    else:
                        #
                        # No pads was in the way
                        #
                        self.fsilksline.append(koaLine(x1_t, y1_t, x2_t, y2_t, 'F.SilkS', self.FSilkSWidth))
                        EndLine = False

                    if x1_t >= x2:
                        EndLine = False

            if (x1 < 0.0 and y1 < 0.0 and y2 > 0.0) or (x1 > 0.0 and y1 < 0.0 and y2 > 0.0):
                #
                # Left and right line
                #
                y1_t = y1 - 0.12
                y2_t = y2 + 0.12
                #
                if x1 < 0.0:
                    # Left line
                    x1_t = min(x1 - 0.12, x2 - 0.12)
                    x2_t = max(x1 - 0.12, x2 - 0.12)
                else:
                    # Right line
                    x1_t = min(x1 + 0.12, x2 + 0.12)
                    x2_t = max(x1 + 0.12, x2 + 0.12)
                #
                EndLine = True
                while EndLine:
                    py1 = 10000000.0
                    py2 = 10000000.0
                    foundPad = False

                    for n in self.pad:
                        n_min_x = n.at.x - (n.size.x / 2.0)
                        n_min_y = n.at.y - (n.size.y / 2.0)
                        n_max_x = n_min_x + n.size.x
                        n_max_y = n_min_y + n.size.y
                        dd = max(0.25, n.solder_mask_margin)

                        if (n_min_x <= x1_t) and (n_max_x > x1_t) and n_max_y > y1_t and n_min_y < y2_t:
                            #
                            # This pad is in SilkS line's path
                            #
                            if n_min_y < py1:
                                py1 = n_min_y
                                py2 = n_max_y
                                foundPad = True
                    if foundPad:
                        #
                        # Found at least one pad that is in SilkS's line
                        #
                        if (py1 - dd) > y1_t:
                            #
                            # It does not cover the start point
                            #
                            self.fsilksline.append(koaLine(x1_t, y1_t, x2_t, py1 - dd, 'F.SilkS', self.FSilkSWidth))
                        y1_t = py2 + dd
                    else:
                        #
                        # No pads was in the way
                        #
                        self.fsilksline.append(koaLine(x1_t, y1_t, x2_t, y2_t, 'F.SilkS', self.FSilkSWidth))
                        EndLine = False

                    if y1_t >= y2:
                        EndLine = False
        #
        #
        for n in self.fsilksline:
            new_node = Line(start=Point2D(n.sx, n.sy), end=Point2D(n.ex, n.ey), layer=n.layer, width=n.width)
            if n.width < 0.0:
                new_node = Line(start=Point2D(n.sx, n.sy), end=Point2D(n.ex, n.ey), layer=n.layer)
            new_node._parent = self
            self.virtual_childs.append(new_node)

    def _createFCrtYdLine(self):
        self.fcrtydline = []
        #
        #
        #
        # Check all holes and pads, if a pad or hole is on the silk line
        # then jump over the pad/hole
        #
        for n in self.boxffabline:
            x1 = min(n.sx, n.ex)
            y1 = min(n.sy, n.ey)
            x2 = max(n.sx, n.ex)
            y2 = max(n.sy, n.ey)
            #
            #
            if (x1 < 0.0 and y1 < 0.0 and y2 < 0.0) or (x1 < 0.0 and y1 > 0.0 and y2 > 0.0):
                #
                # Top and bottom line
                #
                x1_t = x1 - 0.25
                x2_t = x2 + 0.25
                #
                if y1 < 0.0:
                    # Top line
                    y1_t = y1 - 0.25
                    y2_t = y2 - 0.25
                else:
                    # Bottom line
                    y1_t = y1 + 0.25
                    y2_t = y2 + 0.25
                #
                EndLine = True
                while EndLine:
                    px1 = 10000000.0
                    py1 = 10000000.0
                    px2 = 10000000.0
                    py2 = 10000000.0
                    foundPad = False

                    for n in self.pad:
                        n_min_x = n.at.x - (n.size.x / 2.0)
                        n_min_y = n.at.y - (n.size.y / 2.0)
                        n_max_x = n_min_x + n.size.x
                        n_max_y = n_min_y + n.size.y
                        dd = max(0.25, n.solder_mask_margin)

                        if (n_min_y - dd) <= y1_t and (n_max_y + dd) > y1_t and n_max_x > x1_t and n_min_x < x2_t:
                            #
                            # This pad is in SilkS line's path
                            #
                            if n_min_x < px1:
                                px1 = n_min_x
                                py1 = n_min_y
                                px2 = n_max_x
                                py2 = n_max_y
                                foundPad = True
                    if foundPad:
                        #
                        # Found at least one pad that is in SilkS's line
                        #
                        if (px1 - dd) > x1_t:
                            #
                            # It does not cover the start point
                            #
                            self.fsilksline.append(koaLine(x1_t, y1_t, px1 - dd, y2_t, 'F.CrtYd', self.FSilkSWidth))
                            if y1 < 0.0:
                                # Top line
                                self.fsilksline.append(koaLine(px1 - dd, y2_t, px1 - dd, py1 - dd,
                                                               'F.CrtYd', self.FSilkSWidth))
                                self.fsilksline.append(koaLine(px1 - dd, py1 - dd, px2 + dd, py1 - dd,
                                                               'F.CrtYd', self.FSilkSWidth))
                                self.fsilksline.append(koaLine(px2 + dd, py1 - dd, px2 + dd, y2_t,
                                                               'F.CrtYd', self.FSilkSWidth))
                            else:
                                # Bottom line
                                self.fsilksline.append(koaLine(px1 - dd, y2_t, px1 - dd, py2 + dd,
                                                               'F.CrtYd', self.FSilkSWidth))
                                self.fsilksline.append(koaLine(px1 - dd, py2 + dd, px2 + dd, py2 + dd,
                                                               'F.CrtYd', self.FSilkSWidth))
                                self.fsilksline.append(koaLine(px2 + dd, py2 + dd, px2 + dd, y2_t,
                                                               'F.CrtYd', self.FSilkSWidth))
                        x1_t = px2 + dd
                    else:
                        #
                        # No pads was in the way
                        #
                        self.fsilksline.append(koaLine(x1_t, y1_t, x2_t, y2_t, 'F.CrtYd', self.FSilkSWidth))
                        EndLine = False

                    if x1_t >= x2:
                        EndLine = False

            if (x1 < 0.0 and y1 < 0.0 and y2 > 0.0) or (x1 > 0.0 and y1 < 0.0 and y2 > 0.0):
                #
                # Left and right line
                #
                y1_t = y1 - 0.25
                y2_t = y2 + 0.25
                #
                if x1 < 0.0:
                    # Left line
                    x1_t = x1 - 0.25
                    x2_t = x1 - 0.25
                else:
                    # Right line
                    x1_t = x1 + 0.25
                    x2_t = x2 + 0.25
                #
                EndLine = True
                while EndLine:
                    px1 = 10000000.0
                    py1 = 10000000.0
                    px2 = 10000000.0
                    py2 = 10000000.0
                    foundPad = False

                    for n in self.pad:
                        n_min_x = n.at.x - (n.size.x / 2.0)
                        n_min_y = n.at.y - (n.size.y / 2.0)
                        n_max_x = n_min_x + n.size.x
                        n_max_y = n_min_y + n.size.y
                        dd = max(0.25, n.solder_mask_margin)

                        if (n_min_x <= x1_t) and (n_max_x > x1_t) and n_max_y > y1_t and n_min_y < y2_t:
                            #
                            # This pad is in SilkS line's path
                            #
                            if n_min_y < py1:
                                px1 = n_min_x
                                py1 = n_min_y
                                px2 = n_max_x
                                py2 = n_max_y
                                foundPad = True
                    if foundPad:
                        #
                        # Found at least one pad that is in SilkS's line
                        #
                        if (py1 - dd) > y1_t:
                            #
                            # It does not cover the start point
                            #
                            self.fsilksline.append(koaLine(x1_t, y1_t, x2_t, py1 - dd, 'F.CrtYd', self.FSilkSWidth))
                            if x1 < 0.0:
                                # Left line
                                self.fsilksline.append(koaLine(x2_t, py1 - dd, px1 - dd, py1 - dd,
                                                               'F.CrtYd', self.FSilkSWidth))
                                self.fsilksline.append(koaLine(px1 - dd, py1 - dd, px1 - dd, py2 + dd,
                                                               'F.CrtYd', self.FSilkSWidth))
                                self.fsilksline.append(koaLine(px1 - dd, py2 + dd, x2_t, py2 + dd,
                                                               'F.CrtYd', self.FSilkSWidth))
                            else:
                                # Right line
                                self.fsilksline.append(koaLine(x2_t, py1 - dd, px2 + dd, py1 - dd,
                                                               'F.CrtYd', self.FSilkSWidth))
                                self.fsilksline.append(koaLine(px2 + dd, py1 - dd, px2 + dd, py2 + dd,
                                                               'F.CrtYd', self.FSilkSWidth))
                                self.fsilksline.append(koaLine(px2 + dd, py2 + dd, x2_t, py2 + dd,
                                                               'F.CrtYd', self.FSilkSWidth))

                        y1_t = py2 + dd
                    else:
                        #
                        # No pads was in the way
                        #
                        self.fsilksline.append(koaLine(x1_t, y1_t, x2_t, y2_t, 'F.CrtYd', self.FSilkSWidth))
                        EndLine = False

                    if y1_t >= y2:
                        EndLine = False
        #
        #
        for n in self.fsilksline:
            new_node = Line(start=Point2D(n.sx, n.sy), end=Point2D(n.ex, n.ey), layer=n.layer, width=n.width)
            if n.width < 0.0:
                new_node = Line(start=Point2D(n.sx, n.sy), end=Point2D(n.ex, n.ey), layer=n.layer)
            new_node._parent = self
            self.virtual_childs.append(new_node)

    def calculateBoundingBox(self):
        min_x = self.at.x
        min_y = self.at.y
        max_x = min_x + self.size.x
        max_y = min_y + self.size.y

        for child in self.virtual_childs():
            child_outline = child.calculateBoundingBox()

            min_x = min([min_x, child_outline['min']['x']])
            min_y = min([min_y, child_outline['min']['y']])
            max_x = max([max_x, child_outline['max']['x']])
            max_y = max([max_y, child_outline['max']['y']])

        return {'min': Point2D(min_x, min_y), 'max': Point2D(max_x, max_y)}

    def _createPinsNode(self):
        #
        # Add pin and holes
        #
        self.pad = []

        c = 1
        for n in self.pins:
            c = n[1]
            x = n[2]
            y = n[3]
            sx = n[4]
            sy = n[5]
            dh = n[6]
            if n[0] == 'tht':
                if c == '1':
                    new_pad = Pad(number=c, type=Pad.TYPE_THT, shape=Pad.SHAPE_RECT,
                                  at=[x, 0.0 - y], size=[sx, sy], drill=dh, layers=['*.Cu', '*.Mask'])
                    self.footprint.append(new_pad)
                    self.pad.append(new_pad)
                else:
                    new_pad = Pad(number=c, type=Pad.TYPE_THT, shape=Pad.SHAPE_CIRCLE,
                                  at=[x, 0.0 - y], size=[sx, sy], drill=dh, layers=['*.Cu', '*.Mask'])
                    self.footprint.append(new_pad)
                    self.pad.append(new_pad)
            elif n[0] == 'smd':
                    new_pad = Pad(number=c, type=Pad.TYPE_SMT, shape=Pad.SHAPE_RECT,
                                  at=[x, 0.0 - y], size=[sx, sy], drill=dh, layers=['F.Cu', 'F.Paste', 'F.Mask'])
                    self.footprint.append(new_pad)
                    self.pad.append(new_pad)
            elif n[0] == 'npth':
                    if sy == 0:
                        new_pad = Pad(type=Pad.TYPE_NPTH, shape=Pad.SHAPE_CIRCLE,
                                      at=[x, 0.0 - y], size=[sx, sx], drill=dh, layers=['*.Cu', '*.Mask'])
                        self.footprint.append(new_pad)
                        self.pad.append(new_pad)
                    else:
                        new_pad = Pad(type=Pad.TYPE_NPTH, shape=Pad.SHAPE_RECT,
                                      at=[x, 0.0 - y], size=[sx, sy], drill=dh, layers=['*.Cu', '*.Mask'])
                        self.footprint.append(new_pad)
                        self.pad.append(new_pad)
            #
