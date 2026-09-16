import numpy as np

from yt.utilities.logger import ytLogger as mylog


def parse_unit_dimension(unit_dimension):
    r"""Transforms an openPMD unitDimension into a string.

    Parameters
    ----------
    unit_dimension : array_like
        integer array of length 7 with one entry for the dimensional component of every
        SI unit

        [0] length L,
        [1] mass M,
        [2] time T,
        [3] electric current I,
        [4] thermodynamic temperature theta,
        [5] amount of substance N,
        [6] luminous intensity J

    References
    ----------

    https://github.com/openPMD/openPMD-standard/blob/latest/STANDARD.md#unit-systems-and-dimensionality


    Returns
    -------
    str

    Examples
    --------
    >>> velocity = [1.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0]
    >>> print(parse_unit_dimension(velocity))
    'm**1*s**-1'

    >>> magnetic_field = [0.0, 1.0, -2.0, -1.0, 0.0, 0.0, 0.0]
    >>> print(parse_unit_dimension(magnetic_field))
    'kg**1*s**-2*A**-1'
    """
    if len(unit_dimension) != 7:
        mylog.error("SI must have 7 base dimensions!")
    unit_dimension = np.asarray(unit_dimension, dtype="int64")
    dim = []
    si = ["m", "kg", "s", "A", "C", "mol", "cd"]
    for i in np.arange(7):
        if unit_dimension[i] != 0:
            dim.append(f"{si[i]}**{unit_dimension[i]}")
    return "*".join(dim)


def is_const_component(record_component):
    """Determines whether an iteration record is constant

    Parameters
    ----------
    record_component : openpmd_api.openpmd_api_cxx.Record_component

    Returns
    -------
    bool
        True if constant, False otherwise

    References
    ----------
    .. https://github.com/openPMD/openPMD-standard/blob/latest/STANDARD.md,
       section 'Constant Record Components'
    """
    return "value" in record_component.attributes


# TODO delete
"""
def component_ordering(record_component = np.array, geometry = str, data_order = str, axes_labels = list):
    This function converts arrays of the on-disk record component shape to a readable, column-major style
    Example
    -------
    np.shape(record_component_array) == (256, 512), C-order (row-major, ie axes_labels = ['z', 'x']

    component_ordering(record_component_array) == np.array([512,256]) to represent [nX, nZ] where nX and nZ are
    the number of cells in the x and z dimensions

    Parameters
    ----------
    mesh: openpmd_api.openpmd_api_cxx.Mesh
    record_axis: a string which specifies which desired axis

    Returns
    -------
    int
        specifying index of axis
    if "cartesian" in geometry:
        if data_order == "C": #row major
            assert(axes_labels == sorted(axes_labels)[::-1]) #is this true generally?
            #[::-1]
            return record_component
        elif data_order == "F": #column major
            assert(axes_labels == sorted(axes_labels))
            mylog.warning("Fortran dataOrder is not yet supported :( ")
            raise NotImplementedError
    else:
        mylog.warning("'{}' geometry is not yet supported :( )".format(geometry))
        raise NotImplementedError
"""


def make_xyz(value, axes_labels, fill_value=None):
    """Reorder OpenPMD values into yt's x, y, z axis order.

    Parameters
    ----------
    value : array_like
        Mesh data or a one-dimensional mesh metadata vector.
    axes_labels : sequence of str
        OpenPMD axis labels corresponding to ``value``'s dimensions.
    fill_value : scalar, optional
        Value used for missing axes in metadata vectors.
    """
    axes_labels = tuple(axes_labels)
    if len(set(axes_labels)) != len(axes_labels) or not set(axes_labels) <= {
        "x",
        "y",
        "z",
    }:
        raise ValueError(f"Invalid OpenPMD axis labels: {axes_labels}")

    value = np.asarray(value)
    if value.ndim == 1:
        if value.size != len(axes_labels):
            raise ValueError(
                "Metadata vector size must match the number of OpenPMD axes"
            )
        permutation = tuple(axes_labels.index(axis) for axis in axes_labels)
        reordered = value[list(permutation)]
        result = np.full(3, fill_value, dtype=value.dtype)
        for index, axis in enumerate(("x", "y", "z")):
            if axis in axes_labels:
                result[index] = reordered[axes_labels.index(axis)]
        return result

    yt_axes = tuple(axis for axis in ("x", "y", "z") if axis in axes_labels)
    permutation = tuple(axes_labels.index(axis) for axis in yt_axes)

    if permutation != tuple(range(len(permutation))):
        value = np.transpose(value, permutation)

    for axis_index, axis in enumerate(("x", "y", "z")):
        if axis not in axes_labels:
            value = np.expand_dims(value, axis=axis_index)
    return value


# TODO wtf is this nonsense. The axis labels are not always reversed.
def coordinate_mapping(component=str):
    """Conversion between yt axes and openpmd_api axes.
    Parameters
    ----------
    component : string
        component is a constant record component refering to the axis omitted in the simulation

    Example
    --------
    Dataset has MeshRecord.axes_labels == ['z', 'x'] which is transposed for yt to
    result in a OpenPMDDataset with domain_dimensions = [nX, nZ, 1]
    where nX and nZ represent the number of cells along the now X and Y axes, and the z axis has been padded.

    When we annotate particles, yt will call on x and y particle postitions, but y particle positions are
    actually z particle positions in the openpmd_api.

    """
    coord_dict = {"x": "x", "y": "z", "z": "y"}
    return coord_dict[component]


def get_component(record, record_axis, index=0, extent=None):
    """Grabs a Record Component from a Record as a whole or sliced.

    Parameters
    ----------
    record : openpmd_api_cxx.Record
    record_axis : str
        the openpmd_api_cxx.Record_Component string key, not necessarily a physical axis
    index : int, optional
        first entry along the first axis to read
    extent : int, optional
        number of entries to read
        note that the previous frontend named this variable offset,
        which we thinks adds some confusion.
        If not supplied, every entry after index is returned.
    Notes
    -----
    This scales every entry of the component with the respective "unitSI".

    Returns
    -------
    ndarray
        (N,) 1D in case of particle data
        (O,P,Q) 1D/2D/3D in case of mesh data
    """
    record_component = record[record_axis]
    unit_si = record_component.get_attribute("unitSI")
    if is_const_component(record_component):
        shape = np.asarray(record_component.get_attribute("shape"))
        if extent is None:
            shape -= index
        else:
            shape = extent
        # component is constant, craft an array by hand
        registered = record_component.get_attribute("value")
        return np.full(shape, registered * unit_si)
    else:
        if extent is not None:
            extent += index
            if len(record_component.shape) == 3:
                registered = record_component[
                    index[0] : extent[0], index[1] : extent[1], index[2] : extent[2]
                ]
            elif len(record_component.shape) == 2:
                registered = record_component[
                    index[0] : extent[0], index[1] : extent[1]
                ]
            elif len(record_component.shape) == 1:
                registered = record_component[index:extent]
        else:
            # when we don't slice we have to `load_chunk()`
            registered = record_component.load_chunk()
        record_component.series_flush()
        return np.multiply(registered, unit_si)
