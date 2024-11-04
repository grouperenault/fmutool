import logging
import xml.parsers.expat
import zipfile
from pathlib import Path

logger = logging.getLogger("fmutool")


class SSP:
    def __init__(self, fmu_directory: Path, ssp_filename: Path):
        self.ssp_filename = ssp_filename
        self.analyse_ssp(fmu_directory)

    def analyse_ssp(self, fmu_directory: Path):
        with zipfile.ZipFile(self.ssp_filename) as zin:
            for file in zin.filelist:
                target_filename = Path(file.filename).name
                if file.filename.endswith(".fmu"):  # Extract all FMUs into the fmu_directory
                    zin.getinfo(file.filename).filename = target_filename
                    zin.extract(file, path=fmu_directory)
                #elif file.filename == "SystemStructure.ssd":
                elif file.filename.endswith(".ssd"):
                    zin.getinfo(file.filename).filename = target_filename
                    zin.extract(file, path=fmu_directory)
                    with zin.open(file) as file_handle:
                        self.analyse_ssd(file_handle, target_filename)
                    
    def analyse_ssd(self, file, filename):
        logger.info(f"Find {filename}")
        parser = xml.parsers.expat.ParserCreate()
        parser.StartElementHandler = self.start_element
        parser.EndElementHandler = self.end_element
        parser.CharacterDataHandler = self.char_data

        parser.ParseFile(file)


    def start_element(self, name, attrs):
        #logger.info(f"{name} {attrs}")
        pass

    def end_element(self, name):
        pass

    def char_data(self, data):
        pass

class SSD:
    class Component:
        pass
    class Unit:
        pass