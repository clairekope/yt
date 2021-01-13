"""
Fields specific to Streaming data



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

from yt.fields.species_fields import \
    setup_species_fields

class StreamFieldInfo(FieldInfoContainer):
    known_other_fields = (
        ("density", ("code_mass/code_length**3", ["density"], None)),
        ("dark_matter_density", ("code_mass/code_length**3", ["dark_matter_density"], None)),
        ("number_density", ("1/code_length**3", ["number_density"], None)),
        ("pressure", ("dyne/code_length**2", ["pressure"], None)),
        ("thermal_energy", ("erg / g", ["thermal_energy"], None)),
        ("temperature", ("K", ["temperature"], None)),
        ("velocity_x", ("code_length/code_time", ["velocity_x"], None)),
        ("velocity_y", ("code_length/code_time", ["velocity_y"], None)),
        ("velocity_z", ("code_length/code_time", ["velocity_z"], None)),
        ("magnetic_field_x", ("gauss", [], None)),
        ("magnetic_field_y", ("gauss", [], None)),
        ("magnetic_field_z", ("gauss", [], None)),
        ("radiation_acceleration_x", ("code_length/code_time**2", ["radiation_acceleration_x"], None)),
        ("radiation_acceleration_y", ("code_length/code_time**2", ["radiation_acceleration_y"], None)),
        ("radiation_acceleration_z", ("code_length/code_time**2", ["radiation_acceleration_z"], None)),
        ("metallicity", ("Zsun", ["metallicity"], None)),

        # We need to have a bunch of species fields here, too
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

    known_particle_fields = (
        ("particle_position", ("code_length", ["particle_position"], None)),
        ("particle_position_x", ("code_length", ["particle_position_x"], None)),
        ("particle_position_y", ("code_length", ["particle_position_y"], None)),
        ("particle_position_z", ("code_length", ["particle_position_z"], None)),
        ("particle_velocity", ("code_length/code_time", ["particle_velocity"], None)),
        ("particle_velocity_x", ("code_length/code_time", ["particle_velocity_x"], None)),
        ("particle_velocity_y", ("code_length/code_time", ["particle_velocity_y"], None)),
        ("particle_velocity_z", ("code_length/code_time", ["particle_velocity_z"], None)),
        ("particle_index", ("", ["particle_index"], None)),
        ("particle_gas_density", ("code_mass/code_length**3", ["particle_gas_density"], None)),
        ("particle_gas_temperature", ("K", ["particle_gas_temperature"], None)),
        ("particle_mass", ("code_mass", ["particle_mass"], None)),
        ("smoothing_length", ("code_length", ["smoothing_length"], None)),
        ("density", ("code_mass/code_length**3", ["density"], None)),
        ("temperature", ("code_temperature", ["temperature"], None)),
        ("creation_time", ("code_time", ["creation_time"], None)),
        ("age", ("code_time", [], None))
    )

    def __init__(self, *args, **kwargs):
        super(StreamFieldInfo, self).__init__(*args, **kwargs)
        self.species_names = ["H_p0","H_p1","H_m1","H2_p0","H2_p1",
                              "He_p0", "He_p1", "He_p2",
                              "HD_p0", "D_p0", "D_p1", "El"]

    def setup_fluid_fields(self):
        from yt.fields.magnetic_field import \
            setup_magnetic_field_aliases
        for field in self.ds.stream_handler.field_units:
            if field[0] in self.ds.particle_types:
                continue
            units = self.ds.stream_handler.field_units[field]
            if units != '': 
                self.add_output_field(field, sampling_type="cell", units=units)
        setup_magnetic_field_aliases(self, "stream", 
                                     ["magnetic_field_%s" % ax for ax in "xyz"])
        #import pdb; pdb.set_trace()
        setup_species_fields(self)

    def add_output_field(self, name, sampling_type, **kwargs):
        if name in self.ds.stream_handler.field_units:
            kwargs['units'] = self.ds.stream_handler.field_units[name]
        super(StreamFieldInfo, self).add_output_field(name, sampling_type, **kwargs)
