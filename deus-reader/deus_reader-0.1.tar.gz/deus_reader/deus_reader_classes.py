import struct
import numpy as num
import random
import sys


def solve(x, y, y0):
    if y0 is None:
        return num.nan
    if min(y) <= y0 <= max(y):
        if num.size(x) == num.size(y):
            if y[0] > y0:
                for i in range(num.size(y) - 1):
                    if y[i] >= y0 >= y[i + 1]:
                        return x[i + 1] + (y[i + 1] - y0) * (x[i] - x[i + 1]) / (y[i + 1] - y[i])
            else:
                for i in range(num.size(y) - 1):
                    if y[i] <= y0 <= y[i + 1]:
                        return x[i + 1] + (y[i + 1] - y0) * (x[i] - x[i + 1]) / (y[i + 1] - y[i])
        else:
            print("x and y should have the same dimension for 'solve'")
            return None
    else:
        return None


def derivative(x, y):
    dy = num.zeros(num.size(y))

    for i_d in range(num.size(x) - 2):
        dy[i_d + 1] = (y[i_d + 2] - y[i_d]) / (x[i_d + 2] - x[i_d])

    dy[0] = (y[1] - y[0]) / (x[1] - x[0])
    dy[-1] = (y[-1] - y[-2]) / (x[-1] - x[-2])
    return dy


class BasicCosmo:
    MPC = 3.086e+22
    MSUN = 1.98855e+30
    G = 6.67408e-11
    C = 299792458

    def __init__(self, Wm0, h0, Lbox, Npart, a):
        self.Wm0 = Wm0
        self.h0 = h0
        self.a = a
        self.l_box = Lbox
        self.n_part = Npart

    def particle_in_sun_mass_per_h(self):
        return (self.l_box / self.n_part)**3 * self.density() * BasicCosmo.MPC**3 / (BasicCosmo.MSUN * self.h0**2)

    def density(self):
        return 3 * (100 * self.h0) ** 2 /(8 * num.pi * BasicCosmo.G)*self.Wm0 / BasicCosmo.MPC**2 * 10**6


class Unit:
    def __init__(self):
        self._values = dict()
        self._values['r'] = '$r$ in [h$^{-1}$.Mpc]'
        self._values['D'] = '$\Delta(r)$'
        self._values['d'] = '$\delta(r)$'
        self._values['Dv'] = '$\Delta_v(r)$'
        self._values['sigma_v'] = '$\sigma_v$ in [km.s$^{-1}$]'
        self._values['mass'] = '$m$ in [h$^{-1}$.M$_\odot$]'
        self._values['R1'] = '$R_1$ in [h$^{-1}$.Mpc]'
        self._values['R1_v'] = '$R_1^v$ in [h$^{-1}$.Mpc]'
        self._values['d1'] = '$\delta_1$'

    def __call__(self, key):
        if key in self._values:
            return self._values[key]
        elif key[1:] in self._values:
            return 'd' + self._values[key[1:]]
        else:
            return key


class DataProfile:
    def __init__(self, x, y, z, mass, r, D, v, sigma_v, cosmo, over_density):
        self.cosmo = cosmo

        self._arrays = dict()
        self._arrays['r'] = r
        self._arrays['D'] = D
        self._arrays['d'] = D + r/3*derivative(r, D)

        self._arrays['Dv'] = 2997.92458*v/r
        # in [km/s]
        self._arrays['sigma_v'] = self.cosmo.C * sigma_v / 1000

        self._scalars = dict()
        self._scalars['x'] = x
        self._scalars['y'] = y
        self._scalars['z'] = z

        self._scalars['mass'] = mass
        if over_density:
            self._scalars['mass'] *= self.cosmo.particle_in_sun_mass_per_h()
        self._scalars['d0'] = self._arrays['d'][0]

        self._scalars['R1'] = solve(r, D, 0.0)
        self._scalars['R1_v'] = solve(r, self._arrays['Dv'], 0.0)
        self._scalars['d1'] = solve(self._arrays['d'], r, self._scalars['R1'])

    def sparsity(self, Delta_2, Delta_1=200):
        r1 = solve(self._arrays['r'], self._arrays['D'], Delta_1)
        r2 = solve(self._arrays['r'], self._arrays['D'], Delta_2)
        if r1 is not None and r2 is not None:
            return (r1 / r2)**3*(1 + Delta_1)/(1 + Delta_2)
        else:
            return None

    def __call__(self, *args, **kwargs):
        """
        the getter.

        :param args: the desired quantities. Can be one or more of the following keys

            - "R1"= the compensation radius in [Mpc/h]
            - "d1"= the compensation density
            - "r"= the radial comoving coordinate in [Mpc/h]
            - "D"= the mass contrast :math:`\\Delta(r)`
            - "d"= the density contrast profile :math:`\\delta(r)`
            - "Dv"= the velocity contrast profile :math:`\\Delta_v(r)=v_r/(rH)`
        :type args: str

        :return: a tuple with the desired quantities
        """
        t = []
        for key in args:
            if key in self._arrays:
                t.append(self._arrays[key])
            elif key in self._scalars:
                t.append(self._scalars[key])
            elif key == 'sparsity':
                t.append(self.sparsity(**kwargs))
        if len(t) == 1:
            return t[0]
        elif len(t) > 1:
            return tuple(t)
        else:
            return None


class DataProfiles:
    def __init__(self, profile=None):
        self._profiles = []

        self._mean_arrays = dict()
        self._mean_arrays['r'] = None
        self._mean_arrays['D'] = None
        self._mean_arrays['dD'] = None
        self._mean_arrays['Dv'] = None
        self._mean_arrays['dDv'] = None
        self._mean_arrays['sigma_v'] = None
        self._mean_arrays['dsigma_v'] = None
        self._mean_arrays['d'] = None
        self._mean_arrays['dd'] = None

        self._mean_arrays['R1'] = None
        self._mean_arrays['R1_v'] = None
        self._mean_arrays['d1'] = None
        self._mean_arrays['mass'] = None
        self._mean_arrays['d0'] = None

        self._mean_scalar = dict()
        self._mean_scalar['R1'] = None
        self._mean_scalar['R1_v'] = None
        self._mean_scalar['d1'] = None

        self.add_profile(profile, update=True)

    def __call__(self, *args, array=False):
        t = []
        for key in args:
            if key in self._mean_arrays and key in self._mean_scalar:
                if array:
                    t.append(num.nan_to_num(self._mean_arrays[key]))
                else:
                    t.append(num.nan_to_num(self._mean_scalar[key]))
            elif key in self._mean_arrays:
                t.append(num.nan_to_num(self._mean_arrays[key]))
            elif key in self._mean_scalar:
                t.append(num.nan_to_num(self._mean_scalar[key]))
        if len(t) == 1:
            return t[0]
        else:
            return tuple(t)

    def sparsity_array(self, Delta_2, Delta_1=200):
        arr = []
        for profile in self._profiles:
            spar = profile.sparsity(Delta_2, Delta_1)
            if spar is not None:
                arr.append(spar)
        return arr

    def nb_profiles(self):
        return num.size(self._profiles)

    def _get_arrays(self, key):
        l = []
        for profile in self._profiles:
            arr = profile(key)
            if arr is not None:
                l.append(arr)
        return l

    def update_profiles(self):
        if len(self._profiles) > 0:
            self._mean_arrays['r'] = self._profiles[0]('r')
            for key in ['D', 'Dv', 'd', 'sigma_v']:
                arr = num.array(self._get_arrays(key))
                if len(arr) > 0:
                    self._mean_arrays[key] = num.mean(arr, axis=0)
                    if len(arr) > 1:
                        self._mean_arrays['d' + key] = num.std(arr, axis=0)/num.sqrt(len(arr) - 1)
                    else:
                        self._mean_arrays['d' + key] = num.std(arr, axis=0)

            self._mean_scalar['R1'] = solve(self._mean_arrays['r'], self._mean_arrays['D'], 0.0)
            self._mean_scalar['R1_v'] = solve(self._mean_arrays['r'], self._mean_arrays['Dv'], 0.0)
            self._mean_scalar['d1'] = solve(self._mean_arrays['d'], self._mean_arrays['r'], self._mean_scalar['R1'])

            for key in ['R1', 'R1_v', 'd1', 'mass', 'd0']:
                self._mean_arrays[key] = num.asarray(self._get_arrays(key))

    def add_profile(self, profile, update=False):
        if isinstance(profile, DataProfile):
            if len(self._profiles) == 0 or profile('r').all() == self._profiles[-1]('r').all():
                self._profiles.append(profile)
                if update:
                    self.update_profiles()
            else:
                print("impossible to add new profile, 'r' array is not the same.")


class DEUSReader:
    def __init__(self, file_path=None):
        self._file_path = file_path
        self._profiles = []
        self._unit = Unit()

    def label(self, key):
        return self._unit(key)

    def set_file_path(self, file_path):
        self._file_path = file_path

    def get_list_of(self, *args, **kwargs):
        l = []
        for profile in self._profiles:
            res = profile(*args, **kwargs)
            l.append(res)
        ln = num.transpose(num.asarray(l, dtype=num.float))
        if len(ln) == 1:
            return ln[0]
        elif len(ln) > 1:
            return tuple(ln)
        else:
            return None

    def get_averaged_profile_at_R1(self, R1, dR1=None):
        if dR1 is None:
            dR1 = (self._profiles[0]('r')[1] - self._profiles[0]('r')[0])
        dp = DataProfiles()
        for profile in self._profiles:
            if profile('R1') is not None and R1 - dR1 <= profile('R1') <= R1 + dR1:
                dp.add_profile(profile, update=False)
        dp.update_profiles()
        return dp

    def get_all_profiles(self, nb_profiles=-1):
        return self._profiles[:nb_profiles]

    def load_DEUSProfile(self, file_name, nb_profiles=None):
        if isinstance(file_name, list):
            for file in file_name:
                self.load_DEUSProfile(file, False)
        else:
            try:
                file = open(self._file_path + file_name, mode='rb')
                data = file.read()

                # file heading
                h0, a, Wm0, Nc = struct.unpack("fffi", data[:16])
                # cosmo_name = ''.join(num.asarray(struct.unpack("c" * Nc, data[16:16 + Nc])))

                boxlen, npart, isOverDensity, Nprofile, Nradius = struct.unpack("<ii?ii", data[16 + Nc:33 + Nc])

                cosmo = BasicCosmo(Wm0, h0, boxlen, npart, a)

                # radius reading
                r = num.asarray(struct.unpack("f" * (Nradius), data[33 + Nc:33 + Nc + 4 * Nradius]))

                # conversion in Mpc/h
                r *= float(boxlen)
                # initialisation
                self._profiles[:] = []
                simu_infos = dict()
                for key in ('boxlen', 'npart', 'h0', 'Wm0'):
                    simu_infos[key] = locals()[key]

                nb_profiles = min((Nprofile, nb_profiles)) if nb_profiles is not None else Nprofile
                print("loading "+str(nb_profiles)+" random profiles ...", end=" ")
                sys.stdout.flush()

                index_list = random.sample(range(0, Nprofile), nb_profiles)
                start_byte = 33 + Nc + 4 * Nradius
                array_byte_size = 4 * Nradius
                xyz_byte_size = 12
                profile_byte_size = 2 * array_byte_size + xyz_byte_size + 4 if 'DEUSprofile' in file_name else 3 * array_byte_size + xyz_byte_size + 4
                for i in index_list:
                    first_byte = start_byte + i * profile_byte_size
                    x, y, z = num.asarray(struct.unpack("fff", data[first_byte: first_byte + xyz_byte_size]))
                    d0 = (struct.unpack("f", data[first_byte + xyz_byte_size:first_byte + xyz_byte_size + 4]))[0]
                    last_byte = first_byte + xyz_byte_size + 4

                    f_tab = num.asarray(struct.unpack("f" * Nradius, data[last_byte:last_byte + array_byte_size]))
                    last_byte += array_byte_size

                    v_tab = num.asarray(struct.unpack("f" * Nradius,  data[last_byte: last_byte + array_byte_size]))
                    last_byte += array_byte_size

                    if 'DEUSprofile' in file_name:
                        sigma_v_tab = num.zeros_like(v_tab)
                        Delta_tab = f_tab - 1
                    else:
                        sigma_v_tab = num.asarray(struct.unpack("f" * Nradius, data[last_byte: last_byte + array_byte_size]))
                        Delta_tab = f_tab

                    local_profile = DataProfile(r=r, x=x, y=y, z=z, D=Delta_tab, v=v_tab, sigma_v=sigma_v_tab,
                                                mass=d0, cosmo=cosmo, over_density=isOverDensity)

                    self._profiles.append(local_profile)

                print("done. ")
                return True
            except IOError:
                print('\nERROR : no file ' + file_name)
                return False


