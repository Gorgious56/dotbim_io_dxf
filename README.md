# Dotbim <-> DXF converter

This is a collection of scripts to convert from and to the dxf (Drawing Exchange Format) file format and [dotbim file format](https://github.com/paireks/dotbim) :

1. Converting [dotbim files to dxf](https://github.com/Gorgious56/dotbim_io_dxf/blob/master/dotbim_to_dxf.py) :

- The dotbim geometry is exported in the dxf file using [MESH entities](https://ezdxf.readthedocs.io/en/master/dxfentities/mesh.html) (most lightweight entity type for 3D in dxf)
- Entities are exported in BLOCKs
- Entities that use the same dotbim mesh id will reference the same BLOCK
- Entities color will be exported as the BLOCK BYOBJECT true color
- Entities transparency will be exported as the BLOCK BYOBJECT transparency
- Entities properties are exported using BLOCK attributes
- File properties are copied to the dxf header custom variables
- Entities are placed in a layer corresponding to their type
- DXF file is exported in the same folder as the dotbim file

2. Converting [dxf files to dotbim](https://github.com/Gorgious56/dotbim_io_dxf/blob/master/dxf_to_dotbim.py) :

- Only type of supported geometry is dxf [MESH](https://ezdxf.readthedocs.io/en/master/dxfentities/mesh.html)
- Only geometry that is placed in the first level of a block is exported
- Top level BLOCKs BYOBJECT true color and transparency are exported
- Block attributes are exported as entity properties
- DXF header custom vars are exported as file info properties
- dotbim file is exported in the same folder as the dotbim file

__Important__ : Make sure you installed both `dotbimpy` and `ezdxf` modules and all their dependencies in your local python environment.

After installing python and adding pip to the PATH system variables, you can install a new module by opening a system console and typing :

`pip install dotbimpy`

and 

`pip install ezdxf`
