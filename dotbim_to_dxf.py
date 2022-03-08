from collections import defaultdict
from pathlib import Path
import dotbimpy
import ezdxf
import pyquaternion


def dotbim_mesh_to_dxf_mesh(layout, dotbim_mesh):
    dxf_mesh = layout.add_mesh()
    with dxf_mesh.edit_data() as mesh_data:
        mesh_data.vertices = [
            (dotbim_mesh.coordinates[c], dotbim_mesh.coordinates[c + 1], dotbim_mesh.coordinates[c + 2])
            for c in range(0, len(dotbim_mesh.coordinates), 3)
        ]
        mesh_data.faces = [
            (dotbim_mesh.indices[i], dotbim_mesh.indices[i + 1], dotbim_mesh.indices[i + 2])
            for i in range(0, len(dotbim_mesh.indices), 3)
        ]

    return dxf_mesh


def dotbim_to_dxf(dotbim_filepath):
    file = dotbimpy.File.read(dotbim_filepath)
    dxf_file = ezdxf.new(dxfversion="R2010")
    dxf_msp = dxf_file.modelspace()
    meshes_users = defaultdict(list)

    for elt in file.elements:
        meshes_users[elt.mesh_id].append(elt)
    for mesh_id, elts in meshes_users.items():
        dotbim_mesh = next((m for m in file.meshes if m.mesh_id == mesh_id), None)
        for elt in elts:
            mesh = dotbim_mesh_to_dxf_mesh(dxf_msp, dotbim_mesh)
            matrix = ezdxf.math.Matrix44.translate(elt.vector.x, elt.vector.y, elt.vector.z)
            rot = elt.rotation
            matrix_rotation = pyquaternion.Quaternion(rot.qw, rot.qx, rot.qy, rot.qz).rotation_matrix
            for i, col in enumerate(matrix_rotation):
                matrix.set_col(i, col)
            mesh.transform(matrix)

    dotbim_path = Path(dotbim_filepath)
    dxf_filepath = dotbim_path.with_name(dotbim_path.stem + ".dxf")
    dxf_file.saveas(str(dxf_filepath))
    return str(dxf_filepath)


if __name__ == "__main__":
    dotbim_filepath = r"c:/path/to/file.bim"

    dxf_filepath = dotbim_to_dxf(dotbim_filepath)
    input(f"File successfully exported to {dxf_filepath}")
