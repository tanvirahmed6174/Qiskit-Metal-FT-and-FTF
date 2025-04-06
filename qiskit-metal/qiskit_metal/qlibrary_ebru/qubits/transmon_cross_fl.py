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
"""Child of transmon cross, adds a flux line (galvanic T) to the arm with the
DC SQUID."""
# pylint: disable=invalid-name
# Modification of Transmon Pocket Object to include a charge line (would be better to just make as a child)

import numpy as np
from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.qubits.transmon_cross import TransmonCross


class TransmonCrossFL(TransmonCross):  # pylint: disable=invalid-name
    """The base `TransmonCrossFL` class.

    Inherits `TransmonCross` class

    Description:
        Simple Metal Transmon Cross object. Creates the X cross-shaped island,
        the "junction" on the south end, and up to 3 connectors on the remaining arms
        (claw or gap).

        'claw_width' and 'claw_gap' define the width/gap of the CPW line that
        makes up the connector. Note, DC SQUID currently represented by single
        inductance sheet

        Add connectors to it using the `connection_pads` dictonary. See BaseQubit for more
        information.

        Flux line is added by default to the 'south' arm where the DC SQUID is located,
        default is a symmetric T style

        Default Options:
        Convention: Values (unless noted) are strings with units included, (e.g., '30um')

        * make_fl -         (Boolean) If True, adds a flux line
        * t_top -           length of the flux line for mutual inductance to the SQUID
        * t_inductive_gap - amount of metallization between the flux line and SQUID
        * t_offset -        degree by which the tail of the T is offset from the center
        * t_width -         width of the flux line's transmission line center trace
        * t_gap -           dielectric gap of the flux line's transmission line

    .. image::
        transmon_cross_fl.png

    .. meta::
        Transmon Cross Flux Line

    """

    component_metadata = Dict(short_name='Q',
                              _qgeometry_table_poly='True',
                              _qgeometry_table_path='True')
    """Component metadata"""

    default_options = Dict(make_fl=True,
                           fl_options=Dict(t_top='15um',
                                           t_offset='0um',
                                           t_inductive_gap='3um',
                                           t_width='5um',
                                           t_shift='0um',
                                           t_gap='3um'))
    """Default drawing options"""

    TOOLTIP = """The base `TransmonCrossFL` class."""

    def make(self):
        """Define the way the options are turned into QGeometry."""
        super().make()

        if self.options.make_fl == True:
            self.make_flux_line()


#####################################################################

    def make_flux_line(self):
        """Creates the charge line if the user has charge line option to
        TRUE."""

        # Grab option values
        pf = self.p.fl_options
        p = self.p
        #Make the T flux line
        '''
        h_line = draw.LineString([(-pf.t_top / 2, 0), (pf.t_top / 2, 0)])  #Ebru: revert back to this if necessary

#        h_line = draw.LineString([(-pf.t_top/6+pf.t_offset, 0), (pf.t_top*1.5+pf.t_offset , 0)])

        v_line = draw.LineString([(pf.t_offset, 0), (pf.t_offset, -0.03)])

        parts = [h_line, v_line]

        # Move the flux line down to the SQUID
        parts = draw.translate(
            parts, pf.t_shift, -(p.cross_length + p.cross_gap + pf.t_inductive_gap + 
                        pf.t_width / 2 + pf.t_gap))

        # Rotate and translate based on crossmon location
        parts = draw.rotate(parts, p.orientation, origin=(0, 0))
        parts = draw.translate(parts, p.pos_x, p.pos_y)

        [h_line, v_line] = parts

        # Adding to qgeometry table
        self.add_qgeometry('path', {
            'h_line': h_line,
            'v_line': v_line
        },
                           width=pf.t_width,
                           layer=p.layer)

        self.add_qgeometry('path', {
            'h_line_sub': h_line,
            'v_line_sub': v_line
        },
                           width=pf.t_width + 2 * pf.t_gap,
                           subtract=True,
                           layer=p.layer)
'''
#ebru -- > above is the original version, I modified it to have an L-shaped flux line (no dent)
        v_line = draw.LineString([(pf.t_offset, 0), (pf.t_offset, -0.03)])
        t_pad = draw.Polygon([
            (-pf.t_width/2,0), (-pf.t_width/2, -pf.t_width-0.03),
            (pf.t_width/2, -pf.t_width-0.03),
            (pf.t_width/2, -pf.t_width),
            (pf.t_width+pf.t_top, -pf.t_width), (pf.t_width+pf.t_top, 0),
            (-pf.t_width/2, 0)
        ])


#         Geometry pocket (gap)
#         Same way applied for pocket
        pocket = draw.Polygon([
            (-pf.t_width/2-pf.t_gap,pf.t_gap), (-pf.t_width/2-pf.t_gap, -pf.t_width-0.03),
            (pf.t_width/2+pf.t_gap, -pf.t_width-0.03),
            (pf.t_width/2+pf.t_gap, -pf.t_width-pf.t_gap),
            (pf.t_width+pf.t_top, -pf.t_width-pf.t_gap), (pf.t_width+pf.t_top, pf.t_gap),
            (-pf.t_width/2-pf.t_gap, pf.t_gap)
        ])
#        
#
#    
        main_pin_line = draw.LineString([(0,0),
                                         (0,-0.0345)])


        # Create polygon object list
        polys1 = [t_pad,pocket, main_pin_line]

        # Rotates and translates all the objects as requested. Uses package functions in
        # 'draw_utility' for easy rotation/translation
        polys1 = draw.rotate(polys1, p.orientation, origin=(0, 0))
        polys1 = draw.translate(polys1, xoff=p.pos_x-pf.t_gap+pf.t_shift, yoff=p.pos_y-p.cross_length-p.cross_gap-pf.t_inductive_gap-pf.t_gap)#-pf.t_width/2)
        [t_pad,pocket,  main_pin_line] = polys1

        # Adds the object to the qgeometry table
        self.add_qgeometry('poly', dict(t_pad=t_pad), layer=p.layer)

        # Subtracts out ground plane on the layer its on
        self.add_qgeometry('poly',
                           dict(pocket=pocket),
                           subtract=True,
                           layer=p.layer)



 
        # Generating pin
        pin_line = main_pin_line.coords
        self.add_pin("flux_line",
                     points=pin_line,
                     width=pf.t_width,
                     gap=pf.t_gap,
                     input_as_norm=True)
