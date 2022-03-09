from pathlib import Path
import dotbimpy
import ezdxf


def dxf_to_dotbim(dxf_filepath):
    dxf_file = ezdxf.readfile(str(dxf_filepath))
    blocks = dxf_file.blocks

    dotbim_meshes = []
    dotbim_elements = []

    # file_info = {"Author": author, "Date": date.today().strftime("%d.%m.%Y")}
    dotbim_file = dotbimpy.File("1.0.0", meshes=dotbim_meshes, elements=dotbim_elements, info={})

    dotbim_path = Path(dxf_filepath)
    dotbim_path = dotbim_path.with_name(dotbim_path.stem + "_export.bim")
    dotbim_file.save(str(dotbim_path))


if __name__ == "__main__":
    dxf_filepath = r"c:/path/to/file.dxf"
    dxf_to_dotbim(dxf_filepath)
