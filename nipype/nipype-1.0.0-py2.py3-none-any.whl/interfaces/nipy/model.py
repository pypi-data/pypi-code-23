# -*- coding: utf-8 -*-
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
from builtins import range, str, bytes

import os

import nibabel as nb
import numpy as np

from ...utils.misc import package_check
from ...utils import NUMPY_MMAP

from ..base import (BaseInterface, TraitedSpec, traits, File, OutputMultiPath,
                    BaseInterfaceInputSpec, isdefined)

have_nipy = True
try:
    package_check('nipy')
except Exception as e:
    have_nipy = False
else:
    import nipy.modalities.fmri.design_matrix as dm
    import nipy.modalities.fmri.glm as GLM

if have_nipy:
    try:
        BlockParadigm = dm.BlockParadigm
    except AttributeError:
        from nipy.modalities.fmri.experimental_paradigm import BlockParadigm


class FitGLMInputSpec(BaseInterfaceInputSpec):
    session_info = traits.List(
        minlen=1,
        maxlen=1,
        mandatory=True,
        desc=('Session specific information generated by'
              ' ``modelgen.SpecifyModel``, FitGLM does '
              'not  support multiple runs uless they are '
              'concatenated (see SpecifyModel options)'))
    hrf_model = traits.Enum(
        'Canonical',
        'Canonical With Derivative',
        'FIR',
        desc=("that specifies the hemodynamic reponse "
              "function it can be 'Canonical', 'Canonical "
              "With Derivative' or 'FIR'"),
        usedefault=True)
    drift_model = traits.Enum(
        "Cosine",
        "Polynomial",
        "Blank",
        desc=("string that specifies the desired drift "
              "model, to be chosen among 'Polynomial', "
              "'Cosine', 'Blank'"),
        usedefault=True)
    TR = traits.Float(mandatory=True)
    model = traits.Enum(
        "ar1",
        "spherical",
        desc=("autoregressive mode is available only for the "
              "kalman method"),
        usedefault=True)
    method = traits.Enum(
        "kalman",
        "ols",
        desc=("method to fit the model, ols or kalma; kalman "
              "is more time consuming but it supports "
              "autoregressive model"),
        usedefault=True)
    mask = traits.File(
        exists=True,
        desc=("restrict the fitting only to the region defined "
              "by this mask"))
    normalize_design_matrix = traits.Bool(
        False,
        desc=("normalize (zscore) the "
              "regressors before fitting"),
        usedefault=True)
    save_residuals = traits.Bool(False, usedefault=True)
    plot_design_matrix = traits.Bool(False, usedefault=True)


class FitGLMOutputSpec(TraitedSpec):
    beta = File(exists=True)
    nvbeta = traits.Any()
    s2 = File(exists=True)
    dof = traits.Any()
    constants = traits.Any()
    axis = traits.Any()
    reg_names = traits.List()
    residuals = traits.File()
    a = File(exists=True)


class FitGLM(BaseInterface):
    '''
    Fit GLM model based on the specified design. Supports only single or concatenated runs.
    '''
    input_spec = FitGLMInputSpec
    output_spec = FitGLMOutputSpec

    def _run_interface(self, runtime):

        session_info = self.inputs.session_info

        functional_runs = self.inputs.session_info[0]['scans']
        if isinstance(functional_runs, (str, bytes)):
            functional_runs = [functional_runs]
        nii = nb.load(functional_runs[0])
        data = nii.get_data()

        if isdefined(self.inputs.mask):
            mask = nb.load(self.inputs.mask).get_data() > 0
        else:
            mask = np.ones(nii.shape[:3]) == 1

        timeseries = data.copy()[mask, :]
        del data

        for functional_run in functional_runs[1:]:
            nii = nb.load(functional_run, mmap=NUMPY_MMAP)
            data = nii.get_data()
            npdata = data.copy()
            del data
            timeseries = np.concatenate((timeseries, npdata[mask, :]), axis=1)
            del npdata

        nscans = timeseries.shape[1]

        if 'hpf' in list(session_info[0].keys()):
            hpf = session_info[0]['hpf']
            drift_model = self.inputs.drift_model
        else:
            hpf = 0
            drift_model = "Blank"

        reg_names = []
        for reg in session_info[0]['regress']:
            reg_names.append(reg['name'])

        reg_vals = np.zeros((nscans, len(reg_names)))
        for i in range(len(reg_names)):
            reg_vals[:, i] = np.array(
                session_info[0]['regress'][i]['val']).reshape(1, -1)

        frametimes = np.linspace(0, (nscans - 1) * self.inputs.TR, nscans)

        conditions = []
        onsets = []
        duration = []

        for i, cond in enumerate(session_info[0]['cond']):
            onsets += cond['onset']
            conditions += [cond['name']] * len(cond['onset'])
            if len(cond['duration']) == 1:
                duration += cond['duration'] * len(cond['onset'])
            else:
                duration += cond['duration']

        if conditions:
            paradigm = BlockParadigm(
                con_id=conditions, onset=onsets, duration=duration)
        else:
            paradigm = None
        design_matrix, self._reg_names = dm.dmtx_light(
            frametimes,
            paradigm,
            drift_model=drift_model,
            hfcut=hpf,
            hrf_model=self.inputs.hrf_model,
            add_regs=reg_vals,
            add_reg_names=reg_names)
        if self.inputs.normalize_design_matrix:
            for i in range(len(self._reg_names) - 1):
                design_matrix[:, i] = ((
                    design_matrix[:, i] - design_matrix[:, i].mean()) /
                                       design_matrix[:, i].std())

        if self.inputs.plot_design_matrix:
            import pylab
            pylab.pcolor(design_matrix)
            pylab.savefig("design_matrix.pdf")
            pylab.close()
            pylab.clf()

        glm = GLM.GeneralLinearModel()
        glm.fit(
            timeseries.T,
            design_matrix,
            method=self.inputs.method,
            model=self.inputs.model)

        self._beta_file = os.path.abspath("beta.nii")
        beta = np.zeros(mask.shape + (glm.beta.shape[0], ))
        beta[mask, :] = glm.beta.T
        nb.save(nb.Nifti1Image(beta, nii.affine), self._beta_file)

        self._s2_file = os.path.abspath("s2.nii")
        s2 = np.zeros(mask.shape)
        s2[mask] = glm.s2
        nb.save(nb.Nifti1Image(s2, nii.affine), self._s2_file)

        if self.inputs.save_residuals:
            explained = np.dot(design_matrix, glm.beta)
            residuals = np.zeros(mask.shape + (nscans, ))
            residuals[mask, :] = timeseries - explained.T
            self._residuals_file = os.path.abspath("residuals.nii")
            nb.save(
                nb.Nifti1Image(residuals, nii.affine), self._residuals_file)

        self._nvbeta = glm.nvbeta
        self._dof = glm.dof
        self._constants = glm._constants
        self._axis = glm._axis
        if self.inputs.model == "ar1":
            self._a_file = os.path.abspath("a.nii")
            a = np.zeros(mask.shape)
            a[mask] = glm.a.squeeze()
            nb.save(nb.Nifti1Image(a, nii.affine), self._a_file)
        self._model = glm.model
        self._method = glm.method

        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs["beta"] = self._beta_file
        outputs["nvbeta"] = self._nvbeta
        outputs["s2"] = self._s2_file
        outputs["dof"] = self._dof
        outputs["constants"] = self._constants
        outputs["axis"] = self._axis
        outputs["reg_names"] = self._reg_names
        if self.inputs.model == "ar1":
            outputs["a"] = self._a_file
        if self.inputs.save_residuals:
            outputs["residuals"] = self._residuals_file
        return outputs


class EstimateContrastInputSpec(BaseInterfaceInputSpec):
    contrasts = traits.List(
        traits.Either(
            traits.Tuple(traits.Str, traits.Enum('T'), traits.List(traits.Str),
                         traits.List(traits.Float)),
            traits.Tuple(traits.Str, traits.Enum('T'), traits.List(traits.Str),
                         traits.List(traits.Float), traits.List(traits.Float)),
            traits.Tuple(traits.Str, traits.Enum('F'),
                         traits.List(
                             traits.Either(
                                 traits.Tuple(traits.Str, traits.Enum('T'),
                                              traits.List(traits.Str),
                                              traits.List(traits.Float)),
                                 traits.Tuple(traits.Str, traits.Enum('T'),
                                              traits.List(traits.Str),
                                              traits.List(traits.Float),
                                              traits.List(traits.Float)))))),
        desc="""List of contrasts with each contrast being a list of the form:
            [('name', 'stat', [condition list], [weight list], [session list])]. if
            session list is None or not provided, all sessions are used. For F
            contrasts, the condition list should contain previously defined
            T-contrasts.""",
        mandatory=True)
    beta = File(
        exists=True,
        desc="beta coefficients of the fitted model",
        mandatory=True)
    nvbeta = traits.Any(mandatory=True)
    s2 = File(
        exists=True, desc="squared variance of the residuals", mandatory=True)
    dof = traits.Any(desc="degrees of freedom", mandatory=True)
    constants = traits.Any(mandatory=True)
    axis = traits.Any(mandatory=True)
    reg_names = traits.List(mandatory=True)
    mask = traits.File(exists=True)


class EstimateContrastOutputSpec(TraitedSpec):
    stat_maps = OutputMultiPath(File(exists=True))
    z_maps = OutputMultiPath(File(exists=True))
    p_maps = OutputMultiPath(File(exists=True))


class EstimateContrast(BaseInterface):
    '''
    Estimate contrast of a fitted model.
    '''
    input_spec = EstimateContrastInputSpec
    output_spec = EstimateContrastOutputSpec

    def _run_interface(self, runtime):

        beta_nii = nb.load(self.inputs.beta)
        if isdefined(self.inputs.mask):
            mask = nb.load(self.inputs.mask).get_data() > 0
        else:
            mask = np.ones(beta_nii.shape[:3]) == 1

        glm = GLM.GeneralLinearModel()
        nii = nb.load(self.inputs.beta)
        glm.beta = beta_nii.get_data().copy()[mask, :].T
        glm.nvbeta = self.inputs.nvbeta
        glm.s2 = nb.load(self.inputs.s2).get_data().copy()[mask]
        glm.dof = self.inputs.dof
        glm._axis = self.inputs.axis
        glm._constants = self.inputs.constants

        reg_names = self.inputs.reg_names

        self._stat_maps = []
        self._p_maps = []
        self._z_maps = []
        for contrast_def in self.inputs.contrasts:
            name = contrast_def[0]
            contrast = np.zeros(len(reg_names))

            for i, reg_name in enumerate(reg_names):
                if reg_name in contrast_def[2]:
                    idx = contrast_def[2].index(reg_name)
                    contrast[i] = contrast_def[3][idx]

            est_contrast = glm.contrast(contrast)

            stat_map = np.zeros(mask.shape)
            stat_map[mask] = est_contrast.stat().T
            stat_map_file = os.path.abspath(name + "_stat_map.nii")
            nb.save(nb.Nifti1Image(stat_map, nii.affine), stat_map_file)
            self._stat_maps.append(stat_map_file)

            p_map = np.zeros(mask.shape)
            p_map[mask] = est_contrast.pvalue().T
            p_map_file = os.path.abspath(name + "_p_map.nii")
            nb.save(nb.Nifti1Image(p_map, nii.affine), p_map_file)
            self._p_maps.append(p_map_file)

            z_map = np.zeros(mask.shape)
            z_map[mask] = est_contrast.zscore().T
            z_map_file = os.path.abspath(name + "_z_map.nii")
            nb.save(nb.Nifti1Image(z_map, nii.affine), z_map_file)
            self._z_maps.append(z_map_file)

        return runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs["stat_maps"] = self._stat_maps
        outputs["p_maps"] = self._p_maps
        outputs["z_maps"] = self._z_maps
        return outputs
