# BSD 3-Clause License
# 
# Copyright (c) 2018, Tai Sakuma
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# 
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# 
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

##__________________________________________________________________||
import numpy as np

__all__ = ['AltDphi']

##__________________________________________________________________||
class cache_once_property(object):
    """A property decorator that replaces the property with the value that
    the property returns.

    inspired by
    https://stackoverflow.com/questions/4037481/caching-attributes-of-classes-in-python#answer-4037979

    """
    
    def __init__(self, f):
        self.f = f

    def __get__(self, instance, owner):
        val = self.f(instance)
        setattr(instance, self.f.__name__, val)
        return val

##__________________________________________________________________||
class AltDphi(object):

    varnames_main = (
        'pt', 'phi',
        'mht', 'mht_phi',
        'max_f',
        'min_omega_tilde',
        'min_omega_hat',
        'min_chi',
        'min_dphi_star',
        'xi',
        'min_minimized_mht', 'min_X',
        'f', 'dphi',
        'omega','omega_tilde', 'omega_hat', 'chi',
        'dphi_star',
        'sin_dphi_tilde', 'g',
        'minimized_mht',
        'X',
        )

    varnames_intermediate = (
        'px', 'py',
        'mht_x', 'mht_y',
        'min_omega',
        'min_dphi_tilde', 'min_sin_dphi_tilde',
        'min_tan_chi',
        'max_h',
        'cos_dphi', 'sin_dphi',
        'arccot_f',
        'dphi_tilde',
        'sin_dphi_hat', 'dphi_hat',
        'k',
        'tan_chi',
        'h',
    )
    varnames = varnames_main + varnames_intermediate

    def __init__(self, pt, phi, mht=None, mht_phi=None):
        self._repr = self._compose_repr(pt, phi, mht, mht_phi)
        self.pt = pt
        self.phi = phi

        self.monojet_is_minus_mht = mht is None and pt.size == 1

        if mht is not None:
            self.mht = mht
            self.mht_x = mht*np.cos(mht_phi)
            self.mht_y = mht*np.sin(mht_phi)

    ##______________________________________________________________||
    @cache_once_property
    def mht_x(self):
        return -np.sum(self.px)

    @cache_once_property
    def mht_y(self):
        return -np.sum(self.py)

    @cache_once_property
    def mht(self):
        if self.monojet_is_minus_mht:
            ## make mht and pt precisely the same for monojet
            return self.pt[0]
        return np.sqrt(self.mht_x**2 + self.mht_y**2)

    @cache_once_property
    def mht_phi(self):
        return np.arctan2(self.mht_y, self.mht_x)

    ##______________________________________________________________||
    @cache_once_property
    def min_omega_tilde(self):
        if self.omega_tilde.size == 0:
            return np.nan
        return self.omega_tilde.min()

    @cache_once_property
    def min_omega_hat(self):
        if self.omega_hat.size == 0:
            return np.nan
        return self.omega_hat.min()

    @cache_once_property
    def min_chi(self):
        if self.chi.size == 0:
            return np.nan
        return self.chi.min()

    @cache_once_property
    def xi(self):
        if np.isnan(self.min_sin_dphi_tilde):
            return np.nan
        if self.monojet_is_minus_mht:
            return np.pi/2
        return np.arctan2(self.min_sin_dphi_tilde, self.max_h)

    ##______________________________________________________________||
    @cache_once_property
    def minimized_mht(self):
        return self.mht*self.sin_dphi_tilde

    @cache_once_property
    def min_minimized_mht(self):
        return self.mht*self.min_sin_dphi_tilde

    ##______________________________________________________________||
    @cache_once_property
    def X(self):
        return self.mht*self.tan_chi

    ##______________________________________________________________||
    @cache_once_property
    def min_X(self):
        return self.mht*self.min_tan_chi

    ##______________________________________________________________||
    @cache_once_property
    def min_dphi_star(self):
        if self.dphi_star.size == 0:
            return np.nan
        return self.dphi_star.min()

    @cache_once_property
    def min_omega(self):
        if self.omega.size == 0:
            return np.nan
        return self.omega.min()

    @cache_once_property
    def min_dphi_tilde(self):
        if self.dphi_tilde.size == 0:
            return np.nan
        return self.dphi_tilde.min()

    @cache_once_property
    def min_sin_dphi_tilde(self):
        if self.sin_dphi_tilde.size == 0:
            return np.nan
        return self.sin_dphi_tilde.min()

    @cache_once_property
    def max_f(self):
        if self.f.size == 0:
            return np.nan
        return self.f.max()

    @cache_once_property
    def min_tan_chi(self):
        if self.tan_chi.size == 0:
            return np.nan
        return self.tan_chi.min()

    @cache_once_property
    def max_h(self):
        if self.h.size == 0:
            return np.nan
        return self.h.max()

    ##______________________________________________________________||
    @cache_once_property
    def px(self):
        return self.pt*np.cos(self.phi)

    @cache_once_property
    def py(self):
        return self.pt*np.sin(self.phi)

    ##______________________________________________________________||
    @cache_once_property
    def cos_dphi(self):
        if self.monojet_is_minus_mht:
            return np.array([-1.0])
        ret = (self.mht_x*self.px + self.mht_y*self.py)/(self.mht*self.pt)
        ret = np.minimum(ret, 1.0)
        ret = np.maximum(ret, -1.0)
        return ret

    @cache_once_property
    def sin_dphi(self):
        return np.sqrt(1 - self.cos_dphi**2)

    @cache_once_property
    def dphi(self):
        return np.arccos(self.cos_dphi)

    @cache_once_property
    def f(self):
        return self.pt/self.mht

    @cache_once_property
    def arccot_f(self):
        return np.arctan2(1, self.f)

    ##______________________________________________________________||
    @cache_once_property
    def dphi_star(self):
        ret = np.where(
            (self.f == 1) & (self.cos_dphi == -1),
            np.pi/2,
            np.arctan2(self.sin_dphi, self.f + self.cos_dphi)
        )
        return ret

    ##______________________________________________________________||
    @cache_once_property
    def sin_dphi_tilde(self):
        return np.sqrt(1 + (self.g - self.f)**2 - 2*(self.g - self.f)*self.cos_dphi)

    @cache_once_property
    def dphi_tilde(self):
        return np.where(
            self.f + self.cos_dphi >= 0,
            self.dphi,
            np.pi - np.arcsin(self.sin_dphi_tilde)
        )

    @cache_once_property
    def g(self):
        return np.maximum(self.f + self.cos_dphi, 0)

    ##______________________________________________________________||
    @cache_once_property
    def omega(self):
        return np.arctan2(self.sin_dphi, self.f)

    ##______________________________________________________________||
    @cache_once_property
    def omega_tilde(self):
        return np.arctan2(self.sin_dphi_tilde, self.f)

    ##______________________________________________________________||
    @cache_once_property
    def dphi_hat(self):
        return np.minimum(self.dphi, np.pi/2.0)

    @cache_once_property
    def sin_dphi_hat(self):
        return np.sin(self.dphi_hat)

    @cache_once_property
    def omega_hat(self):
        return np.arctan2(self.sin_dphi_hat, self.f)

    ##______________________________________________________________||
    @cache_once_property
    def k(self):
        return np.minimum(self.f, self.g)

    @cache_once_property
    def chi(self):
        ret = np.where(
            (self.f == 1) & (self.cos_dphi == -1),
            np.pi/2,
            np.arctan2(self.sin_dphi_tilde, self.k)
        )
        return ret

    @cache_once_property
    def tan_chi(self):
        return np.tan(self.chi)

    ##______________________________________________________________||
    @cache_once_property
    def h(self):
        if self.sin_dphi_tilde.size == 0:
            return np.array([ ])
        return np.where(
            self.sin_dphi_tilde == self.sin_dphi_tilde.min(),
            self.g, self.f
        )

    ##______________________________________________________________||
    def __repr__(self):
        return self._repr

    def __str__(self):
        return self.to_string()

    def to_string(self, all = False):
        ret = '{!r}:'.format(self) + '\n'

        varnames = self.varnames if all else self.varnames_main
        len_varname = max(len(n) for n in varnames)
        ret = ret + '\n'.join(
            ['    {:>{}}: {}'.format(n, len_varname, str(getattr(self, n))) for n in varnames]
        )
        return ret

    def _compose_repr(self, pt, phi, mht, mht_phi):
        name_value_pairs = [('pt', pt), ('phi', phi)]
        if mht is not None:
            name_value_pairs.append(('mht', mht))
        if mht_phi is not None:
            name_value_pairs.append(('mht_phi', mht_phi))
        return '{}({})'.format(
            self.__class__.__name__,
            ', '.join(['{}={!r}'.format(n, v) for n, v in name_value_pairs]),
        )

##__________________________________________________________________||
