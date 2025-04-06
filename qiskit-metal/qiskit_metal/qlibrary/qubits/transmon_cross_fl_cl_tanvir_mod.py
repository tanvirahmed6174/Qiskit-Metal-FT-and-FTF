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
from qiskit_metal.qlibrary.qubits.transmon_cross_fl_tanvir_temp import TransmonCrossFL_tanvir_temp


class TransmonCrossFL_CL_Tanvir(TransmonCrossFL_tanvir_temp):  # pylint: disable=invalid-name
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

    default_options = Dict(make_cl=True,
                           cl_options=Dict(
                                           c_offset='0um',
                                           c_length='10um',
                                           c_width='5um',
                                           c_gap='3um',
                                           c_angle=180, 
				           c_ground_gap='5um',
                           translate_x='0um',
                           translate_y='0um'))
    """Default drawing options"""

    TOOLTIP = """The base `TransmonCrossFL` class."""

    def make(self):
        """Define the way the options are turned into QGeometry."""
        super().make()

        if self.options.make_cl == True:
            self.make_charge_line()

    def make_charge_line(self):
        """Creates the charge line if the user has charge line option to
        TRUE."""

        # Grab option values
        pc = self.p.cl_options
        p = self.p
        #Make the T flux line
 


        v_line2 = draw.LineString([(pc.c_offset, 0), (pc.c_offset,-0.1)])
        v_line2_dielec = draw.LineString([(pc.c_offset, 0 + pc.c_gap), (pc.c_offset,-0.1)])
#        c_etcher = draw.buffer(v_line, pc.c_gap)
#        parts = [v_line, c_etcher]
        parts = [v_line2, v_line2_dielec]


        # Move the flux line down to the SQUID
        parts = draw.translate(
            parts, 0, -(p.cross_length + p.cross_gap +
                        pc.c_width / 2 + pc.c_gap))

        # Rotate and translate based on crossmon location
        parts = draw.rotate(parts,pc.c_angle, origin=(0, 0))
        parts = draw.translate(parts, p.pos_x, p.pos_y + pc.c_ground_gap - pc.c_gap)
        parts = draw.translate(parts, pc.translate_x, pc.translate_y)
#        [v_line, c_etcher] = parts
        [v_line2, v_line2_dielec] = parts        # Adding to qgeometry table
        self.add_qgeometry('path', {

            'v_line2':v_line2,


        },
                           width=pc.c_width,
                           layer=p.layer)
        self.add_qgeometry('path', {

            'v_line2_dielec':v_line2_dielec,


        },
                           width=pc.c_width + 2*pc.c_gap,
                           subtract = True, 
                           layer=p.layer)#        self.add_qgeometry('path', {
# 
#            'c_etcher': c_etcher
#        },
##                           width=pc.c_width + 2 * pc.c_gap,
#                           subtract=True,
#                           layer=p.layer)

        # Generating pin
        pin_line = v_line2.coords
        self.add_pin("charge_line",
                     points=pin_line,
                     width=pc.c_width,
                     gap=pc.c_gap,
                     input_as_norm=True)
