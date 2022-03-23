from datetime import date
from pathlib import Path
import uuid
import numpy as np
from pyquaternion import Quaternion
import dotbimpy
import ezdxf


def dxf_to_dotbim(dxf_filepath):
    dotbim_meshes = []
    dotbim_elements = []

    dxf_file = ezdxf.readfile(str(dxf_filepath))
    inserts = dxf_file.modelspace().query("INSERT")
    block_names = {insert.dxf.name for insert in inserts}
    block_inserts = dict()

    for block_name in block_names:
        layout = dxf_file.blocks.get(block_name)
        if layout.block.is_anonymous or layout.block.is_xref:
            continue
        vertices = []
        faces = []
        for entity in layout:
            verts_existing = len(vertices)
            if isinstance(entity, ezdxf.entities.mesh.Mesh):
                for f in entity.faces:
                    faces.extend((verts_existing // 3 + f[0], verts_existing // 3 + f[1], verts_existing // 3 + f[2]))
                for c in entity.vertices:
                    vertices.extend((c[0], c[1], c[2]))
            elif isinstance(entity, ezdxf.entities.Face3d):
                face3d_verts = entity.wcs_vertices()
                faces.extend([verts_existing // 3 + i for i in range(len(face3d_verts))])
                for co in face3d_verts:
                    vertices.extend(co)

        mesh_id = len(dotbim_meshes)
        dotbim_meshes.append(dotbimpy.Mesh(mesh_id=mesh_id, coordinates=vertices, indices=faces))
        block_inserts[block_name] = mesh_id

    for insert in inserts:
        mesh_id = block_inserts[insert.block().name]

        ucs = insert.ucs()
        location = dotbimpy.Vector(x=ucs.origin.x, y=ucs.origin.y, z=ucs.origin.z)
        matrix = np.array(list(ucs.matrix))
        matrix.shape = (4, 4)
        matrix = matrix.transpose()
        quat = Quaternion(matrix=matrix)
        rotation = dotbimpy.Rotation(qx=float(quat.x), qy=float(quat.y), qz=float(quat.z), qw=float(quat.w))

        rgb = ezdxf.colors.int2rgb(insert.dxf.true_color)
        alpha = (1 - ezdxf.colors.transparency2float(insert.dxf.transparency)) * 255
        color = dotbimpy.Color(r=rgb[0], g=rgb[1], b=rgb[2], a=alpha)

        info = {attrib.dxf.tag: attrib.dxf.text for attrib in insert.attribs if attrib.dxf.text != ""}

        dotbim_elements.append(
            dotbimpy.Element(
                mesh_id=mesh_id,
                vector=location,
                guid=info.get("guid", uuid.uuid4()),
                info=info,
                rotation=rotation,
                type=info.get("type", insert.dxf.layer),
                color=color,
            )
        )
    author = dxf_file.header.custom_vars.get("Author", "John Doe")
    date_file = dxf_file.header.custom_vars.get("Date", date.today().strftime("%d.%m.%Y"))
    file_info = {"Author": author, "Date": date_file}
    for tag, name in dxf_file.header.custom_vars:
        if tag in ("Author", "Date"):
            continue
        file_info[tag] = name

    dotbim_file = dotbimpy.File("1.0.0", meshes=dotbim_meshes, elements=dotbim_elements, info=file_info)

    dotbim_path = Path(dxf_filepath)
    dotbim_path = dotbim_path.with_name(dotbim_path.stem + "_export.bim")
    dotbim_file.save(str(dotbim_path))


if __name__ == "__main__":
    dxf_filepath = r"c:/path/to/file.dxf"
    dxf_to_dotbim(dxf_filepath)
