# Dotbim <-> DXF converter

This is a collection of utility scripts to convert from and to the dxf (Drawing Exchange Format) file format :

1. Converting dotbim files to dxf :

- The dotbim geometry is exported in the dxf file using [MESH entities](https://ezdxf.readthedocs.io/en/master/dxfentities/mesh.html) (most lightweight entity type for 3D in dxf)
- Dotbim Meshes are exported in BLOCKs
- Dotbim entities are exported in BLOCKs
- Dotbim entities that use the same dotbim mesh id will instance a block of the relevant mesh inside their block definition
- Dotbim entites color will be exported as the BLOCK color
- Transparency is not yet supported
- Dotbim entities properties are exported using BLOCK attributes

2. Converting dxf files to dotbim :

- WIP

__Important__ : Please make sure you have installed both `dotbimpy` and `ezdxf` modules and all their dependencies in your local python environment.

Usually, after installing your preferred python version and adding pip to the PATH system variables, you can install a new module by opening a system console and typing :

`pip install dotbimpy`

then 

`pip install ezdxf`
