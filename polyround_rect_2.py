import numpy as np
import warnings
import math
from dingo.MetabolicNetwork import MetabolicNetwork
from dingo.fva import slow_fva
from dingo.utils import (
    map_samples_to_steady_states,
    get_matrices_of_low_dim_polytope,
    get_matrices_of_full_dim_polytope,
)

try:
    import gurobipy
    from dingo.gurobi_based_implementations import (
        fast_fba,
        fast_fva,
        fast_inner_ball,
        fast_remove_redundant_facets,
    )
except ImportError as e:
    pass

from volestipy import HPolytope

# Import PolyRound modules for polytope simplification and transformation
from PolyRound.mutable_classes.polytope import Polytope
from PolyRound.api import PolyRoundApi


class PolytopeSampler:
    def __init__(self, metabol_net):

        if not isinstance(metabol_net, MetabolicNetwork):
            raise Exception("An unknown input object given for initialization.")

        self._metabolic_network = metabol_net
        self._A = []
        self._b = []
        self._N = []
        self._N_shift = []
        self._T = []
        self._T_shift = []
        self._parameters = {}
        self._parameters["nullspace_method"] = "sparseQR"
        self._parameters["opt_percentage"] = self.metabolic_network.parameters[
            "opt_percentage"
        ]
        self._parameters["distribution"] = "uniform"
        self._parameters["first_run_of_mmcs"] = True
        self._parameters["remove_redundant_facets"] = True

        try:
            import gurobipy

            self._parameters["fast_computations"] = True
            self._parameters["tol"] = 1e-06
        except ImportError as e:
            self._parameters["fast_computations"] = False
            self._parameters["tol"] = 1e-03

    def get_polytope(self):
        # ... same as before ...

    def generate_steady_states_no_multiphase(
        self, method="billiard_walk", n=1000, burn_in=0, thinning=1
    ):
        # ... same as before ...

    def round_polytope(self, method="john_position"):
        # ... same as before ...

    def generate_steady_states(
        self, ess=1000, psrf=False, parallel_mmcs=False, num_threads=1
    ):
        """
        A member function to sample steady states.

        Keyword arguments:
        ess -- the target effective sample size
        psrf -- a boolean flag to request PSRF smaller than 1.1 for all marginal fluxes
        parallel_mmcs -- a boolean flag to request the parallel mmcs
        num_threads -- the number of threads to use for parallel mmcs
        """
        self.get_polytope()

        P = HPolytope(self._A, self._b)

        if self._parameters["fast_computations"]:
            self._A, self._b, Tr, Tr_shift, samples = P.fast_mmcs(
                ess, psrf, parallel_mmcs, num_threads
            )
        else:
            self._A, self._b, Tr, Tr_shift, samples = P.slow_mmcs(
                ess, psrf, parallel_mmcs, num_threads
            )

        if self._parameters["first_run_of_mmcs"]:
            steady_states = map_samples_to_steady_states(
                samples, self._N, self._N_shift
            )
            self._parameters["first_run_of_mmcs"] = False
        else:
            steady_states = map_samples_to_steady_states(
                samples, self._N, self._N_shift, self._T, self._T_shift
            )

        self._T = np.dot(self._T, Tr)
        self._T_shift = np.add(self._T_shift, Tr_shift)

        return steady_states

    @staticmethod
    def sample_from_polytope(
        A, b, ess=1000, psrf=False, parallel_mmcs=False, num_threads=1
    ):
        # ... same as before ...

    @staticmethod
    def sample_from_polytope_no_multiphase(
        A, b, method="billiard_walk", n=1000, burn_in=0, thinning=1
    ):
        # ... same as before ...

    @staticmethod
    def sample_from_fva_output(
        min_fluxes,
        max_fluxes,
        biomass_function,
        max_biomass_objective,
        S,
        opt_percentage=100,
        ess=1000,
        psrf=False,
        parallel_mmcs=False,
        num_threads=1,
    ):
        # ... same as before ...

    @property
    def A(self):
        return self._A

    @property
    def b(self):
        return self._b

    @property
    def T(self):
        return self._T

    @property
    def T_shift(self):
        return self._T_shift

    @property
    def N(self):
        return self._N

    @property
    def N_shift(self):
        return self._N_shift

    @property
    def metabolic_network(self):
        return self._metabolic_network

    def facet_redundancy_removal(self, value):
        self._parameters["remove_redundant_facets"] = value

        if (not self._parameters["fast_computations"]) and value:
            warnings.warn(
                "Since you are in slow mode the redundancy removal step is skipped (dingo does not currently support this functionality in slow mode)"
            )

    def set_fast_mode(self):

        self._parameters["fast_computations"] = True
        self._parameters["tol"] = 1e-06

    def set_slow_mode(self):

        self._parameters["fast_computations"] = False
        self._parameters["tol"] = 1e-03

    def set_distribution(self, value):

        self._parameters["distribution"] = value

    def set_nullspace_method(self, value):

        self._parameters["nullspace_method"] = value

    def set_tol(self, value):

        self._parameters["to1"] = value

    def set_opt_percentage(self, value):

        self._parameters["opt_percentage"] = value
