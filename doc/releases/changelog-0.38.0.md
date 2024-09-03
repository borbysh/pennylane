:orphan:

# Release 0.38.0 (current release)

<h3>New features since last release</h3>

<h4>Converting noise models from Qiskit ♻️</h4>

* A new `qml.from_qiskit_noise` method now allows one to convert a Qiskit ``NoiseModel`` to a
  PennyLane ``NoiseModel`` via the Pennylane-Qiskit plugin.
  [(#5996)](https://github.com/PennyLaneAI/pennylane/pull/5996)

<h4>Registers of wires 🌈</h4>

* Set operations are now supported by Wires.
  [(#5983)](https://github.com/PennyLaneAI/pennylane/pull/5983)

* The representation for `Wires` has now changed to be more copy-paste friendly.
  [(#5958)](https://github.com/PennyLaneAI/pennylane/pull/5958)

* A new function `qml.registers` has been added, enabling the creation of registers, which are implemented as a dictionary of `Wires` instances.
  [(#5957)](https://github.com/PennyLaneAI/pennylane/pull/5957)
  [(#6102)](https://github.com/PennyLaneAI/pennylane/pull/6102)

<h4>Quantum arithmetic operations 🧮</h4>

* The `qml.Adder` and `qml.PhaseAdder` templates are added to perform in-place modular addition.
  [(#6109)](https://github.com/PennyLaneAI/pennylane/pull/6109)

* The `qml.Multiplier` and `qml.OutMultiplier` templates are added to perform modular multiplication.
  [(#6112)](https://github.com/PennyLaneAI/pennylane/pull/6112)

* The `qml.OutAdder` and `qml.ModExp` templates are added to perform out-of-place modular addition and modular exponentiation.
  [(#6121)](https://github.com/PennyLaneAI/pennylane/pull/6121)


<h4>Creating spin Hamiltonians 🧑‍🎨</h4>

* The function ``transverse_ising`` is added to generate transverse-field Ising Hamiltonian.
  [(#6106)](https://github.com/PennyLaneAI/pennylane/pull/6106)

* The functions ``heisenberg`` and ``fermi_hubbard`` are added to generate Heisenberg and Fermi-Hubbard Hamiltonians respectively.
  [(#6128)](https://github.com/PennyLaneAI/pennylane/pull/6128)

<h3>Improvements 🛠</h3>

* Counts measurements with `all_outcomes=True` can now be used with jax jitting. Measurements
  broadcasted across all available wires (`qml.probs()`) can now be used with jit and devices that
  allow variable numbers of wires (`qml.device('default.qubit')`).
  [(#6108)](https://github.com/PennyLaneAI/pennylane/pull/6108/)

<h4>A Prep-Select-Prep template</h4>

* The `qml.PrepSelPrep` template is added. The template implements a block-encoding of a linear
  combination of unitaries.
  [(#5756)](https://github.com/PennyLaneAI/pennylane/pull/5756)
  [(#5987)](https://github.com/PennyLaneAI/pennylane/pull/5987)

<h4>QChem improvements</h4>

* Molecules and Hamiltonians can now be constructed for all the elements present in the periodic table.
  [(#5821)](https://github.com/PennyLaneAI/pennylane/pull/5821)

* `qml.UCCSD` now accepts an additional optional argument, `n_repeats`, which defines the number of
  times the UCCSD template is repeated. This can improve the accuracy of the template by reducing
  the Trotter error but would result in deeper circuits.
  [(#5801)](https://github.com/PennyLaneAI/pennylane/pull/5801)

* The `qubit_observable` function is modified to return an ascending wire order for molecular 
  Hamiltonians.
  [(#5950)](https://github.com/PennyLaneAI/pennylane/pull/5950)

* A new method `to_mat` has been added to the `FermiWord` and `FermiSentence` classes, which allows
  computing the matrix representation of these Fermi operators.
  [(#5920)](https://github.com/PennyLaneAI/pennylane/pull/5920)
  
* `qml.pauli.group_observables` now uses `Rustworkx` colouring algorithms to solve the Minimum Clique Cover problem.
  This adds two new options for the `method` argument: `dsatur` and `gis`. In addition, the creation of the adjacency matrix
  now takes advantage of the symplectic representation of the Pauli observables. An additional function `qml.pauli.compute_partition_indices`
  is added to calculate the indices from the partitioned observables more efficiently. `qml.pauli.grouping.PauliGroupingStrategy.idx_partitions_from_graph`
  can be used to compute partitions of custom indices. These changes improve the wall time of `qml.LinearCombination.compute_grouping`
  and `grouping_type='qwc'` by orders of magnitude.
  [(#6043)](https://github.com/PennyLaneAI/pennylane/pull/6043)

<h4>Improvements to operators</h4>

* `GlobalPhase` now supports parameter broadcasting.
  [(#5923)](https://github.com/PennyLaneAI/pennylane/pull/5923)

* Added the `compute_decomposition` method for `qml.Hermitian`.
  [(#6062)](https://github.com/PennyLaneAI/pennylane/pull/6062)

* Port the fast `apply_operation` implementation of `PauliZ` to `PhaseShift`, `S` and `T`.
  [(#5876)](https://github.com/PennyLaneAI/pennylane/pull/5876)

* The `tree-traversal` algorithm implemented in `default.qubit` is refactored
  into an iterative (instead of recursive) implementation, doing away with
  potential stack overflow for deep circuits.
  [(#5868)](https://github.com/PennyLaneAI/pennylane/pull/5868)
  
* The `tree-traversal` algorithm is compatible with analytic-mode execution (`shots=None`).
  [(#5868)](https://github.com/PennyLaneAI/pennylane/pull/5868)
  
* `fuse_rot_angles` now respects the global phase of the combined rotations.
  [(#6031)](https://github.com/PennyLaneAI/pennylane/pull/6031)

* The `CNOT` operator no longer decomposes to itself. Instead, it raises a `qml.DecompositionUndefinedError`.
  [(#6039)](https://github.com/PennyLaneAI/pennylane/pull/6039)

<h4>Mid-circuit measurement improvements</h4>

* `qml.dynamic_one_shot` now supports circuits using the `"tensorflow"` interface.
  [(#5973)](https://github.com/PennyLaneAI/pennylane/pull/5973)

* If the conditional does not include a mid-circuit measurement, then `qml.cond`
  will automatically evaluate conditionals using standard Python control flow.
  [(#6016)](https://github.com/PennyLaneAI/pennylane/pull/6016)

  This allows `qml.cond` to be used to represent a wider range of conditionals:

  ```python
  dev = qml.device("default.qubit", wires=1)

  @qml.qnode(dev)
  def circuit(x):
      c = qml.cond(x > 2.7, qml.RX, qml.RZ)
      c(x, wires=0)
      return qml.probs(wires=0)
  ```

  ```pycon
  >>> print(qml.draw(circuit)(3.8))
  0: ──RX(3.80)─┤  Probs
  >>> print(qml.draw(circuit)(0.54))
  0: ──RZ(0.54)─┤  Probs
  ```

<h4>Transforms</h4>

* The `diagonalize_measurements` transform is added. This transform converts measurements
  to the Z basis by applying the relevant diagonalizing gates. It can be set to diagonalize only 
  a subset of the base observables `{X, Y, Z, Hadamard}`.
  [(#5829)](https://github.com/PennyLaneAI/pennylane/pull/5829)

* The `split_to_single_terms` transform is added. This transform splits expectation values of sums
  into multiple single-term measurements on a single tape, providing better support for simulators
  that can handle non-commuting observables but don't natively support multi-term observables.
  [(#5884)](https://github.com/PennyLaneAI/pennylane/pull/5884)

* New functionality has been added to natively support exponential extrapolation when using the `mitigate_with_zne`. This allows
  users to have more control over the error mitigation protocol without needing to add further dependencies.
  [(#5972)](https://github.com/PennyLaneAI/pennylane/pull/5972)

* `fuse_rot_angles` now respects the global phase of the combined rotations.
  [(#6031)](https://github.com/PennyLaneAI/pennylane/pull/6031)

<h4>Capturing and representing hybrid programs</h4>

* `qml.for_loop` now supports `range`-like syntax with default `step=1`.
  [(#6068)](https://github.com/PennyLaneAI/pennylane/pull/6068)

* Applying `adjoint` and `ctrl` to a quantum function can now be captured into plxpr.
  Furthermore, the `qml.cond` function can be captured into plxpr.
  [(#5966)](https://github.com/PennyLaneAI/pennylane/pull/5966)
  [(#5967)](https://github.com/PennyLaneAI/pennylane/pull/5967)
  [(#5999)](https://github.com/PennyLaneAI/pennylane/pull/5999)
  [(#6058)](https://github.com/PennyLaneAI/pennylane/pull/6058)

* During experimental program capture, functions that accept and/or return `pytree` structures can now be handled in the `QNode` call, `cond`, `for_loop` and `while_loop`. 
  [(#6081)](https://github.com/PennyLaneAI/pennylane/pull/6081)

* During experimental program capture, the qnode can now use closure variables.
  [(#6052)](https://github.com/PennyLaneAI/pennylane/pull/6052)

* Mid-circuit measurements can now be captured with `qml.capture` enabled.
  [(#6015)](https://github.com/PennyLaneAI/pennylane/pull/6015)

* `qml.for_loop` can now be captured into plxpr.
  [(#6041)](https://github.com/PennyLaneAI/pennylane/pull/6041)
  [(#6064)](https://github.com/PennyLaneAI/pennylane/pull/6064)

* `qml.for_loop` and `qml.while_loop` now fallback to standard Python control
  flow if `@qjit` is not present, allowing the same code to work with and without
  `@qjit` without any rewrites.
  [(#6014)](https://github.com/PennyLaneAI/pennylane/pull/6014)

  ```python
  dev = qml.device("lightning.qubit", wires=3)

  @qml.qnode(dev)
  def circuit(x, n):

      @qml.for_loop(0, n, 1)
      def init_state(i):
          qml.Hadamard(wires=i)

      init_state()

      @qml.for_loop(0, n, 1)
      def apply_operations(i, x):
          qml.RX(x, wires=i)

          @qml.for_loop(i + 1, n, 1)
          def inner(j):
              qml.CRY(x**2, [i, j])

          inner()
          return jnp.sin(x)

      apply_operations(x)
      return qml.probs()
  ```

  ```pycon
  >>> print(qml.draw(circuit)(0.5, 3))
  0: ──H──RX(0.50)─╭●────────╭●──────────────────────────────────────┤  Probs
  1: ──H───────────╰RY(0.25)─│──────────RX(0.48)─╭●──────────────────┤  Probs
  2: ──H─────────────────────╰RY(0.25)───────────╰RY(0.23)──RX(0.46)─┤  Probs
  >>> circuit(0.5, 3)
  array([0.125     , 0.125     , 0.09949758, 0.15050242, 0.07594666,
       0.11917543, 0.08942104, 0.21545687])
  >>> qml.qjit(circuit)(0.5, 3)
  Array([0.125     , 0.125     , 0.09949758, 0.15050242, 0.07594666,
       0.11917543, 0.08942104, 0.21545687], dtype=float64)
  ```

<h4>Community contributions 🥳</h4>

* Resolved the bug in `qml.ThermalRelaxationError` where there was a typo from `tq` to `tg`.
  [(#5988)](https://github.com/PennyLaneAI/pennylane/issues/5988)

* `DefaultQutritMixed` readout error has been added using parameters `readout_relaxation_probs` and 
  `readout_misclassification_probs` on the `default.qutrit.mixed` device. These parameters add a `~.QutritAmplitudeDamping`  and a `~.TritFlip` channel, respectively,
  after measurement diagonalization. The amplitude damping error represents the potential for
  relaxation to occur during longer measurements. The trit flip error represents misclassification during readout.
  [(#5842)](https://github.com/PennyLaneAI/pennylane/pull/5842)s

<h4>Other improvements</h4>

* Added the decomposition of zyz for special unitaries with multiple control wires.
  [(#6042)](https://github.com/PennyLaneAI/pennylane/pull/6042)

* A new method `process_density_matrix` has been added to the `ProbabilityMP` and `DensityMatrixMP`
  classes, allowing for more efficient handling of quantum density matrices, particularly with batch
  processing support. This method simplifies the calculation of probabilities from quantum states
  represented as density matrices.
  [(#5830)](https://github.com/PennyLaneAI/pennylane/pull/5830)

* `SProd.terms` now flattens out the terms if the base is a multi-term observable.
  [(#5885)](https://github.com/PennyLaneAI/pennylane/pull/5885)

* `QNGOptimizer` now supports cost functions with multiple arguments, updating each argument independently.
  [(#5926)](https://github.com/PennyLaneAI/pennylane/pull/5926)

* Removed `semantic_version` from the list of required packages in PennyLane. 
  [(#5836)](https://github.com/PennyLaneAI/pennylane/pull/5836)

* `qml.devices.LegacyDeviceFacade` has been added to map the legacy devices to the new
  device interface.
  [(#5927)](https://github.com/PennyLaneAI/pennylane/pull/5927)

* Added the `compute_sparse_matrix` method for `qml.ops.qubit.BasisStateProjector`.
  [(#5790)](https://github.com/PennyLaneAI/pennylane/pull/5790)

* `StateMP.process_state` defines rules in `cast_to_complex` for complex casting, avoiding a superfluous state vector copy in Lightning simulations
  [(#5995)](https://github.com/PennyLaneAI/pennylane/pull/5995)

* `QuantumScript.hash` is now cached, leading to performance improvements.
  [(#5919)](https://github.com/PennyLaneAI/pennylane/pull/5919)

* Observable validation for `default.qubit` is now based on execution mode (analytic vs. finite shots) and measurement type (sample measurement vs. state measurement).
  [(#5890)](https://github.com/PennyLaneAI/pennylane/pull/5890)

* Added `is_leaf` parameter to function `flatten` in the `qml.pytrees` module. This is to allow node flattening to be stopped for any node where the `is_leaf` optional argument evaluates to being `True`.
  [(#6107)](https://github.com/PennyLaneAI/pennylane/issues/6107)

* Added a progress bar when downloading datasets with `qml.data.load()`
  [(#5560)](https://github.com/PennyLaneAI/pennylane/pull/5560)

* Upgraded and simplified `StatePrep` and `AmplitudeEmbedding` templates.
  [(#6034)](https://github.com/PennyLaneAI/pennylane/pull/6034)
  [(#6170)](https://github.com/PennyLaneAI/pennylane/pull/6170)

* Upgraded and simplified `BasisState` and `BasisEmbedding` templates.
  [(#6021)](https://github.com/PennyLaneAI/pennylane/pull/6021)
  
<h3>Breaking changes 💔</h3>

* `MeasurementProcess.shape(shots: Shots, device:Device)` is now
  `MeasurementProcess.shape(shots: Optional[int], num_device_wires:int = 0)`. This has been done to allow
  jitting when a measurement is broadcasted across all available wires, but the device does not specify wires.
  [(#6108)](https://github.com/PennyLaneAI/pennylane/pull/6108/)

* If the shape of a probability measurement is affected by a `Device.cutoff` property, it will no longer work with
  jitting.
  [(#6108)](https://github.com/PennyLaneAI/pennylane/pull/6108/)

* `GlobalPhase` is considered non-differentiable with tape transforms.
  As a consequence, `qml.gradients.finite_diff` and `qml.gradients.spsa_grad` no longer
  support differentiation of `GlobalPhase` with state-based outputs.
  [(#5620)](https://github.com/PennyLaneAI/pennylane/pull/5620) 

* The `CircuitGraph.graph` rustworkx graph now stores indices into the circuit as the node labels,
  instead of the operator/ measurement itself.  This allows the same operator to occur multiple times in
  the circuit.
  [(#5907)](https://github.com/PennyLaneAI/pennylane/pull/5907)

* `queue_idx` attribute has been removed from the `Operator`, `CompositeOp`, and `SymbolicOp` classes.
  [(#6005)](https://github.com/PennyLaneAI/pennylane/pull/6005)

* `qml.from_qasm` no longer removes measurements from the QASM code. Use 
  `measurements=[]` to remove measurements from the original circuit.
  [(#5982)](https://github.com/PennyLaneAI/pennylane/pull/5982)

* `qml.transforms.map_batch_transform` has been removed, since transforms can be applied directly to a batch of tapes.
  See :func:`~.pennylane.transform` for more information.
  [(#5981)](https://github.com/PennyLaneAI/pennylane/pull/5981)

* `QuantumScript.interface` has been removed.
  [(#5980)](https://github.com/PennyLaneAI/pennylane/pull/5980)

<h3>Deprecations 👋</h3>

* The `decomp_depth` argument in `qml.device` has been deprecated.
  [(#6026)](https://github.com/PennyLaneAI/pennylane/pull/6026)

* The `max_expansion` argument in `qml.QNode` has been deprecated.
  [(#6026)](https://github.com/PennyLaneAI/pennylane/pull/6026)

* The `expansion_strategy` attribute in the `QNode` class is deprecated.
  [(#5989)](https://github.com/PennyLaneAI/pennylane/pull/5989)

* The `expansion_strategy` argument has been deprecated in all of `qml.draw`, `qml.draw_mpl`, and `qml.specs`.
  The `level` argument should be used instead.
  [(#5989)](https://github.com/PennyLaneAI/pennylane/pull/5989)

* `Operator.expand` has been deprecated. Users should simply use `qml.tape.QuantumScript(op.decomposition())`
  for equivalent behaviour.
  [(#5994)](https://github.com/PennyLaneAI/pennylane/pull/5994)

* `pennylane.transforms.sum_expand` and `pennylane.transforms.hamiltonian_expand` have been deprecated.
  Users should instead use `pennylane.transforms.split_non_commuting` for equivalent behaviour.
  [(#6003)](https://github.com/PennyLaneAI/pennylane/pull/6003)

* The `expand_fn` argument in `qml.execute` has been deprecated.
  Instead, please create a `qml.transforms.core.TransformProgram` with the desired preprocessing and pass it to the `transform_program` argument of `qml.execute`.
  [(#5984)](https://github.com/PennyLaneAI/pennylane/pull/5984)

* The `max_expansion` argument in `qml.execute` has been deprecated.
  Instead, please use `qml.devices.preprocess.decompose` with the desired expansion level, add it to a `TransformProgram` and pass it to the `transform_program` argument of `qml.execute`.
  [(#5984)](https://github.com/PennyLaneAI/pennylane/pull/5984)

* The `override_shots` argument in `qml.execute` is deprecated.
  Instead, please add the shots to the `QuantumTape`'s to be executed.
  [(#5984)](https://github.com/PennyLaneAI/pennylane/pull/5984)

* The `device_batch_transform` argument in `qml.execute` is deprecated.
  Instead, please create a `qml.transforms.core.TransformProgram` with the desired preprocessing and pass it to the `transform_program` argument of `qml.execute`.
  [(#5984)](https://github.com/PennyLaneAI/pennylane/pull/5984)

* `pennylane.qinfo.classical_fisher` and `pennylane.qinfo.quantum_fisher` have been deprecated.
  Instead, use `pennylane.gradients.classical_fisher` and `pennylane.gradients.quantum_fisher`.
  [(#5985)](https://github.com/PennyLaneAI/pennylane/pull/5985)

* The legacy devices `default.qubit.{autograd,torch,tf,jax,legacy}` are deprecated.
  Instead, use `default.qubit` as it now supports backpropagation through the several backends.
  [(#5997)](https://github.com/PennyLaneAI/pennylane/pull/5997)

* The logic for internally switching a device for a different backpropagation
  compatible device is now deprecated, as it was in place for the deprecated
  `default.qubit.legacy`.
  [(#6032)](https://github.com/PennyLaneAI/pennylane/pull/6032)

<h3>Documentation 📝</h3>

* Improves the docstring for `qinfo.quantum_fisher` regarding the internally used functions and
  potentially required auxiliary wires.
  [(#6074)](https://github.com/PennyLaneAI/pennylane/pull/6074)

* Improves the docstring for `QuantumScript.expand` and `qml.tape.tape.expand_tape`.
  [(#5974)](https://github.com/PennyLaneAI/pennylane/pull/5974)

<h3>Bug fixes 🐛</h3>

* Fix Pytree serialization of operators with empty shot vectors
  [(#6155)](https://github.com/PennyLaneAI/pennylane/pull/6155)

* Fixes an error in the `dynamic_one_shot` transform when used with sampling a single shot.
  [(#6149)](https://github.com/PennyLaneAI/pennylane/pull/6149)

* `qml.transforms.pattern_matching_optimization` now preserves the tape measurements.
  [(#6153)](https://github.com/PennyLaneAI/pennylane/pull/6153)

* `qml.transforms.broadcast_expand` no longer squeezes out batch sizes of size 1, as a batch size of 1 is still a
  batch size.
  [(#6147)](https://github.com/PennyLaneAI/pennylane/pull/6147)

* Catalyst replaced `argnum` with `argnums` in gradient related functions, therefore we update the Catalyst
  calls to those functions in PennyLane.
  [(#6117)](https://github.com/PennyLaneAI/pennylane/pull/6117)

* `fuse_rot_angles` no longer returns wrong derivatives at singular points but returns NaN.
  [(#6031)](https://github.com/PennyLaneAI/pennylane/pull/6031)

* `qml.GlobalPhase` and `qml.I` can now be captured when acting on no wires.
  [(#6060)](https://github.com/PennyLaneAI/pennylane/pull/6060)

* Fix `jax.grad` + `jax.jit` not working for `AmplitudeEmbedding`, `StatePrep` and `MottonenStatePreparation`.
  [(#5620)](https://github.com/PennyLaneAI/pennylane/pull/5620) 

* Fixed a bug in `qml.center` that omitted elements from the center if they were
  linear combinations of input elements.
  [(#6049)](https://github.com/PennyLaneAI/pennylane/pull/6049)

* Fix a bug where the global phase returned by `one_qubit_decomposition` gained a broadcasting dimension.
  [(#5923)](https://github.com/PennyLaneAI/pennylane/pull/5923)

* Fixed a bug in `qml.SPSAOptimizer` that ignored keyword arguments in the objective function.
  [(#6027)](https://github.com/PennyLaneAI/pennylane/pull/6027)

* `dynamic_one_shot` was broken for old-API devices since `override_shots` was deprecated.
  [(#6024)](https://github.com/PennyLaneAI/pennylane/pull/6024)

* `CircuitGraph` can now handle circuits with the same operation instance occuring multiple times.
  [(#5907)](https://github.com/PennyLaneAI/pennylane/pull/5907)

* `qml.QSVT` is updated to store wire order correctly.
  [(#5959)](https://github.com/PennyLaneAI/pennylane/pull/5959)

* `qml.devices.qubit.measure_with_samples` now returns the correct result if the provided measurements
  contain sum of operators acting on the same wire.
  [(#5978)](https://github.com/PennyLaneAI/pennylane/pull/5978)

* `qml.AmplitudeEmbedding` has better support for features using low precision integer data types.
  [(#5969)](https://github.com/PennyLaneAI/pennylane/pull/5969)

* `qml.BasisState` and `qml.BasisEmbedding` now works with jax.jit, lightning.qubit and give the correct decomposition.
  [(#6021)](https://github.com/PennyLaneAI/pennylane/pull/6021)

* Jacobian shape is fixed for measurements with dimension in `qml.gradients.vjp.compute_vjp_single`.
[(5986)](https://github.com/PennyLaneAI/pennylane/pull/5986)

* `qml.lie_closure` works with sums of Paulis.
  [(#6023)](https://github.com/PennyLaneAI/pennylane/pull/6023)

* Workflows that parameterize the coefficients of `qml.exp` are now jit-compatible.
  [(#6082)](https://github.com/PennyLaneAI/pennylane/pull/6082)

* Fixes a bug where `CompositeOp.overlapping_ops` changes the original ordering of ops, causing incorrect matrix generated for `Prod` with `Sum` as operands.
  [(#6091)](https://github.com/PennyLaneAI/pennylane/pull/6091)

* `qml.qsvt` now works with "Wx" convention and any number of angles.
  [(#6105)](https://github.com/PennyLaneAI/pennylane/pull/6105)

* Basis set data from the Basis Set Exchange library can now be loaded for elements with `SPD`-type orbitals.
  [(#6159)](https://github.com/PennyLaneAI/pennylane/pull/6159)

<h3>Contributors ✍️</h3>

This release contains contributions from (in alphabetical order):

Tarun Kumar Allamsetty,
Guillermo Alonso,
Ali Asadi,
Utkarsh Azad,
Tonmoy T. Bhattacharya,
Gabriel Bottrill,
Jack Brown,
Ahmed Darwish,
Astral Cai,
Yushao Chen,
Ahmed Darwish,
Diksha Dhawan
Maja Franz,
Lillian M. A. Frederiksen,
Pietropaolo Frisoni,
Emiliano Godinez,
Austin Huang,
Renke Huang,
Josh Izaac,
Soran Jahangiri,
Korbinian Kottmann,
Christina Lee,
Jorge Martinez de Lejarza,
William Maxwell,
Vincent Michaud-Rioux,
Anurav Modak,
Mudit Pandey,
Andrija Paurevic,
Erik Schultheis,
nate stemen,
David Wierichs,