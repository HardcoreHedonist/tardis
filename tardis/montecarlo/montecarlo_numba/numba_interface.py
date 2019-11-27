from numba import float64, int64, jitclass
import numpy as np

from tardis import constants as const


C_SPEED_OF_LIGHT = const.c.to('cm/s').value

numba_model_spec = [
    ('r_inner', float64[:]),
    ('r_outer', float64[:]),
    ('time_explosion', float64)
]


@jitclass(numba_model_spec)
class NumbaModel(object):

    def __init__(self, r_inner, r_outer, time_explosion):
        """
        Model for the Numba mode

        Parameters
        ----------
        r_inner: numpy.ndarray
        r_outer: numpy.ndarray
        time_explosion: float
        """
        self.r_inner = r_inner
        self.r_outer = r_outer
        self.time_explosion = time_explosion

numba_plasma_spec = [
    ('electron_density', float64[:]),
    ('line_list_nu', float64[:]),
    ('tau_sobolev', float64[:, :]),
    ('transition_probabilities', float64[:, :]),
    ('line2macro_level_upper', int64[:]),
    ('macro_block_references', int64[:]),
    ('transition_type', int64[:]),
    ('destination_level_id', int64[:]),
    ('transition_line_id', int64[:]),

]

@jitclass(numba_plasma_spec)
class NumbaPlasma(object):
    def __init__(self, electron_density, line_list_nu, tau_sobolev,
                 transition_probabilities, line2macro_level_upper,
                 macro_block_references, transition_type, destination_level_id,
                 transition_line_id):

        self.electron_density = electron_density
        self.line_list_nu = line_list_nu
        self.tau_sobolev = tau_sobolev

        #### Macro Atom transition probabilities
        self.transition_probabilities = transition_probabilities
        self.line2macro_level_upper = line2macro_level_upper

        self.macro_block_references = macro_block_references
        self.transition_type = transition_type

        # Destination level is not needed and/or generated for downbranch
        self.destination_level_id = destination_level_id
        self.transition_line_id = transition_line_id


def numba_plasma_initialize(plasma):
    electron_densities = plasma.electron_densities.values
    line_list_nu = plasma.atomic_data.lines.nu.values
    tau_sobolev = np.ascontiguousarray(plasma.tau_sobolevs.values.copy(),
                                       dtype=np.float64)

    transition_probabilities = np.ascontiguousarray(
        plasma.transition_probabilities.values.copy(), dtype=np.float64)
    line2macro_level_upper = plasma.atomic_data.lines_upper2macro_reference_idx
    macro_block_references = plasma.atomic_data.macro_atom_references[
        'block_references'].values

    transition_type = plasma.atomic_data.macro_atom_data[
        'transition_type'].values

    # Destination level is not needed and/or generated for downbranch
    destination_level_id = plasma.atomic_data.macro_atom_data[
        'destination_level_idx'].values
    transition_line_id = plasma.atomic_data.macro_atom_data[
        'lines_idx'].values

    return NumbaPlasma(electron_densities, line_list_nu, tau_sobolev,
                       transition_probabilities, line2macro_level_upper,
                       macro_block_references, transition_type,
                       destination_level_id, transition_line_id)


packet_collection_spec = [
    ('packets_input_nu', float64[:]),
    ('packets_input_mu', float64[:]),
    ('packets_input_energy', float64[:]),
    ('packets_output_nu', float64[:]),
    ('packets_output_energy', float64[:]),
]

@jitclass(packet_collection_spec)
class PacketCollection(object):
    def __init__(self, packets_input_nu, packets_input_mu, packets_input_energy,
                 packets_output_nu, packets_output_energy):
        self.packets_input_nu = packets_input_nu
        self.packets_input_mu = packets_input_mu
        self.packets_input_energy = packets_input_energy
        self.packets_output_nu = packets_output_nu
        self.packets_output_energy = packets_output_energy

vpacket_collection_spec = [
    ('spectrum_frequency', float64[:]),
    ('nus', float64[:]),
    ('energies', float64[:]),
    ('idx', int64),
    ('number_of_vpackets', int64)
]

@jitclass(vpacket_collection_spec)
class VPacketCollection(object):
    def __init__(self, spectrum_frequency, number_of_vpackets, initial_vpacket_bins):
        self.spectrum_frequency = spectrum_frequency
        self.nus = np.empty(initial_vpacket_bins, dtype=np.float64)
        self.energies = np.empty(initial_vpacket_bins, dtype=np.float64)
        self.number_of_vpackets = number_of_vpackets
        self.idx = 0
        
        
estimators_spec = [
    ('j_estimator', float64[:]),
    ('nu_bar_estimator', float64[:]),
]

@jitclass(estimators_spec)
class Estimators(object):
    def __init__(self, j_estimator, nu_bar_estimator):
        self.j_estimator = j_estimator
        self.nu_bar_estimator = nu_bar_estimator

monte_carlo_configuration_spec = [
    ('number_of_vpackets', int64)
]

@jitclass(monte_carlo_configuration_spec)
class MonteCarloConfiguration(object):
    def __init__(self, number_of_vpackets):
        self.number_of_vpackets = number_of_vpackets


#class TrackRPacket(object):