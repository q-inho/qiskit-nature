# This code is part of Qiskit.
#
# (C) Copyright IBM 2021, 2022.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""Tests Electronic Structure Problem."""
import unittest
from test import QiskitNatureTestCase
from test.second_q.problems.resources.resource_reader import (
    read_expected_file,
)

import numpy as np

import qiskit_nature.optionals as _optionals
from qiskit_nature.second_q.drivers import PySCFDriver
from qiskit_nature.second_q.operators import SecondQuantizedOp
from qiskit_nature.second_q.transformers import ActiveSpaceTransformer


class TestElectronicStructureProblem(QiskitNatureTestCase):
    """Tests Electronic Structure Problem."""

    @unittest.skipIf(not _optionals.HAS_PYSCF, "pyscf not available.")
    def test_second_q_ops_without_transformers(self):
        """Tests that the list of second quantized operators is created if no transformers
        provided."""
        expected_num_of_sec_quant_ops = 6
        expected_fermionic_op_path = self.get_resource_path(
            "H2_631g_ferm_op_two_ints",
            "second_q/problems/resources",
        )
        expected_fermionic_op = read_expected_file(expected_fermionic_op_path)

        driver = PySCFDriver(basis="631g")
        electronic_structure_problem = driver.run()

        electr_sec_quant_op, second_quantized_ops = electronic_structure_problem.second_q_ops()

        with self.subTest("Check expected length of the list of second quantized operators."):
            assert len(second_quantized_ops) == expected_num_of_sec_quant_ops
        with self.subTest("Check types in the list of second quantized operators."):
            for second_quantized_op in second_quantized_ops.values():
                assert isinstance(second_quantized_op, SecondQuantizedOp)
        with self.subTest("Check components of electronic second quantized operator."):
            assert all(
                s[0] == t[0] and np.isclose(np.abs(s[1]), np.abs(t[1]))
                for s, t in zip(expected_fermionic_op, electr_sec_quant_op.to_list())
            )

    @unittest.skipIf(not _optionals.HAS_PYSCF, "pyscf not available.")
    def test_second_q_ops_with_active_space(self):
        """Tests that the correct second quantized operator is created if an active space
        transformer is provided."""
        expected_num_of_sec_quant_ops = 6
        expected_fermionic_op_path = self.get_resource_path(
            "H2_631g_ferm_op_active_space",
            "second_q/problems/resources",
        )
        expected_fermionic_op = read_expected_file(expected_fermionic_op_path)
        driver = PySCFDriver(basis="631g")
        trafo = ActiveSpaceTransformer(num_electrons=2, num_molecular_orbitals=2)

        electronic_structure_problem = trafo.transform(driver.run())
        electr_sec_quant_op, second_quantized_ops = electronic_structure_problem.second_q_ops()

        with self.subTest("Check expected length of the list of second quantized operators."):
            assert len(second_quantized_ops) == expected_num_of_sec_quant_ops
        with self.subTest("Check types in the list of second quantized operators."):
            for second_quantized_op in second_quantized_ops.values():
                assert isinstance(second_quantized_op, SecondQuantizedOp)
        with self.subTest("Check components of electronic second quantized operator."):
            assert all(
                s[0] == t[0] and np.isclose(np.abs(s[1]), np.abs(t[1]))
                for s, t in zip(expected_fermionic_op, electr_sec_quant_op.to_list())
            )


if __name__ == "__main__":
    unittest.main()
