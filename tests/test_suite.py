import unittest
import sys
import os

sys.path.insert(0, os.path.relpath(os.path.join(os.path.dirname(__file__), "..")))
from fmu_manipulation_toolbox.fmu_operations import *
from fmu_manipulation_toolbox.fmu_container import *
from fmu_manipulation_toolbox.assembly import *


class FMUManipulationToolboxTestSuite(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fmu_filename = "bouncing_ball.fmu"

    def assert_identical_files(self, filename1, filename2):
        with open(filename1, mode="rt", newline=None) as a, \
                open(filename2, mode="rt", newline=None) as b:
            self.assertTrue(all(lineA == lineB for lineA, lineB in zip(a, b)))

    def assert_names_match_ref(self, fmu_filename):
        fmu = FMU(fmu_filename)
        csv_filename = os.path.splitext(fmu_filename)[0] + ".csv"
        ref_filename = "REF-" + csv_filename
        operation = OperationSaveNamesToCSV(csv_filename)
        fmu.apply_operation(operation)
        self.assert_identical_files(ref_filename, csv_filename)

    def assert_operation_match_ref(self, fmu_filename, operation):
        fmu = FMU(self.fmu_filename)
        fmu.apply_operation(operation)
        fmu.repack(fmu_filename)
        self.assert_names_match_ref(fmu_filename)

    def test_strip_top_level(self):
        self.assert_operation_match_ref("bouncing_ball-no-tl.fmu", OperationStripTopLevel())

    def test_save_names_to_CSV(self):
        self.assert_names_match_ref("bouncing_ball.fmu")

    def test_rename_from_CSV(self):
        self.assert_operation_match_ref("bouncing_ball-renamed.fmu",
                                        OperationRenameFromCSV("bouncing_ball-modified.csv"))

    @unittest.skipUnless(sys.platform.startswith("win"), "Supported only on Windows")
    def test_add_remoting_win32(self):
        fmu = FMU(self.fmu_filename)
        operation = OperationAddRemotingWin32()
        fmu.apply_operation(operation)
        fmu.repack("bouncing_ball-win32.fmu")

    def test_remove_regexp(self):
        self.assert_operation_match_ref("bouncing_ball-removed.fmu",
                                        OperationRemoveRegexp("e"))

    def test_keep_only_regexp(self):
        self.assert_operation_match_ref("bouncing_ball-keeponly.fmu",
                                        OperationKeepOnlyRegexp("e"))

    def test_container(self):
        assembly = AssemblyCSV(Path("bouncing.csv"), fmu_directory="containers/bouncing_ball", mt=True)
        assembly.make_fmu(debug=True)
        self.assert_identical_files("containers/bouncing_ball/REF_container.txt",
                                    "containers/bouncing_ball/bouncing/resources/container.txt")


if __name__ == '__main__':
    unittest.main()
