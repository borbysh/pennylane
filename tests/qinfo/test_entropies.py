# Copyright 2022 Xanadu Quantum Technologies Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Unit tests for differentiable quantum entropies.
"""
# pylint: disable=too-many-arguments
import pytest

import pennylane as qml
from pennylane import numpy as np

pytestmark = [
    pytest.mark.filterwarnings(
        r"ignore:The qml\.qinfo\.(vn_entropy|mutual_info|reduced_dm) transform:pennylane.PennyLaneDeprecationWarning"
    ),
    pytest.mark.filterwarnings(
        "ignore:qml.qinfo.relative_entropy is deprecated:pennylane.PennyLaneDeprecationWarning"
    ),
]


def expected_entropy_ising_xx(param):
    """
    Return the analytical entropy for the IsingXX.
    """
    eigs = [np.cos(param / 2) ** 2, np.sin(param / 2) ** 2]
    eigs = [eig for eig in eigs if eig > 0]

    expected_entropy = eigs * np.log(eigs)

    expected_entropy = -np.sum(expected_entropy)
    return expected_entropy


def expected_entropy_grad_ising_xx(param):
    """
    Return the analytical gradient entropy for the IsingXX.
    """
    eig_1 = (1 + np.sqrt(1 - 4 * np.cos(param / 2) ** 2 * np.sin(param / 2) ** 2)) / 2
    eig_2 = (1 - np.sqrt(1 - 4 * np.cos(param / 2) ** 2 * np.sin(param / 2) ** 2)) / 2
    eigs = [eig_1, eig_2]
    eigs = np.maximum(eigs, 1e-08)

    grad_expected_entropy = -(
        (np.log(eigs[0]) + 1)
        * (np.sin(param / 2) ** 3 * np.cos(param / 2) - np.sin(param / 2) * np.cos(param / 2) ** 3)
        / np.sqrt(1 - 4 * np.cos(param / 2) ** 2 * np.sin(param / 2) ** 2)
    ) - (
        (np.log(eigs[1]) + 1)
        * (
            np.sin(param / 2)
            * np.cos(param / 2)
            * (np.cos(param / 2) ** 2 - np.sin(param / 2) ** 2)
        )
        / np.sqrt(1 - 4 * np.cos(param / 2) ** 2 * np.sin(param / 2) ** 2)
    )
    return grad_expected_entropy


class TestVonNeumannEntropy:
    """Tests Von Neumann entropy transform"""

    single_wires_list = [[0], [1]]

    base = [2, np.exp(1), 10]

    check_state = [True, False]

    parameters = np.linspace(0, 2 * np.pi, 10)
    devices = ["default.qubit", "default.mixed", "lightning.qubit"]

    def test_qinfo_vn_entropy_deprecated(self):
        """Test that qinfo.vn_entropy is deprecated."""

        dev = qml.device("default.qubit", wires=2)

        @qml.qnode(dev)
        def circuit():
            return qml.state()

        with pytest.warns(
            qml.PennyLaneDeprecationWarning,
            match="The qml.qinfo.vn_entropy transform is deprecated",
        ):
            _ = qml.qinfo.vn_entropy(circuit, [0])()

    def test_vn_entropy_cannot_specify_device(self):
        """Test that an error is raised if a device or device wires are given
        to the vn_entropy transform manually."""
        dev = qml.device("default.qubit", wires=2)

        @qml.qnode(dev)
        def circuit(params):
            qml.RY(params, wires=0)
            qml.CNOT(wires=[0, 1])
            return qml.state()

        with pytest.raises(ValueError, match="Cannot provide a 'device' value"):
            _ = qml.qinfo.vn_entropy(circuit, wires=[0], device=dev)

        with pytest.raises(ValueError, match="Cannot provide a 'device_wires' value"):
            _ = qml.qinfo.vn_entropy(circuit, wires=[0], device_wires=dev.wires)

    @pytest.mark.parametrize("wires", single_wires_list)
    @pytest.mark.parametrize("param", parameters)
    @pytest.mark.parametrize("device", devices)
    @pytest.mark.parametrize("base", base)
    def test_IsingXX_qnode_entropy(self, param, wires, device, base):
        """Test entropy for a QNode numpy."""

        dev = qml.device(device, wires=2)

        @qml.qnode(dev)
        def circuit_state(x):
            qml.IsingXX(x, wires=[0, 1])
            return qml.state()

        entropy = qml.qinfo.vn_entropy(circuit_state, wires=wires, base=base)(param)
        expected_entropy = expected_entropy_ising_xx(param) / np.log(base)
        assert qml.math.allclose(entropy, expected_entropy)

    interfaces = ["auto", "autograd"]

    @pytest.mark.autograd
    @pytest.mark.parametrize("wires", single_wires_list)
    @pytest.mark.parametrize("param", parameters)
    @pytest.mark.parametrize("base", base)
    @pytest.mark.parametrize("interface", interfaces)
    def test_IsingXX_qnode_entropy_grad(self, param, wires, base, interface):
        """Test entropy for a QNode gradient with autograd."""

        dev = qml.device("default.qubit", wires=2)

        @qml.qnode(dev, interface=interface)
        def circuit_state(x):
            qml.IsingXX(x, wires=[0, 1])
            return qml.state()

        grad_entropy = qml.grad(qml.qinfo.vn_entropy(circuit_state, wires=wires, base=base))(param)
        grad_expected_entropy = expected_entropy_grad_ising_xx(param) / np.log(base)
        assert qml.math.allclose(grad_entropy, grad_expected_entropy)

    interfaces = ["torch"]

    @pytest.mark.torch
    @pytest.mark.parametrize("wires", single_wires_list)
    @pytest.mark.parametrize("param", parameters)
    @pytest.mark.parametrize("device", devices)
    @pytest.mark.parametrize("base", base)
    @pytest.mark.parametrize("interface", interfaces)
    def test_IsingXX_qnode_torch_entropy(self, param, wires, device, base, interface):
        """Test entropy for a QNode with torch interface."""
        import torch

        dev = qml.device(device, wires=2)

        @qml.qnode(dev, interface=interface)
        def circuit_state(x):
            qml.IsingXX(x, wires=[0, 1])
            return qml.state()

        entropy = qml.qinfo.vn_entropy(circuit_state, wires=wires, base=base)(torch.tensor(param))
        expected_entropy = expected_entropy_ising_xx(param) / np.log(base)
        assert qml.math.allclose(entropy, expected_entropy)

    @pytest.mark.torch
    @pytest.mark.parametrize("wires", single_wires_list)
    @pytest.mark.parametrize("param", parameters)
    @pytest.mark.parametrize("base", base)
    @pytest.mark.parametrize("interface", interfaces)
    def test_IsingXX_qnode_entropy_grad_torch(self, param, wires, base, interface):
        """Test entropy for a QNode gradient with torch."""
        import torch

        dev = qml.device("default.qubit", wires=2)

        @qml.qnode(dev, interface=interface, diff_method="backprop")
        def circuit_state(x):
            qml.IsingXX(x, wires=[0, 1])
            return qml.state()

        eig_1 = (1 + np.sqrt(1 - 4 * np.cos(param / 2) ** 2 * np.sin(param / 2) ** 2)) / 2
        eig_2 = (1 - np.sqrt(1 - 4 * np.cos(param / 2) ** 2 * np.sin(param / 2) ** 2)) / 2
        eigs = [eig_1, eig_2]
        eigs = np.maximum(eigs, 1e-08)

        grad_expected_entropy = expected_entropy_grad_ising_xx(param) / np.log(base)

        param = torch.tensor(param, dtype=torch.float64, requires_grad=True)

        entropy = qml.qinfo.vn_entropy(circuit_state, wires=wires, base=base)(param)
        entropy.backward()
        grad_entropy = param.grad

        assert qml.math.allclose(grad_entropy, grad_expected_entropy)

    interfaces = ["tf"]

    @pytest.mark.tf
    @pytest.mark.parametrize("wires", single_wires_list)
    @pytest.mark.parametrize("param", parameters)
    @pytest.mark.parametrize("device", devices)
    @pytest.mark.parametrize("base", base)
    @pytest.mark.parametrize("interface", interfaces)
    def test_IsingXX_qnode_tf_entropy(self, param, wires, device, base, interface):
        """Test entropy for a QNode with tf interface."""
        import tensorflow as tf

        dev = qml.device(device, wires=2)

        @qml.qnode(dev, interface=interface)
        def circuit_state(x):
            qml.IsingXX(x, wires=[0, 1])
            return qml.state()

        entropy = qml.qinfo.vn_entropy(circuit_state, wires=wires, base=base)(tf.Variable(param))
        expected_entropy = expected_entropy_ising_xx(param) / np.log(base)

        assert qml.math.allclose(entropy, expected_entropy)

    @pytest.mark.tf
    @pytest.mark.parametrize("wires", single_wires_list)
    @pytest.mark.parametrize("param", parameters)
    @pytest.mark.parametrize("base", base)
    @pytest.mark.parametrize("interface", interfaces)
    def test_IsingXX_qnode_entropy_grad_tf(self, param, wires, base, interface):
        """Test entropy for a QNode gradient with tf."""
        import tensorflow as tf

        dev = qml.device("default.qubit", wires=2)

        @qml.qnode(dev, interface=interface, diff_method="backprop")
        def circuit_state(x):
            qml.IsingXX(x, wires=[0, 1])
            return qml.state()

        param = tf.Variable(param)
        with tf.GradientTape() as tape:
            entropy = qml.qinfo.vn_entropy(circuit_state, wires=wires, base=base)(param)

        grad_entropy = tape.gradient(entropy, param)
        grad_expected_entropy = expected_entropy_grad_ising_xx(param) / np.log(base)

        assert qml.math.allclose(grad_entropy, grad_expected_entropy)

    interfaces = ["jax"]

    @pytest.mark.jax
    @pytest.mark.parametrize("wires", single_wires_list)
    @pytest.mark.parametrize("param", parameters)
    @pytest.mark.parametrize("device", devices)
    @pytest.mark.parametrize("base", base)
    @pytest.mark.parametrize("interface", interfaces)
    def test_IsingXX_qnode_jax_entropy(self, param, wires, device, base, interface):
        """Test entropy for a QNode with jax interface."""
        import jax.numpy as jnp

        dev = qml.device(device, wires=2)

        @qml.qnode(dev, interface=interface)
        def circuit_state(x):
            qml.IsingXX(x, wires=[0, 1])
            return qml.state()

        entropy = qml.qinfo.vn_entropy(circuit_state, wires=wires, base=base)(jnp.array(param))
        expected_entropy = expected_entropy_ising_xx(param) / np.log(base)

        assert qml.math.allclose(entropy, expected_entropy)

    @pytest.mark.jax
    @pytest.mark.parametrize("wires", single_wires_list)
    @pytest.mark.parametrize("param", parameters)
    @pytest.mark.parametrize("base", base)
    @pytest.mark.parametrize("interface", interfaces)
    def test_IsingXX_qnode_entropy_grad_jax(self, param, wires, base, interface):
        """Test entropy for a QNode gradient with Jax."""
        import jax

        dev = qml.device("default.qubit", wires=2)

        @qml.qnode(dev, interface=interface, diff_method="backprop")
        def circuit_state(x):
            qml.IsingXX(x, wires=[0, 1])
            return qml.state()

        grad_entropy = jax.grad(qml.qinfo.vn_entropy(circuit_state, wires=wires, base=base))(
            jax.numpy.array(param)
        )
        grad_expected_entropy = expected_entropy_grad_ising_xx(param) / np.log(base)

        assert qml.math.allclose(grad_entropy, grad_expected_entropy, rtol=1e-04, atol=1e-05)

    interfaces = ["jax-jit"]

    @pytest.mark.jax
    @pytest.mark.parametrize("wires", single_wires_list)
    @pytest.mark.parametrize("param", parameters)
    @pytest.mark.parametrize("base", base)
    @pytest.mark.parametrize("interface", interfaces)
    def test_IsingXX_qnode_jax_jit_entropy(self, param, wires, base, interface):
        """Test entropy for a QNode with jax-jit interface."""
        import jax
        import jax.numpy as jnp

        dev = qml.device("default.qubit", wires=2)

        @qml.qnode(dev, interface=interface)
        def circuit_state(x):
            qml.IsingXX(x, wires=[0, 1])
            return qml.state()

        entropy = jax.jit(qml.qinfo.vn_entropy(circuit_state, wires=wires, base=base))(
            jnp.array(param)
        )
        expected_entropy = expected_entropy_ising_xx(param) / np.log(base)

        assert qml.math.allclose(entropy, expected_entropy)

    @pytest.mark.jax
    @pytest.mark.parametrize("wires", single_wires_list)
    @pytest.mark.parametrize("param", parameters)
    @pytest.mark.parametrize("base", base)
    @pytest.mark.parametrize("interface", interfaces)
    def test_IsingXX_qnode_entropy_grad_jax_jit(self, param, wires, base, interface):
        """Test entropy for a QNode gradient with Jax-jit."""
        import jax

        dev = qml.device("default.qubit", wires=2)

        @qml.qnode(dev, interface=interface, diff_method="backprop")
        def circuit_state(x):
            qml.IsingXX(x, wires=[0, 1])
            return qml.state()

        grad_entropy = jax.jit(
            jax.grad(qml.qinfo.vn_entropy(circuit_state, wires=wires, base=base))
        )(jax.numpy.array(param))
        grad_expected_entropy = expected_entropy_grad_ising_xx(param) / np.log(base)

        assert qml.math.allclose(grad_entropy, grad_expected_entropy, rtol=1e-04, atol=1e-05)

    def test_qnode_entropy_wires_full_range_not_state(self):
        """Test entropy needs a QNode returning state."""
        param = 0.1
        dev = qml.device("default.qubit", wires=2)

        @qml.qnode(dev)
        def circuit_state(x):
            qml.IsingXX(x, wires=[0, 1])
            return qml.expval(qml.PauliX(wires=0))

        with pytest.raises(
            ValueError,
            match="The qfunc return type needs to be a state.",
        ):
            qml.qinfo.vn_entropy(circuit_state, wires=[0, 1])(param)

    def test_qnode_entropy_wires_full_range_state_vector(self):
        """Test entropy for a QNode that returns a state vector with all wires, entropy is 0."""
        param = 0.1
        dev = qml.device("default.qubit", wires=2)

        @qml.qnode(dev)
        def circuit_state(x):
            qml.IsingXX(x, wires=[0, 1])
            return qml.state()

        entropy = qml.qinfo.vn_entropy(circuit_state, wires=[0, 1])(param)
        expected_entropy = 0.0
        assert qml.math.allclose(entropy, expected_entropy)

    def test_qnode_entropy_wires_full_range_density_mat(self):
        """Test entropy for a QNode that returns a density mat with all wires, entropy is 0."""
        param = 0.1
        dev = qml.device("default.mixed", wires=2)

        @qml.qnode(dev)
        def circuit_state(x):
            qml.IsingXX(x, wires=[0, 1])
            return qml.state()

        entropy = qml.qinfo.vn_entropy(circuit_state, wires=[0, 1])(param)
        expected_entropy = 0.0
        assert qml.math.allclose(entropy, expected_entropy)

    @pytest.mark.parametrize("device", devices)
    def test_entropy_wire_labels(self, device, tol):
        """Test that vn_entropy is correct with custom wire labels"""
        param = np.array(1.234)
        wires = ["a", 8]
        dev = qml.device(device, wires=wires)

        @qml.qnode(dev)
        def circuit(x):
            qml.PauliX(wires=wires[0])
            qml.IsingXX(x, wires=wires)
            return qml.state()

        entropy0 = qml.qinfo.vn_entropy(circuit, wires=[wires[0]])(param)

        eigs0 = [np.sin(param / 2) ** 2, np.cos(param / 2) ** 2]
        exp0 = -np.sum(eigs0 * np.log(eigs0))

        entropy1 = qml.qinfo.vn_entropy(circuit, wires=[wires[1]])(param)

        eigs1 = [np.cos(param / 2) ** 2, np.sin(param / 2) ** 2]
        exp1 = -np.sum(eigs1 * np.log(eigs1))

        assert np.allclose(exp0, entropy0, atol=tol)
        assert np.allclose(exp1, entropy1, atol=tol)


class TestRelativeEntropy:
    """Tests for the relative entropy information functions"""

    diff_methods = ["backprop", "finite-diff"]

    params = [[0.0, 0.0], [np.pi, 0.0], [0.0, np.pi], [0.123, 0.456], [0.789, 1.618]]

    # to avoid nan values in the gradient for relative entropy
    grad_params = [[0.123, 0.456], [0.789, 1.618]]

    def test_qinfo_relative_entropy_deprecated(self):
        """Test that qinfo.relative_entropy is deprecated."""

        dev = qml.device("default.qubit", wires=2)

        @qml.qnode(dev)
        def circuit(param):
            qml.RY(param, wires=0)
            qml.CNOT(wires=[0, 1])
            return qml.state()

        x, y = 0.4, 0.6

        with pytest.warns(
            qml.PennyLaneDeprecationWarning,
            match="qml.qinfo.relative_entropy is deprecated",
        ):
            _ = qml.qinfo.relative_entropy(circuit, circuit, wires0=[0], wires1=[0])((x,), (y,))

    @pytest.mark.all_interfaces
    @pytest.mark.parametrize("device", ["default.qubit", "default.mixed", "lightning.qubit"])
    @pytest.mark.parametrize("interface", ["autograd", "jax", "tensorflow", "torch"])
    @pytest.mark.parametrize("param", params)
    def test_qnode_relative_entropy(self, device, interface, param):
        """Test that the relative entropy transform works for QNodes by comparing
        against analytic values"""
        dev = qml.device(device, wires=2)

        param = qml.math.asarray(np.array(param), like=interface)

        @qml.qnode(dev, interface=interface)
        def circuit1(param):
            qml.RY(param, wires=0)
            qml.CNOT(wires=[0, 1])
            return qml.state()

        @qml.qnode(dev, interface=interface)
        def circuit2(param):
            qml.RY(param, wires=0)
            qml.CNOT(wires=[0, 1])
            return qml.state()

        rel_ent_circuit = qml.qinfo.relative_entropy(circuit1, circuit2, [0], [1])
        actual = rel_ent_circuit((param[0],), (param[1],))

        # compare transform results with analytic results
        first_term = (
            0
            if np.cos(param[0] / 2) == 0
            else np.cos(param[0] / 2) ** 2
            * (np.log(np.cos(param[0] / 2) ** 2) - np.log(np.cos(param[1] / 2) ** 2))
        )
        second_term = (
            0
            if np.sin(param[0] / 2) == 0
            else np.sin(param[0] / 2) ** 2
            * (np.log(np.sin(param[0] / 2) ** 2) - np.log(np.sin(param[1] / 2) ** 2))
        )
        expected = first_term + second_term

        assert np.allclose(actual, expected)

    interfaces = ["jax-jit"]

    @pytest.mark.jax
    @pytest.mark.parametrize("param", params)
    @pytest.mark.parametrize("interface", interfaces)
    def test_qnode_relative_entropy_jax_jit(self, param, interface):
        """Test that the relative entropy transform works for QNodes by comparing
        against analytic values, for the JAX-jit interface"""
        import jax
        import jax.numpy as jnp

        dev = qml.device("default.qubit", wires=2)

        param = jnp.array(param)

        @qml.qnode(dev, interface=interface)
        def circuit1(params):
            qml.RY(params, wires=0)
            qml.CNOT(wires=[0, 1])
            return qml.state()

        @qml.qnode(dev, interface=interface)
        def circuit2(params):
            qml.RY(params, wires=0)
            qml.CNOT(wires=[0, 1])
            return qml.state()

        rel_ent_circuit = qml.qinfo.relative_entropy(circuit1, circuit2, [0], [1])
        actual = jax.jit(rel_ent_circuit)((param[0],), (param[1],))

        # compare transform results with analytic results
        first_term = (
            0
            if jnp.cos(param[0] / 2) == 0
            else jnp.cos(param[0] / 2) ** 2
            * (jnp.log(jnp.cos(param[0] / 2) ** 2) - jnp.log(jnp.cos(param[1] / 2) ** 2))
        )
        second_term = (
            0
            if jnp.sin(param[0] / 2) == 0
            else jnp.sin(param[0] / 2) ** 2
            * (jnp.log(jnp.sin(param[0] / 2) ** 2) - jnp.log(jnp.sin(param[1] / 2) ** 2))
        )
        expected = first_term + second_term

        assert np.allclose(actual, expected)

    @pytest.mark.jax
    @pytest.mark.parametrize("param", grad_params)
    @pytest.mark.parametrize("interface", interfaces)
    def test_qnode_grad_jax(self, param, interface):
        """Test that the gradient of relative entropy works for QNodes
        with the JAX interface"""
        import jax
        import jax.numpy as jnp

        dev = qml.device("default.qubit", wires=2)

        @qml.qnode(dev, interface=interface, diff_method="backprop")
        def circuit1(param):
            qml.RY(param, wires=0)
            qml.CNOT(wires=[0, 1])
            return qml.state()

        @qml.qnode(dev, interface=interface, diff_method="backprop")
        def circuit2(param):
            qml.RY(param, wires=0)
            qml.CNOT(wires=[0, 1])
            return qml.state()

        rel_ent_circuit = qml.qinfo.relative_entropy(circuit1, circuit2, [0], [1])

        def wrapper(param0, param1):
            return rel_ent_circuit((param0,), (param1,))

        expected = [
            np.sin(param[0] / 2)
            * np.cos(param[0] / 2)
            * (np.log(np.tan(param[0] / 2) ** 2) - np.log(np.tan(param[1] / 2) ** 2)),
            np.cos(param[0] / 2) ** 2 * np.tan(param[1] / 2)
            - np.sin(param[0] / 2) ** 2 / np.tan(param[1] / 2),
        ]

        param0, param1 = jnp.array(param[0]), jnp.array(param[1])
        actual = jax.grad(wrapper, argnums=[0, 1])(param0, param1)

        assert np.allclose(actual, expected, atol=1e-8)

    @pytest.mark.jax
    @pytest.mark.parametrize("param", grad_params)
    @pytest.mark.parametrize("interface", interfaces)
    def test_qnode_grad_jax_jit(self, param, interface):
        """Test that the gradient of relative entropy works for QNodes
        with the JAX interface"""
        import jax
        import jax.numpy as jnp

        dev = qml.device("default.qubit", wires=2)

        @qml.qnode(dev, interface=interface, diff_method="backprop")
        def circuit1(param):
            qml.RY(param, wires=0)
            qml.CNOT(wires=[0, 1])
            return qml.state()

        @qml.qnode(dev, interface=interface, diff_method="backprop")
        def circuit2(param):
            qml.RY(param, wires=0)
            qml.CNOT(wires=[0, 1])
            return qml.state()

        rel_ent_circuit = qml.qinfo.relative_entropy(circuit1, circuit2, [0], [1])

        def wrapper(param0, param1):
            return rel_ent_circuit((param0,), (param1,))

        expected = [
            np.sin(param[0] / 2)
            * np.cos(param[0] / 2)
            * (np.log(np.tan(param[0] / 2) ** 2) - np.log(np.tan(param[1] / 2) ** 2)),
            np.cos(param[0] / 2) ** 2 * np.tan(param[1] / 2)
            - np.sin(param[0] / 2) ** 2 / np.tan(param[1] / 2),
        ]

        param0, param1 = jnp.array(param[0]), jnp.array(param[1])
        actual = jax.jit(jax.grad(wrapper, argnums=[0, 1]))(param0, param1)

        assert np.allclose(actual, expected, atol=1e-8)

    interfaces = ["auto", "autograd"]

    @pytest.mark.autograd
    @pytest.mark.parametrize("param", grad_params)
    @pytest.mark.parametrize("interface", interfaces)
    def test_qnode_grad(self, param, interface):
        """Test that the gradient of relative entropy works for QNodes
        with the autograd interface"""
        dev = qml.device("default.qubit", wires=2)

        @qml.qnode(dev, interface=interface, diff_method="backprop")
        def circuit1(param):
            qml.RY(param, wires=0)
            qml.CNOT(wires=[0, 1])
            return qml.state()

        @qml.qnode(dev, interface=interface, diff_method="backprop")
        def circuit2(param):
            qml.RY(param, wires=0)
            qml.CNOT(wires=[0, 1])
            return qml.state()

        rel_ent_circuit = qml.qinfo.relative_entropy(circuit1, circuit2, [0], [1])

        def wrapper(param0, param1):
            return rel_ent_circuit((param0,), (param1,))

        expected = [
            np.sin(param[0] / 2)
            * np.cos(param[0] / 2)
            * (np.log(np.tan(param[0] / 2) ** 2) - np.log(np.tan(param[1] / 2) ** 2)),
            np.cos(param[0] / 2) ** 2 * np.tan(param[1] / 2)
            - np.sin(param[0] / 2) ** 2 / np.tan(param[1] / 2),
        ]

        param0, param1 = np.array(param[0]), np.array(param[1])
        actual = qml.grad(wrapper)(param0, param1)

        assert np.allclose(actual, expected, atol=1e-8)

    interfaces = ["tf"]

    @pytest.mark.tf
    @pytest.mark.parametrize("param", grad_params)
    @pytest.mark.parametrize("interface", interfaces)
    def test_qnode_grad_tf(self, param, interface):
        """Test that the gradient of relative entropy works for QNodes
        with the TensorFlow interface"""
        import tensorflow as tf

        dev = qml.device("default.qubit", wires=2)

        @qml.qnode(dev, interface=interface, diff_method="backprop")
        def circuit1(param):
            qml.RY(param, wires=0)
            qml.CNOT(wires=[0, 1])
            return qml.state()

        @qml.qnode(dev, interface=interface, diff_method="backprop")
        def circuit2(param):
            qml.RY(param, wires=0)
            qml.CNOT(wires=[0, 1])
            return qml.state()

        expected = [
            np.sin(param[0] / 2)
            * np.cos(param[0] / 2)
            * (np.log(np.tan(param[0] / 2) ** 2) - np.log(np.tan(param[1] / 2) ** 2)),
            np.cos(param[0] / 2) ** 2 * np.tan(param[1] / 2)
            - np.sin(param[0] / 2) ** 2 / np.tan(param[1] / 2),
        ]

        param0, param1 = tf.Variable(param[0]), tf.Variable(param[1])

        with tf.GradientTape() as tape:
            out = qml.qinfo.relative_entropy(circuit1, circuit2, [0], [1])((param0,), (param1,))

        actual = tape.gradient(out, [param0, param1])

        assert np.allclose(actual, expected, atol=1e-5)

    interfaces = ["torch"]

    @pytest.mark.torch
    @pytest.mark.parametrize("param", grad_params)
    @pytest.mark.parametrize("interface", interfaces)
    def test_qnode_grad_torch(self, param, interface):
        """Test that the gradient of relative entropy works for QNodes
        with the Torch interface"""
        import torch

        dev = qml.device("default.qubit", wires=2)

        @qml.qnode(dev, interface=interface, diff_method="backprop")
        def circuit1(param):
            qml.RY(param, wires=0)
            qml.CNOT(wires=[0, 1])
            return qml.state()

        @qml.qnode(dev, interface=interface, diff_method="backprop")
        def circuit2(param):
            qml.RY(param, wires=0)
            qml.CNOT(wires=[0, 1])
            return qml.state()

        expected = [
            np.sin(param[0] / 2)
            * np.cos(param[0] / 2)
            * (np.log(np.tan(param[0] / 2) ** 2) - np.log(np.tan(param[1] / 2) ** 2)),
            np.cos(param[0] / 2) ** 2 * np.tan(param[1] / 2)
            - np.sin(param[0] / 2) ** 2 / np.tan(param[1] / 2),
        ]

        param0 = torch.tensor(param[0], requires_grad=True)
        param1 = torch.tensor(param[1], requires_grad=True)

        out = qml.qinfo.relative_entropy(circuit1, circuit2, [0], [1])((param0,), (param1,))
        out.backward()
        actual = [param0.grad, param1.grad]

        assert np.allclose(actual, expected, atol=1e-8)

    @pytest.mark.all_interfaces
    @pytest.mark.parametrize("device", ["default.qubit", "default.mixed", "lightning.qubit"])
    @pytest.mark.parametrize("interface", ["autograd", "jax", "tensorflow", "torch"])
    def test_num_wires_mismatch(self, device, interface):
        """Test that an error is raised when the number of wires in the
        two QNodes are different"""
        dev = qml.device(device, wires=2)

        @qml.qnode(dev, interface=interface)
        def circuit1(param):
            qml.RY(param, wires=0)
            qml.CNOT(wires=[0, 1])
            return qml.state()

        @qml.qnode(dev, interface=interface)
        def circuit2(param):
            qml.RY(param, wires=0)
            qml.CNOT(wires=[0, 1])
            return qml.state()

        msg = "The two states must have the same number of wires"
        with pytest.raises(qml.QuantumFunctionError, match=msg):
            qml.qinfo.relative_entropy(circuit1, circuit2, [0], [0, 1])

    @pytest.mark.parametrize("device", ["default.qubit", "default.mixed", "lightning.qubit"])
    def test_full_wires(self, device):
        """Test that the relative entropy transform for full wires works for QNodes"""
        dev = qml.device(device, wires=1)

        @qml.qnode(dev)
        def circuit1(param):
            qml.RY(param, wires=0)
            return qml.state()

        @qml.qnode(dev)
        def circuit2(param):
            qml.RY(param, wires=0)
            return qml.state()

        rel_ent_circuit = qml.qinfo.relative_entropy(circuit1, circuit2, [0], [0])
        x, y = np.array(0.3), np.array(0.7)

        # test that the circuit executes
        rel_ent_circuit(x, y)

    @pytest.mark.parametrize("device", ["default.qubit", "default.mixed", "lightning.qubit"])
    def test_qnode_no_args(self, device):
        """Test that the relative entropy transform works for QNodes without arguments"""
        dev = qml.device(device, wires=2)

        @qml.qnode(dev)
        def circuit1():
            qml.PauliY(wires=0)
            qml.CNOT(wires=[0, 1])
            return qml.state()

        @qml.qnode(dev)
        def circuit2():
            qml.PauliZ(wires=0)
            qml.CNOT(wires=[0, 1])
            return qml.state()

        rel_ent_circuit = qml.qinfo.relative_entropy(circuit1, circuit2, [0], [1])

        # test that the circuit executes
        rel_ent_circuit()

    @pytest.mark.parametrize("device", ["default.qubit", "default.mixed", "lightning.qubit"])
    def test_qnode_kwargs(self, device):
        """Test that the relative entropy transform works for QNodes that take keyword arguments"""
        dev = qml.device(device, wires=2)

        @qml.qnode(dev)
        def circuit1(param=0):
            qml.RY(param, wires=0)
            qml.CNOT(wires=[0, 1])
            return qml.state()

        @qml.qnode(dev)
        def circuit2(param=0):
            qml.RY(param, wires=0)
            qml.CNOT(wires=[0, 1])
            return qml.state()

        rel_ent_circuit = qml.qinfo.relative_entropy(circuit1, circuit2, [0], [1])

        x, y = np.array(0.4), np.array(0.8)
        actual = rel_ent_circuit(({"param": x},), ({"param": y},))

        # compare transform results with analytic results
        expected = (
            np.cos(x / 2) ** 2 * (np.log(np.cos(x / 2) ** 2) - np.log(np.cos(y / 2) ** 2))
        ) + (np.sin(x / 2) ** 2 * (np.log(np.sin(x / 2) ** 2) - np.log(np.sin(y / 2) ** 2)))

        assert np.allclose(actual, expected)

    @pytest.mark.parametrize("device", ["default.qubit", "default.mixed", "lightning.qubit"])
    def test_entropy_wire_labels(self, device, tol):
        """Test that relative_entropy is correct with custom wire labels"""
        param = np.array([0.678, 1.234])
        wires = ["a", 8]
        dev = qml.device(device, wires=wires)

        @qml.qnode(dev)
        def circuit(param):
            qml.RY(param, wires=wires[0])
            qml.CNOT(wires=wires)
            return qml.state()

        rel_ent_circuit = qml.qinfo.relative_entropy(circuit, circuit, [wires[0]], [wires[1]])
        actual = rel_ent_circuit((param[0],), (param[1],))

        # compare transform results with analytic results
        first_term = np.cos(param[0] / 2) ** 2 * (
            np.log(np.cos(param[0] / 2) ** 2) - np.log(np.cos(param[1] / 2) ** 2)
        )
        second_term = np.sin(param[0] / 2) ** 2 * (
            np.log(np.sin(param[0] / 2) ** 2) - np.log(np.sin(param[1] / 2) ** 2)
        )
        expected = first_term + second_term

        assert np.allclose(actual, expected, atol=tol)


@pytest.mark.parametrize("device", ["default.qubit", "default.mixed"])
class TestBroadcasting:
    """Test that the entropy transforms support broadcasting"""

    def test_vn_entropy_broadcast(self, device):
        """Test that the vn_entropy transform supports broadcasting"""
        dev = qml.device(device, wires=2)

        @qml.qnode(dev)
        def circuit_state(x):
            qml.IsingXX(x, wires=[0, 1])
            return qml.state()

        x = np.array([0.4, 0.6, 0.8])
        entropy = qml.qinfo.vn_entropy(circuit_state, wires=[0])(x)

        expected = [expected_entropy_ising_xx(_x) for _x in x]
        assert qml.math.allclose(entropy, expected)

    def test_mutual_info_broadcast(self, device):
        """Test that the mutual_info transform supports broadcasting"""
        dev = qml.device(device, wires=2)

        @qml.qnode(dev)
        def circuit_state(x):
            qml.IsingXX(x, wires=[0, 1])
            return qml.state()

        x = np.array([0.4, 0.6, 0.8])
        minfo = qml.qinfo.mutual_info(circuit_state, wires0=[0], wires1=[1])(x)

        expected = [2 * expected_entropy_ising_xx(_x) for _x in x]
        assert qml.math.allclose(minfo, expected)

    def test_relative_entropy_broadcast(self, device):
        """Test that the relative_entropy transform supports broadcasting"""
        dev = qml.device(device, wires=2)

        @qml.qnode(dev)
        def circuit_state(x):
            qml.IsingXX(x, wires=[0, 1])
            return qml.state()

        x = np.array([0.4, 0.6, 0.8])
        y = np.array([0.6, 0.8, 1.0])

        entropy = qml.qinfo.relative_entropy(circuit_state, circuit_state, wires0=[0], wires1=[1])(
            x, y
        )

        eigs0 = np.stack([np.cos(x / 2) ** 2, np.sin(x / 2) ** 2])
        eigs1 = np.stack([np.cos(y / 2) ** 2, np.sin(y / 2) ** 2])
        expected = np.sum(eigs0 * np.log(eigs0), axis=0) - np.sum(eigs0 * np.log(eigs1), axis=0)
        assert qml.math.allclose(entropy, expected)
