"""
GDF-specific fields



"""

#-----------------------------------------------------------------------------
# Copyright (c) 2013, yt Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------

from yt.fields.field_info_container import \
    FieldInfoContainer

# The nice thing about GDF is that for the most part, everything is in CGS,
# with potentially a scalar modification.

class GDFFieldInfo(FieldInfoContainer):
    known_other_fields = (
        ("density", ("g/cm**3", ["density"], None)),
        ("specific_energy", ("erg/g", ["thermal_energy"], None)),
        ("pressure", ("erg/cm**3", ["pressure"], None)),
        ("temperature", ("K", ["temperature"], None)),
        ("velocity_x", ("cm/s", ["velocity_x"], None)),
        ("velocity_y", ("cm/s", ["velocity_y"], None)),
        ("velocity_z", ("cm/s", ["velocity_z"], None)),
        ("mag_field_x", ("gauss", ["magnetic_field_x"], None)),
        ("mag_field_y", ("gauss", ["magnetic_field_y"], None)),
        ("mag_field_z", ("gauss", ["magnetic_field_z"], None)),

        ("metal_density", ("code_mass/code_length**3", ["metal_density"], None)),
        ("H_p0_density", ("code_mass/code_length**3", ["H_p0_density"], None)),
        ("H_p1_density", ("code_mass/code_length**3", ["H_p1_density"], None)),
        ("H_m1_density", ("code_mass/code_length**3", ["H_m1_density"], None)),
        ("H2_p0_density", ("code_mass/code_length**3", ["H2_p0_density"], None)),
        ("H2_p1_density", ("code_mass/code_length**3", ["H2_p1_density"], None)),
        ("He_p0_density", ("code_mass/code_length**3", ["He_p0_density"], None)),
        ("He_p1_density", ("code_mass/code_length**3", ["He_p1_density"], None)),
        ("He_p2_density", ("code_mass/code_length**3", ["He_p2_density"], None)),
        ("HD_p0_density", ("code_mass/code_length**3", ["HD_p0_density"], None)),
        ("D_p0_density", ("code_mass/code_length**3", ["D_p0_density"], None)),
        ("D_p1_density", ("code_mass/code_length**3", ["D_p1_density"], None)),
        ("El_density",  ("code_mass/code_length**3", ["El_density"], None)),
    )
    known_particle_fields = ()

    def __init__(self, *args, **kwargs):
        super(GDFFieldInfo, self).__init__(*args, **kwargs)
        self.species_names = ["H_p0","H_p1","H_m1","H2_p0","H2_p1",
                              "He_p0", "He_p1", "He_p2",
                              "HD_p0", "D_p0", "D_p1", "El"]        

    def setup_fluid_fields(self):
        from yt.fields.magnetic_field import \
            setup_magnetic_field_aliases
        setup_magnetic_field_aliases(self, "gdf", ["magnetic_field_%s" % ax for ax in "xyz"])
