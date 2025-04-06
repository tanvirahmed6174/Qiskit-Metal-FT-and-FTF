
import numpy as np
from qiskit_metal import draw, Dict
from qiskit_metal.qlibrary.qubits.transmon_pocket_cl import TransmonPocketCL


class TransmonPocketCL_FL(TransmonPocketCL):  # pylint: disable=invalid-name

    component_metadata = Dict(short_name='Q', _qgeometry_table_poly='True')
    """Component metadata"""

    default_options = Dict(
        make_FL=True,
        fl_options=Dict(t_top='15um',
        t_offset='0um',
        t_inductive_gap='3um',
        t_width='5um',
        t_shift='0um',
        t_gap='3um', 
        ))
    """Default drawing options"""

    TOOLTIP = """Create a standard pocket transmon qubit for a ground plane,
    with two pads connected by a junction"""

    def make(self):
        """Define the way the options are turned into QGeometry."""
        super().make()

        if self.options.make_FL == True:
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
        polys1 = draw.rotate(polys1, 0, origin=(0, 0))
        polys1 = draw.translate(polys1, xoff=p.pos_x-pf.t_gap+pf.t_shift, yoff=p.pos_y-p.pocket_height/2-pf.t_inductive_gap-pf.t_gap+pf.t_offset)#-pf.t_width/2)
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
