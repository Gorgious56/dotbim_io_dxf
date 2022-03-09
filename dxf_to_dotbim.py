from pathlib import Path
import dotbimpy
import ezdxf


def dxf_to_dotbim(dxf_filepath):
    dotbim_meshes = []
    dotbim_elements = []

    dxf_file = ezdxf.readfile(str(dxf_filepath))
    blocks = dxf_file.blocks
    for layout in blocks:
        if not layout.is_block_layout or layout.block.is_anonymous or layout.block.is_xref:
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
            dotbim_meshes.append(dotbimpy.Mesh(mesh_id=len(dotbim_meshes), coordinates=vertices, indices=faces))


    # file_info = {"Author": author, "Date": date.today().strftime("%d.%m.%Y")}
    dotbim_file = dotbimpy.File("1.0.0", meshes=dotbim_meshes, elements=dotbim_elements, info={})

    dotbim_path = Path(dxf_filepath)
    dotbim_path = dotbim_path.with_name(dotbim_path.stem + "_export.bim")
    dotbim_file.save(str(dotbim_path))


if __name__ == "__main__":
    dxf_filepath = r"c:/path/to/file.dxf"
    dxf_to_dotbim(dxf_filepath)
