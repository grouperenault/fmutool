import csv
import json
import logging
import os
from typing import *
from pathlib import Path
import uuid

from .fmu_container import FMUContainer

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
    def __init__(self, name: str, step_size:float = None, mt = False, profiling = False,
                 auto_link = True):
        self.name = name
        self.step_size = step_size
        self.mt = mt
        self.profiling = profiling
        self.auto_link = auto_link

        self.children: List[AssemblyNode] = []

        self.fmu_names_list: List[str] = []
        self.input_ports: Dict[Port, str] = {}
        self.output_ports: Dict[Port, str] = {}
        self.start_values: Dict[Port, str] = {}
        self.drop_ports: List[Port] = []
        self.links: List[Connection] = []

    def add_container(self, name: Union[None, str] = None, mt = False, profiling = False, auto_link = True):
        if name is None:
            name = str(uuid.uuid4())

        node = AssemblyNode(name, mt=mt, profiling=profiling, auto_link=auto_link)
        self.fmu_names_list.append(node.name)
        self.children.append(node)

    def add_fmu(self, fmu_name: str):
        self.fmu_names_list.append(fmu_name)

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

    def generate_fmu(self, fmu_directory: Path, auto_input=False, auto_output=False, debug=False):
        for node in self.children:
            node.generate_fmu(fmu_directory, debug=debug)

        container = FMUContainer(self.name, fmu_directory)
        logger.info(f"Building FMU Container from '{container.description_pathname}'")

        for fmu_name in self.fmu_names_list:
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


        container.add_implicit_rule(auto_input=auto_input,
                                    auto_output=auto_output,
                                    auto_link=self.auto_link)

        container.make_fmu(self.name, self.step_size, mt=self.mt, profiling=self.profiling, debug=debug)

        for node in self.children:
            logger.info(f"Deleting transient FMU Container '{node.name}'")
            os.remove(node.name)


class AssemblyError(Exception):
    def __init__(self, reason: str):
        self.reason = reason

    def __repr__(self):
        return f"{self.reason}"


class Assembly:
    def __init__(self, root: AssemblyNode, auto_input = True, auto_output = True, fmu_directory: str= "."):
        self.root = root
        self.auto_input = auto_input
        self.auto_output = auto_output
        self.fmu_directory = Path(fmu_directory)

    def write_csv(self, description_filename: Union[str, Path]):
        if self.root.children:
            raise AssemblyError("This assembly is not flat. Cannot export to CSV file.")

        with open(self.fmu_directory / description_filename, "wt") as outfile:
            print("rule;from_fmu;from_port;to_fmu;to_port", file=outfile)
            for fmu in self.root.fmu_names_list:
                print(f"FMU;{fmu};;;", file=outfile)
            for port, source in self.root.input_ports.items():
                print(f"INPUT;;{source};{port.fmu_name};{port.port_name}", file=outfile)
            for port, target in self.root.output_ports.items():
                print(f"OUTPUT;{port.fmu_name};{port.port_name};;{target}", file=outfile)
            for link in self.root.links:
                print(f"LINK;{link.from_port.fmu_name};{link.from_port.port_name};"
                      f"{link.to_port.fmu_name};{link.to_port.port_name}", file=outfile)
            for port, value in self.root.start_values.items():
                print(f"START;{port.fmu_name};{port.port_name};{value};", file=outfile)
            for port in self.root.drop_ports:
                print(f"DROP;{port.fmu_name};{port.port_name};;", file=outfile)

    def make_fmu(self, debug=False):
        self.root.generate_fmu(self.fmu_directory, auto_input=self.auto_input, auto_output=self.auto_output,
                               debug=debug)


class AssemblyCSV(Assembly):
    def __init__(self, csv_filename: str, auto_link: bool = True,  auto_input: bool = True, auto_output: bool = True,
                 mt: bool = False, profiling: bool = False, fmu_directory: str = "."):

        try:
            filename, step_size = str(csv_filename).split(":")
            step_size = float(step_size)
        except ValueError:
            step_size = None
            filename = csv_filename

        name = str(Path(filename).with_suffix(".fmu"))
        root = AssemblyNode(name, step_size=step_size, auto_link=auto_link, mt=mt, profiling=profiling)
        super().__init__(root, auto_input=auto_input, auto_output=auto_output, fmu_directory=fmu_directory)

        logger.info(f"Building FMU Container from '{csv_filename}'")

        with open(Path(fmu_directory) / csv_filename) as file:
            reader = csv.reader(file, delimiter=';')
            self.check_headers(reader)
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
                        self._read_csv_rule(root, rule,
                                            from_fmu_filename, from_port_name,
                                            to_fmu_filename, to_port_name)
                    except AssemblyError as e:
                        logger.error(f"Line #{i+2}: {e}. Line skipped.")
                        continue
                else:
                    logger.error(f"Line #{i+2}: unexpected rule '{rule}'. Line skipped.")

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
            node.add_input(from_port_name, to_fmu_filename, to_port_name)

        elif rule == "OUTPUT":
            if not from_fmu_filename or not from_port_name:
                raise AssemblyError("Missing OUTPUT ports information.")
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
    def check_headers(reader):
        headers = next(reader)
        if not headers == ["rule", "from_fmu", "from_port", "to_fmu", "to_port"]:
            raise AssemblyError("Header (1st line of the file) is not well formatted.")


class AssemblyJson(Assembly):
    pass


class AssemblySSP(Assembly):
    pass
