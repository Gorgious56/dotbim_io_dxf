from collections import defaultdict
from pathlib import Path
import dotbimpy
import ezdxf
import pyquaternion
import uuid


def create_blockdef_from_dotbim_mesh(dxf_file, block_name, dotbim_mesh):
    block_def = dxf_file.blocks.new(name=block_name)
    dxf_mesh = block_def.add_mesh(dxfattribs={"color": 0})  # Color BY BLOCK
    with dxf_mesh.edit_data() as mesh_data:
        mesh_data.vertices = [
            (dotbim_mesh.coordinates[c], dotbim_mesh.coordinates[c + 1], dotbim_mesh.coordinates[c + 2])
            for c in range(0, len(dotbim_mesh.coordinates), 3)
        ]
        mesh_data.faces = [
            (dotbim_mesh.indices[i], dotbim_mesh.indices[i + 1], dotbim_mesh.indices[i + 2])
            for i in range(0, len(dotbim_mesh.indices), 3)
        ]


def rgb_to_hex(vals):
    return int("0x" + "".join(["{:02X}".format(int(round(x))) for x in vals]), 16)


def get_layer_names(elt_types):
    for elt_type in elt_types:
        for char in ("/", "<", ">", "\\", "“", '"', ":", ";", "?", "*", "|", "=", "‘"):
            elt_type = elt_type.replace(char, "_")
        yield elt_type


def get_matrix(dotbim_element):
    matrix = ezdxf.math.Matrix44.translate(dotbim_element.vector.x, dotbim_element.vector.y, dotbim_element.vector.z)
    rot = dotbim_element.rotation
    matrix_rotation = pyquaternion.Quaternion(rot.qw, rot.qx, rot.qy, rot.qz).rotation_matrix
    for i, col in enumerate(matrix_rotation):
        matrix.set_col(i, col)
    return matrix


def dotbim_to_dxf(dotbim_filepath):
    dotbim_file = dotbimpy.File.read(dotbim_filepath)
    dxf_file = ezdxf.new(dxfversion="R2010")
    for key, value in dotbim_file.info.items():
        dxf_file.header.custom_vars.append(key, value)
    dxf_msp = dxf_file.modelspace()
    meshes_users = defaultdict(list)
    elt_types = set()

    for elt in dotbim_file.elements:
        meshes_users[elt.mesh_id].append(elt)
        elt_types.add(elt.type)
    for layer_name in get_layer_names(elt_types):
        dxf_file.layers.new(layer_name)
    for mesh_id, elts in meshes_users.items():
        dotbim_mesh = next((m for m in dotbim_file.meshes if m.mesh_id == mesh_id), None)
        block_name = f"Mesh {mesh_id}_{uuid.uuid4()}"
        create_blockdef_from_dotbim_mesh(dxf_file, block_name, dotbim_mesh)
        for elt in elts:
            block_elt_instance = dxf_msp.add_blockref(
                block_name,
                insert=(0, 0, 0),
                dxfattribs={
                    "color": 257,  # True Color
                    "true_color": rgb_to_hex((elt.color.r, elt.color.g, elt.color.b)),
                    "layer": str(elt.type)
                    # "transparency": float(elt.color.a / 255),  # Throws DXFValueError. Can't make it work for INSERT ?
                },
            )
            block_elt_instance.transform(get_matrix(elt))

            attributes = {attrib: value for (attrib, value) in elt.info.items()}
            attributes.update({"guid": elt.guid, "type": elt.type})
            for key, value in attributes.items():
                # Can't seem to make the invisible attribute work. Setting the texts really really small for now
                block_elt_instance.add_attrib(key, value, dxfattribs={"invisible": 1, "height": 0.00001})

    dotbim_path = Path(dotbim_filepath)
    dxf_filepath = dotbim_path.with_name(dotbim_path.stem + ".dxf")
    dxf_file.saveas(str(dxf_filepath))


if __name__ == "__main__":
    dotbim_filepath = r"c:/path/to/file.bim"
    dotbim_to_dxf(dotbim_filepath)
