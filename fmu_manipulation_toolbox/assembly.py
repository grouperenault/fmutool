import csv
import json
import logging
from typing import *
from pathlib import Path
import uuid
import xml.parsers.expat
import zipfile

from .fmu_container import FMUContainer, FMUContainerError

logger = logging.getLogger("fmu_manipulation_toolbox")


class Port:
    def __init__(self, fmu_name: str, port_name: str):
        self.fmu_name = fmu_name
        self.port_name = port_name

    def __hash__(self):
        return hash(f"{self.fmu_name}/{self.port_name}")

    def __eq__(self, other):
        return str(self) == str(other)


class Connection:
    def __init__(self, from_port: Port, to_port: Port):
        self.from_port = from_port
        self.to_port = to_port


class AssemblyNode:
    def __init__(self, name: str, step_size: float = None, mt=False, profiling=False,
                 auto_link=True, auto_input=True, auto_output=True):
        self.name = name
        self.step_size = step_size
        self.mt = mt
        self.profiling = profiling
        self.auto_link = auto_link
        self.auto_input = auto_input
        self.auto_output = auto_output
        self.children: List[AssemblyNode] = []

        self.fmu_names_list: Set[str] = set()
        self.input_ports: Dict[Port, str] = {}
        self.output_ports: Dict[Port, str] = {}
        self.start_values: Dict[Port, str] = {}
        self.drop_ports: List[Port] = []
        self.links: List[Connection] = []

    def add_sub_node(self, sub_node):
        if sub_node.name is None:
            sub_node.name = str(uuid.uuid4())+".fmu"

        self.fmu_names_list.add(sub_node.name)
        self.children.append(sub_node)

    def add_fmu(self, fmu_name: str):
        self.fmu_names_list.add(fmu_name)

    def add_input(self, from_port_name: str, to_fmu_filename: str, to_port_name: str):
        self.input_ports[Port(to_fmu_filename, to_port_name)] = from_port_name

    def add_output(self, from_fmu_filename: str, from_port_name: str, to_port_name: str):
        self.output_ports[Port(from_fmu_filename, from_port_name)] = to_port_name

    def add_drop_port(self, fmu_filename: str, port_name: str):
        self.drop_ports.append(Port(fmu_filename, port_name))

    def add_link(self, from_fmu_filename: str, from_port_name: str, to_fmu_filename: str, to_port_name: str):
        self.links.append(Connection(Port(from_fmu_filename, from_port_name),
                          Port(to_fmu_filename, to_port_name)))

    def add_start_value(self, fmu_filename: str, port_name: str, value: str):
        self.start_values[Port(fmu_filename, port_name)] = value

    def make_fmu(self, fmu_directory: Path, debug=False, description_pathname=None):
        for node in self.children:
            node.make_fmu(fmu_directory, debug=debug)

        container = FMUContainer(self.name, fmu_directory, description_pathname=description_pathname)

        for fmu_name in sorted(self.fmu_names_list):
            container.get_fmu(fmu_name)

        for port, source in self.input_ports.items():
            container.add_input(source, port.fmu_name, port.port_name)

        for port, target in self.output_ports.items():
            container.add_output(port.fmu_name, port.port_name, target)

        for link in self.links:
            container.add_link(link.from_port.fmu_name, link.from_port.port_name,
                               link.to_port.fmu_name, link.to_port.port_name)

        for drop in self.drop_ports:
            container.drop_port(drop.fmu_name, drop.port_name)

        for port, value in self.start_values.items():
            container.add_start_value(port.fmu_name, port.port_name, value)

        container.add_implicit_rule(auto_input=self.auto_input,
                                    auto_output=self.auto_output,
                                    auto_link=self.auto_link)

        container.make_fmu(self.name, self.step_size, mt=self.mt, profiling=self.profiling, debug=debug)

        for node in self.children:
            logger.info(f"Deleting transient FMU Container '{node.name}'")
            (fmu_directory / node.name).unlink()


class AssemblyError(Exception):
    def __init__(self, reason: str):
        self.reason = reason

    def __repr__(self):
        return f"{self.reason}"


class Assembly:
    def __init__(self, filename: str, step_size=None, auto_link=True,  auto_input=True, debug=False,
                 auto_output=True, mt=False, profiling=False, fmu_directory: Path = "."):
        self.filename = Path(filename)
        self.default_auto_input = auto_input
        self.debug = debug
        self.default_auto_output = auto_output
        self.default_step_size = step_size
        self.default_auto_link = auto_link
        self.default_mt = mt
        self.default_profiling = profiling
        self.fmu_directory = fmu_directory
        self.transient_filenames: List[Path] = []
        self.transient_dirnames: Set[Path] = set()

        if not fmu_directory.is_dir():
            raise FMUContainerError(f"FMU directory is not valid: '{fmu_directory}'")

        self.description_pathname = fmu_directory / self.filename  # For inclusion in FMU
        self.root = None
        self.read()

    def add_transient_file(self, filename: str):
        self.transient_filenames.append(self.fmu_directory / filename)
        self.transient_dirnames.add(Path(filename).parent)

    def __del__(self):
        if not self.debug:
            for filename in self.transient_filenames:
                try:
                    filename.unlink()
                except FileNotFoundError:
                    pass
            for dirname in self.transient_dirnames:
                while not str(dirname) == ".":
                    try:
                        (self.fmu_directory / dirname).rmdir()
                    except FileNotFoundError:
                        pass
                    dirname = dirname.parent

    def read(self):
        logger.info(f"Reading '{self.filename}'")
        if self.filename.suffix == ".json":
            self.read_json()
        elif self.filename.suffix == ".ssp":
            self.read_ssp()
        elif self.filename.suffix == ".csv":
            self.read_csv()
        else:
            raise FMUContainerError(f"Not supported file format '{self.filename}")

    def write(self, filename: str):
        if filename.endswith(".csv"):
            return self.write_csv(filename)
        elif filename.endswith(".json"):
            return self.write_json(filename)
        else:
            logger.critical(f"Unable to write to '{filename}': format unsupported.")

    def read_csv(self):
        name = str(self.filename.with_suffix(".fmu"))
        self.root = AssemblyNode(name, step_size=self.default_step_size, auto_link=self.default_auto_link,
                                 mt=self.default_mt, profiling=self.default_profiling,
                                 auto_input=self.default_auto_input, auto_output=self.default_auto_output)

        with open(self.description_pathname) as file:
            reader = csv.reader(file, delimiter=';')
            self.check_csv_headers(reader)
            for i, row in enumerate(reader):
                if not row or row[0][0] == '#':  # skip blank line of comment
                    continue

                try:
                    rule, from_fmu_filename, from_port_name, to_fmu_filename, to_port_name = row
                except ValueError:
                    logger.error(f"Line #{i+2}: expecting 5 columns. Line skipped.")
                    continue

                rule = rule.upper()
                if rule in ("LINK", "INPUT", "OUTPUT", "DROP", "FMU", "START"):
                    try:
                        self._read_csv_rule(self.root, rule,
                                            from_fmu_filename, from_port_name, to_fmu_filename, to_port_name)
                    except AssemblyError as e:
                        logger.error(f"Line #{i+2}: {e}. Line skipped.")
                        continue
                else:
                    logger.error(f"Line #{i+2}: unexpected rule '{rule}'. Line skipped.")

    def write_csv(self, filename: Union[str, Path]):
        if self.root.children:
            raise AssemblyError("This assembly is not flat. Cannot export to CSV file.")

        with open(self.fmu_directory / filename, "wt") as outfile:
            outfile.write("rule;from_fmu;from_port;to_fmu;to_port\n")
            for fmu in self.root.fmu_names_list:
                outfile.write(f"FMU;{fmu};;;\n")
            for port, source in self.root.input_ports.items():
                outfile.write(f"INPUT;;{source};{port.fmu_name};{port.port_name}\n")
            for port, target in self.root.output_ports.items():
                outfile.write(f"OUTPUT;{port.fmu_name};{port.port_name};;{target}\n")
            for link in self.root.links:
                outfile.write(f"LINK;{link.from_port.fmu_name};{link.from_port.port_name};"
                              f"{link.to_port.fmu_name};{link.to_port.port_name}\n")
            for port, value in self.root.start_values.items():
                outfile.write(f"START;{port.fmu_name};{port.port_name};{value};\n")
            for port in self.root.drop_ports:
                outfile.write(f"DROP;{port.fmu_name};{port.port_name};;\n")

    @staticmethod
    def _read_csv_rule(node: AssemblyNode, rule: str, from_fmu_filename: str, from_port_name: str,
                       to_fmu_filename: str, to_port_name: str):
        if rule == "FMU":
            if not from_fmu_filename:
                raise AssemblyError("Missing FMU information.")
            node.add_fmu(from_fmu_filename)

        elif rule == "INPUT":
            if not to_fmu_filename or not to_port_name:
                raise AssemblyError("Missing INPUT ports information.")
            if not from_port_name:
                from_port_name = to_port_name
            node.add_input(from_port_name, to_fmu_filename, to_port_name)

        elif rule == "OUTPUT":
            if not from_fmu_filename or not from_port_name:
                raise AssemblyError("Missing OUTPUT ports information.")
            if not to_port_name:
                to_port_name = from_port_name
            node.add_output(from_fmu_filename, from_port_name, to_port_name)

        elif rule == "DROP":
            if not from_fmu_filename or not from_port_name:
                raise AssemblyError("Missing DROP ports information.")
            node.add_drop_port(from_fmu_filename, from_port_name)

        elif rule == "LINK":
            node.add_link(from_fmu_filename, from_port_name, to_fmu_filename, to_port_name)

        elif rule == "START":
            if not from_fmu_filename or not from_port_name or not to_fmu_filename:
                raise AssemblyError("Missing START ports information.")

            node.add_start_value(from_fmu_filename, from_port_name, to_fmu_filename)
        # no else: check on rule is already done in read_description()

    @staticmethod
    def check_csv_headers(reader):
        headers = next(reader)
        if not headers == ["rule", "from_fmu", "from_port", "to_fmu", "to_port"]:
            raise AssemblyError("Header (1st line of the file) is not well formatted.")

    def read_json(self):
        with open(self.description_pathname) as file:
            try:
                data = json.load(file)
            except json.decoder.JSONDecodeError as e:
                raise FMUContainerError(f"Cannot read json: {e}")
        self.root = self.json_decode_node(data)
        if not self.root.name:
            self.root.name = str(self.filename.with_suffix(".fmu"))

    def write_json(self, filename: Union[str, Path]):
        with open(self.fmu_directory / filename, "wt") as file:
            data = self.json_encode_node(self.root)
            json.dump(data, file, indent=2)

    def json_encode_node(self, node: AssemblyNode) -> Dict[str, Any]:
        json_node = dict()
        json_node["name"] = node.name
        json_node["mt"] = node.mt
        json_node["profiling"] = node.profiling
        json_node["auto_link"] = node.auto_link
        if node.step_size:
            json_node["step_size"] = node.step_size

        if node.children:
            json_node["container"] = [self.json_encode_node(child) for child in node.children]

        if node.fmu_names_list:
            json_node["fmu"] = [f"{fmu_name}" for fmu_name in sorted(node.fmu_names_list)]

        if node.input_ports:
            json_node["input"] = [[f"{source}", f"{port.fmu_name}", f"{port.port_name}"]
                                  for port, source in node.input_ports.items()]

        if node.output_ports:
            json_node["output"] = [[f"{port.fmu_name}", f"{port.port_name}", f"{target}"]
                                   for port, target in node.output_ports.items()]

        if node.links:
            json_node["link"] = [[f"{link.from_port.fmu_name}", f"{link.from_port.port_name}",
                                  f"{link.to_port.fmu_name}", f"{link.to_port.port_name}"]
                                 for link in node.links]

        if node.start_values:
            json_node["start"] = [[f"{port.fmu_name}", f"{port.port_name}", value]
                                  for port, value in node.start_values.items()]

        if node.drop_ports:
            json_node["drop"] = [[f"{port.fmu_name}", f"{port.port_name}"] for port in node.drop_ports]

        return json_node

    def json_decode_node(self, data) -> AssemblyNode:
        name = data.get("name", None)
        step_size = data.get("step_size", self.default_step_size)
        auto_link = data.get("auto_link", self.default_auto_link)
        auto_input = data.get("auto_input", self.default_auto_input)
        auto_output = data.get("auto_output", self.default_auto_output)
        mt = data.get("mt", self.default_mt)
        profiling = data.get("profiling", self.default_profiling)

        node = AssemblyNode(name, step_size=step_size, auto_link=auto_link, mt=mt, profiling=profiling,
                            auto_input=auto_input, auto_output=auto_output)

        if "container" in data:
            if not isinstance(data["container"], list):
                raise FMUContainerError("JSON: 'container' keyword should define a list.")
            for sub_data in data["container"]:
                node.add_sub_node(self.json_decode_node(sub_data))

        if "fmu" in data:
            if not isinstance(data["fmu"], list):
                raise FMUContainerError("JSON: 'fmu' keyword should define a list.")
            for fmu in data["fmu"]:
                node.add_fmu(fmu)

        if "input" in data:
            if not isinstance(data["input"], list):
                raise FMUContainerError("JSON: 'input' keyword should define a list.")
            for line in data["input"]:
                node.add_input(line[1], line[2], line[0])

        if "output" in data:
            if not isinstance(data["output"], list):
                raise FMUContainerError("JSON: 'output' keyword should define a list.")
            for line in data["output"]:
                node.add_output(line[0], line[1], line[2])

        if "start" in data:
            if not isinstance(data["start"], list):
                raise FMUContainerError("JSON: 'start' keyword should define a list.")
            for line in data["start"]:
                node.add_start_value(line[0], line[1], line[2])

        if "drop" in data:
            for line in data["drop"]:
                node.add_drop_port(line[0], line[1])

        return node

    def read_ssp(self):
        logger.warning("This feature is ALPHA stage.")

        with zipfile.ZipFile(self.fmu_directory / self.filename) as zin:
            for file in zin.filelist:
                if file.filename.endswith(".fmu") or file.filename.endswith(".ssd"):
                    zin.extract(file, path=self.fmu_directory)
                    logger.debug(f"Extracted: {file.filename}")
                    self.add_transient_file(file.filename)

        self.description_pathname = self.fmu_directory / "SystemStructure.ssd"
        if self.description_pathname.is_file():
            sdd = SSDParser(step_size=self.default_step_size, auto_link=self.default_auto_link,
                            mt=self.default_mt, profiling=self.default_profiling,
                            auto_input=self.default_auto_input, auto_output=self.default_auto_output)
            self.root = sdd.parse(self.description_pathname)

    def make_fmu(self):
        self.root.make_fmu(self.fmu_directory, debug=self.debug, description_pathname=self.description_pathname)


class SSDParser:
    def __init__(self, **kwargs):
        self.node_stack: List[AssemblyNode] = []
        self.root = None
        self.fmu_filenames: Dict[str, str] = {}  # Component name => FMU filename
        self.node_attrs = kwargs

    def parse(self, ssd_filepath: Path) -> AssemblyNode:
        logger.debug(f"Analysing {ssd_filepath}")
        with open(ssd_filepath, "rb") as file:
            parser = xml.parsers.expat.ParserCreate()
            parser.StartElementHandler = self.start_element
            parser.EndElementHandler = self.end_element
            parser.ParseFile(file)

        return self.root

    def start_element(self, tag_name, attrs):
        if tag_name == 'ssd:Connection':
            if 'startElement' in attrs:
                if 'endElement' in attrs:
                    fmu_start = self.fmu_filenames[attrs['startElement']]
                    fmu_end = self.fmu_filenames[attrs['endElement']]
                    self.node_stack[-1].add_link(fmu_start, attrs['startConnector'],
                                                 fmu_end, attrs['endConnector'])
                else:
                    fmu_start = self.fmu_filenames[attrs['startElement']]
                    self.node_stack[-1].add_output(fmu_start, attrs['startConnector'],
                                                   attrs['endConnector'])
            else:
                fmu_end = self.fmu_filenames[attrs['endElement']]
                self.node_stack[-1].add_input(attrs['startConnector'],
                                              fmu_end, attrs['endConnector'])

        elif tag_name == 'ssd:System':
            logger.info(f"SSP System: {attrs['name']}")
            filename = attrs['name'] + ".fmu"
            self.fmu_filenames[attrs['name']] = filename
            node = AssemblyNode(filename, **self.node_attrs)
            if self.node_stack:
                self.node_stack[-1].add_sub_node(node)
            else:
                self.root = node

            self.node_stack.append(node)

        elif tag_name == 'ssd:Component':
            filename = attrs['source']
            name = attrs['name']
            self.fmu_filenames[name] = filename
            self.node_stack[-1].add_fmu(filename)
            logger.debug(f"Component {name} => {filename}")

    def end_element(self, tag_name):
        if tag_name == 'ssd:System':
            self.node_stack.pop()
