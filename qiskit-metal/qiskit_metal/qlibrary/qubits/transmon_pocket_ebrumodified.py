# -*- coding: utf-8 -*-

# This code is part of Qiskit.
#
# (C) Copyright IBM 2017, 2021.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.
"""Transmon Pocket.

.. code-block::
     ________________________________
    |______ ____           __________|
    |      |____|         |____|     |
    |        __________________      |
    |       |                  |     |
    |       |__________________|     |
    |                 |              |
    |                 x              |
    |        _________|________      |
    |       |                  |     |
    |       |__________________|     |
    |        ______                  |
    |_______|______|                 |
    |________________________________|
"""

import numpy as np
from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.core import BaseQubit


class TransmonPocket(BaseQubit):
    """The base `TransmonPocket` class.

    Inherits `BaseQubit` class.

    Create a standard pocket transmon qubit for a ground plane,
    with two pads connected by a junction (see drawing below).

    Connector lines can be added using the `connection_pads`
    dictionary. Each connector pad has a name and a list of default
    properties.

    Sketch:
        Below is a sketch of the qubit
        ::

                 +1                            +1
                ________________________________
            -1  |______ ____           __________|   +1     Y
                |      |____|         |____|     |          ^
                |        __________________      |          |
                |       |     island       |     |          |----->  X
                |       |__________________|     |
                |                 |              |
                |  pocket         x              |
                |        _________|________      |
                |       |                  |     |
                |       |__________________|     |
                |        ______                  |
                |_______|______|                 |
            -1  |________________________________|   +1
                 
                 -1                            -1

    .. image::
        transmon_pocket.png

    .. meta::
        Transmon Pocket

    BaseQubit Default Options:
        * connection_pads: Empty Dict -- The dictionary which contains all active connection lines for the qubit.
        * _default_connection_pads: Empty Dict -- The default values for the (if any) connection lines of the qubit.

    Default Options:
        * pad_gap: '30um' -- The distance between the two charge islands, which is also the resulting 'length' of the pseudo junction
        * inductor_width: '20um' -- Width of the pseudo junction between the two charge islands (if in doubt, make the same as pad_gap). Really just for simulating in HFSS / other EM software
        * pad_width: '455um' -- The width (x-axis) of the charge island pads
        * pad_height: '90um' -- The size (y-axis) of the charge island pads
        * pocket_width: '650um' -- Size of the pocket (cut out in ground) along x-axis
        * pocket_height: '650um' -- Size of the pocket (cut out in ground) along y-axis
        * _default_connection_pads: Dict
            * pad_gap: '15um' -- Space between the connector pad and the charge island it is nearest to
            * pad_width: '125um' -- Width (x-axis) of the connector pad
            * pad_height: '30um' -- Height (y-axis) of the connector pad
            * pad_cpw_shift: '5um' -- Shift the connector pad cpw line by this much away from qubit
            * pad_cpw_extent: '25um' -- Shift the connector pad cpw line by this much away from qubit
            * cpw_width: 'cpw_width' -- Center trace width of the CPW line
            * cpw_gap: 'cpw_gap' -- Dielectric gap width of the CPW line
            * cpw_extend: '100um' -- Depth the connector line extense into ground (past the pocket edge)
            * pocket_extent: '5um' -- How deep into the pocket should we penetrate with the cpw connector (into the fround plane)
            * pocket_rise: '65um' -- How far up or downrelative to the center of the transmon should we elevate the cpw connection point on the ground plane
            * loc_W: '+1' -- Width location  only +-1
            * loc_H: '+1' -- Height location only +-1
    """

    default_options = Dict(
        pad_gap='30um',
        inductor_width='20um',
        pad_width='455um',
        pad_height='90um',
        pocket_width='650um',
        pocket_height='650um',
        # 90 has dipole aligned along the +X axis,
        # while 0 has dipole aligned along the +Y axis
        _default_connection_pads=Dict(
            pad_gap='15um',
            pad_width='125um',
            pad_height='30um',
            pad_cpw_shift='5um',
            pad_cpw_extent='25um',
            cpw_width='cpw_width',
            cpw_gap='cpw_gap',
            # : cpw_extend: how far into the ground to extend the CPW line from the coupling pads
            cpw_extend='100um',
            pocket_extent='5um',
            pocket_rise='65um',
            loc_W='+1',  # width location  only +-1
            loc_H='+1',  # height location only +-1
        ))
    """Default drawing options"""

    component_metadata = Dict(short_name='Pocket',
                              _qgeometry_table_path='True',
                              _qgeometry_table_poly='True',
                              _qgeometry_table_junction='True')
    """Component metadata"""

    TOOLTIP = """The base `TransmonPocket` class."""

    def make(self):
        """Define the way the options are turned into QGeometry.

        The make function implements the logic that creates the geoemtry
        (poly, path, etc.) from the qcomponent.options dictionary of
        parameters, and the adds them to the design, using
        qcomponent.add_qgeometry(...), adding in extra needed
        information, such as layer, subtract, etc.
        """
        self.make_pocket()
        self.make_connection_pads()

    def make_pocket(self):
        """Makes standard transmon in a pocket."""

        # self.p allows us to directly access parsed values (string -> numbers) form the user option
        p = self.p

        # extract chip name
        chip = p.chip

        # since we will reuse these options, parse them once and define them as varaibles
        pad_width = p.pad_width
        pad_height = p.pad_height
        pad_gap = p.pad_gap

        # make the pads as rectangles (shapely polygons)
        pad = draw.rectangle(pad_width, pad_height)
        pad_top = draw.translate(pad, 0, +(pad_height + pad_gap) / 2.)
        pad_bot = draw.translate(pad, 0, -(pad_height + pad_gap) / 2.)

        rect_jj = draw.LineString([(0, -pad_gap / 2), (0, +pad_gap / 2)])
        # the draw.rectangle representing the josephson junction
        # rect_jj = draw.rectangle(p.inductor_width, pad_gap)

        rect_pk = draw.rectangle(p.pocket_width, p.pocket_height)

        # Rotate and translate all qgeometry as needed.
        # Done with utility functions in Metal 'draw_utility' for easy rotation/translation
        # NOTE: Should modify so rotate/translate accepts qgeometry, would allow for
        # smoother implementation.
        polys = [rect_jj, pad_top, pad_bot, rect_pk]
        polys = draw.rotate(polys, p.orientation, origin=(0, 0))
        polys = draw.translate(polys, p.pos_x, p.pos_y)
        [rect_jj, pad_top, pad_bot, rect_pk] = polys

        # Use the geometry to create Metal qgeometry
        self.add_qgeometry('poly',
                           dict(pad_top=pad_top, pad_bot=pad_bot),
                           chip=chip)
        self.add_qgeometry('poly',
                           dict(rect_pk=rect_pk),
                           subtract=True,
                           chip=chip)
        # self.add_qgeometry('poly', dict(
        #     rect_jj=rect_jj), helper=True)
        self.add_qgeometry('junction',
                           dict(rect_jj=rect_jj),
                           width=p.inductor_width,
                           chip=chip)

    def make_connection_pads(self):
        """Makes standard transmon in a pocket."""
        for name in self.options.connection_pads:
            self.make_connection_pad(name)

    def make_connection_pad(self, name: str):
        """Makes n individual connector.

        Args:
            name (str) : Name of the connector
        """

        # self.p allows us to directly access parsed values (string -> numbers) form the user option
        p = self.p
        pc = self.p.connection_pads[name]  # parser on connector options

        # extract chip name
        chip = p.chip

        # define commonly used variables once
        cpw_width = pc.cpw_width
        cpw_extend = pc.cpw_extend
        pad_width = pc.pad_width
        pad_height = pc.pad_height
        pad_cpw_shift = pc.pad_cpw_shift
        pocket_rise = pc.pocket_rise
        pocket_extent = pc.pocket_extent

        # Define the geometry
        # Connector pad
        connector_pad = draw.rectangle(pad_width, pad_height, -pad_width / 2,
                                       pad_height / 2)
        # Connector CPW wire
        connector_wire_path = draw.wkt.loads(f"""LINESTRING (\
            0 {pad_cpw_shift+cpw_width/2}, \
            {pc.pad_cpw_extent}                           {pad_cpw_shift+cpw_width/2}, \
            {(p.pocket_width-p.pad_width)/2-pocket_extent} {pad_cpw_shift+cpw_width/2+pocket_rise}, \
            {(p.pocket_width-p.pad_width)/2+cpw_extend}    {pad_cpw_shift+cpw_width/2+pocket_rise}\
                                        )""")
        # for connector cludge
        connector_wire_CON = draw.buffer(connector_wire_path, cpw_width /
                                         2.)  # helper for the moment

        # Position the connector, rot and tranlate
        loc_W, loc_H = float(pc.loc_W), float(pc.loc_H)
        # if float(loc_W) not in [-1., +1.] or float(loc_H) not in [-1., +1.]:
        #     self.logger.info(
        #         'Warning: Did you mean to define a transmon wubit with loc_W and'
        #         ' loc_H that are not +1 or -1?? Are you sure you want to do this?'
        #     )
        objects = [connector_pad, connector_wire_path, connector_wire_CON]
        #objects = draw.scale(objects, loc_W, loc_H, origin=(0, 0))
        objects = draw.translate(
            objects,
            # loc_W * (p.pad_width) / 2.,
            # loc_H * (p.pad_height + p.pad_gap / 2 + pc.pad_gap))
            loc_W,
            loc_H)
        objects = draw.rotate_position(objects, p.orientation,
                                       [p.pos_x, p.pos_y])
        [connector_pad, connector_wire_path, connector_wire_CON] = objects

        self.add_qgeometry('poly', {f'{name}_connector_pad': connector_pad},
                           chip=chip)
        self.add_qgeometry('path', {f'{name}_wire': connector_wire_path},
                           width=cpw_width,
                           chip=chip)
        self.add_qgeometry('path', {f'{name}_wire_sub': connector_wire_path},
                           width=cpw_width + 2 * pc.cpw_gap,
                           subtract=True,
                           chip=chip)

        ############################################################

        # add pins
        points = np.array(connector_wire_path.coords)
        self.add_pin(name,
                     points=points[-2:],
                     width=cpw_width,
                     input_as_norm=True,
                     chip=chip)
