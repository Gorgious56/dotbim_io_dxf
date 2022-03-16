from pathlib import Path
import dotbimpy
import ezdxf
import uuid


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
        for entity in layout:
            if not isinstance(entity, ezdxf.entities.mesh.Mesh):
                continue
            faces = []
            for f in entity.faces:
                faces.extend((f[0], f[1], f[2]))
            vertices = []
            for c in entity.vertices:
                vertices.extend((c[0], c[1], c[2]))
            mesh_id = len(dotbim_meshes)
            dotbim_meshes.append(dotbimpy.Mesh(mesh_id=mesh_id, coordinates=vertices, indices=faces))
        block_inserts[block_name] = mesh_id

    for insert in inserts:
        mesh_id = block_inserts[insert.block().name]
        ucs = insert.ucs()
        location = dotbimpy.Vector(x=ucs.origin.x, y=ucs.origin.y, z=ucs.origin.z)
        info = {attrib.dxf.tag: attrib.dxf.text for attrib in insert.attribs if attrib.dxf.text != ""}
        # TODO figure out a way to get rotation from coordinate system
        rotation = dotbimpy.Rotation(qx=0, qy=0, qz=0, qw=1)
        element_type = info.get("type") or insert.dxf.layer
        rgb = ezdxf.colors.int2rgb(insert.dxf.true_color)
        alpha = (1 - ezdxf.colors.transparency2float(insert.dxf.transparency)) * 255
        color = dotbimpy.Color(r=rgb[0], g=rgb[1], b=rgb[2], a=alpha)

        dotbim_elements.append(
            dotbimpy.Element(
                mesh_id=mesh_id,
                vector=location,
                guid=uuid.uuid4(),
                info=info,
                rotation=rotation,
                type=element_type,
                color=color,
            )
        )

    # file_info = {"Author": author, "Date": date.today().strftime("%d.%m.%Y")}
    dotbim_file = dotbimpy.File("1.0.0", meshes=dotbim_meshes, elements=dotbim_elements, info={})

    dotbim_path = Path(dxf_filepath)
    dotbim_path = dotbim_path.with_name(dotbim_path.stem + "_export.bim")
    dotbim_file.save(str(dotbim_path))


if __name__ == "__main__":
    dxf_filepath = r"c:/path/to/file.dxf"
    dxf_to_dotbim(dxf_filepath)
