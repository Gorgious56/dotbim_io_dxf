from collections import defaultdict
from pathlib import Path
import dotbimpy
import ezdxf
import pyquaternion


def dotbim_mesh_to_dxf_mesh(layout, dotbim_mesh):
    dxf_mesh = layout.add_mesh(dxfattribs={"color": 0})  # Color BY BLOCK
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


def rgb_to_hex(vals):
    # Ensure values are rounded integers, convert to hex, and concatenate
    return int("0x" + "".join(["{:02X}".format(int(round(x))) for x in vals]), 16)


def dotbim_to_dxf(dotbim_filepath):
    file = dotbimpy.File.read(dotbim_filepath)
    dxf_file = ezdxf.new(dxfversion="R2010")
    dxf_msp = dxf_file.modelspace()
    meshes_users = defaultdict(list)

    for elt in file.elements:
        meshes_users[elt.mesh_id].append(elt)
    for mesh_id, elts in meshes_users.items():
        dotbim_mesh = next((m for m in file.meshes if m.mesh_id == mesh_id), None)
        block_mesh_def = dxf_file.blocks.new(name=f"Mesh {mesh_id}")
        dotbim_mesh_to_dxf_mesh(block_mesh_def, dotbim_mesh)
        for elt in elts:
            block_elt_def = dxf_file.blocks.new(name=elt.info.get("Name", str(elt.guid)))
            block_elt_def.add_blockref(block_mesh_def.name, insert=(0, 0, 0), dxfattribs={"color": 0})  # Color BY BLOCK

            attr_names = list(elt.info.keys())
            attr_names.extend(("guid", "type"))
            for attr_name in attr_names:
                # Can't seem to make the invisible attribute work. Setting the texts really really small for now
                block_elt_def.add_attdef(attr_name, dxfattribs={"invisible": True, "height": 0.00001})

            block_elt_instance = dxf_msp.add_blockref(
                block_elt_def.name,
                insert=(0, 0, 0),
                dxfattribs={
                    "color": 257,  # True Color
                    "true_color": rgb_to_hex((elt.color.r, elt.color.g, elt.color.b)),
                    # "transparency": float(elt.color.a / 255),  # Throws DXFValueError. Can't make it work for INSERT ?
                },
            )
            matrix = ezdxf.math.Matrix44.translate(elt.vector.x, elt.vector.y, elt.vector.z)
            rot = elt.rotation
            matrix_rotation = pyquaternion.Quaternion(rot.qw, rot.qx, rot.qy, rot.qz).rotation_matrix
            for i, col in enumerate(matrix_rotation):
                matrix.set_col(i, col)
            block_elt_instance.transform(matrix)

            attributes = {attrib: value for (attrib, value) in elt.info.items()}
            attributes.update({"guid": elt.guid, "type": elt.type})
            block_elt_instance.add_auto_attribs(attributes)

    dotbim_path = Path(dotbim_filepath)
    dxf_filepath = dotbim_path.with_name(dotbim_path.stem + ".dxf")
    dxf_file.saveas(str(dxf_filepath))
    return str(dxf_filepath)


if __name__ == "__main__":
    dotbim_filepath = r"c:/path/to/file.bim"

    dxf_filepath = dotbim_to_dxf(dotbim_filepath)
    input(f"File successfully exported to {dxf_filepath}")
