"""wolfpass.py is a project example using resources from Wolf Pass"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from numpy import load as npload

from .base import BaseExample, exampleproperty
from ..data import DataArray
from ..line import Line, Mesh1D
from ..point import Mesh0D, Point
from ..project import Project
from ..surface import Mesh2D, Surface
from ..texture import Texture2DImage
from ..volume import Mesh3DGrid, Volume


class Wolfpass(BaseExample):
    """Wolfpass example

    This module provides example data for a geology exploration project.
    """

    @exampleproperty
    def filenames(self):
        return [
            'AG_gpt.line.npy',
            'AS_ppm.line.npy',
            'AU_gpt.line.npy',
            'CU_pct.line.npy',
            'CU_pct.vol.npy',
            'CU_pct_0.75_1.0_t.cusurf.npy',
            'CU_pct_0.75_1.0_v.cusurf.npy',
            'CU_pct_1.0_1.25_t.cusurf.npy',
            'CU_pct_1.0_1.25_v.cusurf.npy',
            'CU_pct_1.25_1.5_t.cusurf.npy',
            'CU_pct_1.25_1.5_v.cusurf.npy',
            'CU_pct_gt_1.5_t.cusurf.npy',
            'CU_pct_gt_1.5_v.cusurf.npy',
            'CU_pct_lt_0.75_t.cusurf.npy',
            'CU_pct_lt_0.75_v.cusurf.npy',
            'Density.line.npy',
            'MO_ppm.line.npy',
            'Recov.line.npy',
            'S_pct.line.npy',
            'basement_t.lithsurf.npy',
            'basement_v.lithsurf.npy',
            'boreholes_s.line.npy',
            'boreholes_v.line.npy',
            'dacite_data.line.npy',
            'dacite_t.lithsurf.npy',
            'dacite_v.lithsurf.npy',
            'diorite_early_t.lithsurf.npy',
            'diorite_early_v.lithsurf.npy',
            'diorite_late_t.lithsurf.npy',
            'diorite_late_v.lithsurf.npy',
            'dist_to_borehole.lithsurf.npy',
            'dist_to_borehole.vol.npy',
            'drill_loc_v.point.npy',
            'elevation.toposurf.npy',
            'lithology.xsurf.npy',
            'maxdepth.point.npy',
            'ovb_t.lithsurf.npy',
            'ovb_v.lithsurf.npy',
            'section_number.xsurf.npy',
            'topo_t.toposurf.npy',
            'topo_v.toposurf.npy',
            'topography.png',
            'trench.point.npy',
            'vol_h1.vol.npy',
            'vol_h2.vol.npy',
            'vol_h3.vol.npy',
            'vol_x0.vol.npy',
            'xsect_t.xsurf.npy',
            'xsect_v.xsurf.npy',
        ]

    @exampleproperty
    def drill_vertices(self):
        """drill point vertices"""
        return npload(Wolfpass.fetch_data(filename='drill_loc_v.point.npy',
                                          download_if_missing=False,
                                          verbose=False))

    @exampleproperty
    def drill_data(self):
        """dictionry of drill point data"""
        if getattr(self, '_drill_data', None) is None:
            self._drill_data = dict()
            for npyfile in self.filenames:
                if not npyfile.endswith('.point.npy'):
                    continue
                if npyfile.endswith('_v.point.npy'):
                    continue
                self._drill_data[npyfile.split('.')[0]] = npload(
                    Wolfpass.fetch_data(filename=npyfile,
                                        download_if_missing=False,
                                        verbose=False)
                )
        return self._drill_data

    @exampleproperty
    def borehole_vertices(self):
        """borehole line vertices"""
        return npload(Wolfpass.fetch_data(filename='boreholes_v.line.npy',
                                          download_if_missing=False,
                                          verbose=False))

    @exampleproperty
    def borehole_segments(self):
        """borehole segment vertex indices"""
        return npload(Wolfpass.fetch_data(filename='boreholes_s.line.npy',
                                          download_if_missing=False,
                                          verbose=False))

    @exampleproperty
    def borehole_data(self):
        """dictionary of borehole data"""
        if getattr(self, '_borehole_data', None) is None:
            self._borehole_data = dict()
            for npyfile in self.filenames:
                if not npyfile.endswith('.line.npy'):
                    continue
                if (npyfile.endswith('_v.line.npy') or
                        npyfile.endswith('_s.line.npy')):
                    continue
                self._borehole_data[npyfile.split('.')[0]] = npload(
                    Wolfpass.fetch_data(filename=npyfile,
                                        download_if_missing=False,
                                        verbose=False)
                )
        return self._borehole_data

    @exampleproperty
    def cu_names(self):
        """list of names for the different cu pct surfaces"""
        return [fname[:-13] for fname in self.filenames
                if fname.endswith('_v.cusurf.npy')]

    @exampleproperty
    def cu_vertices(self):
        """list of cu pct surface vertices"""
        return [npload(Wolfpass.fetch_data(filename=prefix + '_v.cusurf.npy',
                                           download_if_missing=False,
                                           verbose=False))
                for prefix in self.cu_names]

    @exampleproperty
    def cu_triangles(self):
        """list of cu pct surface triangles"""
        return [npload(Wolfpass.fetch_data(filename=prefix + '_t.cusurf.npy',
                                           download_if_missing=False,
                                           verbose=False))
                for prefix in self.cu_names]

    @exampleproperty
    def lith_names(self):
        """list of names for the different lithology surfaces"""
        return [fname[:-15] for fname in self.filenames
                if fname.endswith('_v.lithsurf.npy')]

    @exampleproperty
    def lith_vertices(self):
        """list of lithology surface vertices"""
        return [npload(Wolfpass.fetch_data(filename=prefix + '_v.lithsurf.npy',
                                           download_if_missing=False,
                                           verbose=False))
                for prefix in self.lith_names]

    @exampleproperty
    def lith_triangles(self):
        """list of lithology surface triangles"""
        return [npload(Wolfpass.fetch_data(filename=prefix + '_t.lithsurf.npy',
                                           download_if_missing=False,
                                           verbose=False))
                for prefix in self.lith_names]

    @exampleproperty
    def lith_diorite_early_data(self):
        """data for early diorite surface"""
        return npload(Wolfpass.fetch_data(
            filename='dist_to_borehole.lithsurf.npy',
            download_if_missing=False,
            verbose=False
        ))

    @exampleproperty
    def topo_vertices(self):
        """topography vertices"""
        return npload(Wolfpass.fetch_data(filename='topo_v.toposurf.npy',
                                          download_if_missing=False,
                                          verbose=False))

    @exampleproperty
    def topo_triangles(self):
        """topography triangles"""
        return npload(Wolfpass.fetch_data(filename='topo_t.toposurf.npy',
                                          download_if_missing=False,
                                          verbose=False))

    @exampleproperty
    def topo_image(self):
        """surface image PNG"""
        return Wolfpass.fetch_data(filename='topography.png',
                                   download_if_missing=False,
                                   verbose=False)

    @exampleproperty
    def topo_image_orientation(self):
        """surface image O, U, and V"""
        return dict(
            O=[443200., 491750, 0],
            U=[4425., 0, 0],
            V=[0., 3690, 0]
        )

    @exampleproperty
    def topo_data(self):
        """elevation data"""
        return npload(Wolfpass.fetch_data(filename='elevation.toposurf.npy',
                                          download_if_missing=False,
                                          verbose=False))

    @exampleproperty
    def xsect_vertices(self):
        """cross section vertices"""
        return npload(Wolfpass.fetch_data(filename='xsect_v.xsurf.npy',
                                          download_if_missing=False,
                                          verbose=False))

    @exampleproperty
    def xsect_triangles(self):
        """cross section triangles"""
        return npload(Wolfpass.fetch_data(filename='xsect_t.xsurf.npy',
                                          download_if_missing=False,
                                          verbose=False))

    @exampleproperty
    def xsect_data(self):
        """dictionary of cross section data"""
        if getattr(self, '_xsect_data', None) is None:
            self._xsect_data = dict()
            for npyfile in self.filenames:
                if not npyfile.endswith('.xsurf.npy'):
                    continue
                if (npyfile.endswith('_v.xsurf.npy') or
                        npyfile.endswith('_t.xsurf.npy')):
                    continue
                self._xsect_data[npyfile.split('.')[0]] = npload(
                    Wolfpass.fetch_data(filename=npyfile,
                                        download_if_missing=False,
                                        verbose=False)
                )
        return self._xsect_data

    @exampleproperty
    def lith_tensor(self):
        """h1, h2, h3 dictionary for lith volume"""
        return dict(
            h1=npload(Wolfpass.fetch_data(filename='vol_h1.vol.npy',
                                          download_if_missing=False,
                                          verbose=False)),
            h2=npload(Wolfpass.fetch_data(filename='vol_h2.vol.npy',
                                          download_if_missing=False,
                                          verbose=False)),
            h3=npload(Wolfpass.fetch_data(filename='vol_h3.vol.npy',
                                          download_if_missing=False,
                                          verbose=False))
        )

    @exampleproperty
    def lith_origin(self):
        """x0 for lith volume"""
        return npload(Wolfpass.fetch_data(filename='vol_x0.vol.npy',
                                          download_if_missing=False,
                                          verbose=False))

    @exampleproperty
    def lith_data(self):
        """dictionary of data for lith volume"""
        if getattr(self, '_lith_data', None) is None:
            self._lith_data = dict()
            for npyfile in self.filenames:
                if not npyfile.endswith('.vol.npy'):
                    continue
                if npyfile.startswith('vol_'):
                    continue
                self._lith_data[npyfile.split('.')[0]] = npload(
                    Wolfpass.fetch_data(filename=npyfile,
                                        download_if_missing=False,
                                        verbose=False)
                ).flatten()
        return self._lith_data

    @classmethod
    def get_project(self):
        """Return a project with all the Wolf Pass data"""
        proj = Project(
            title='Wolf Pass'
        )
        self._add_points(proj)
        self._add_lines(proj)
        self._add_cu_surf(proj)
        self._add_lith_surf(proj)
        self._add_topo(proj)
        self._add_xsect(proj)
        self._add_lith_vol(proj)
        return proj

    @classmethod
    def get_project_topo(self):
        """Return a project with Wolf Pass topography data"""
        proj = Project(
            title='Topography',
            description='Topography, surface imagery, and drill locations'
        )
        self._add_points(proj)
        self._add_topo(proj)
        return proj

    @classmethod
    def get_project_dacite(self):
        """Return a project with Wolf Pass dacite data"""
        proj = Project(
            title='Wolf Pass',
            description='Boreholes and dacite formation'
        )
        self._add_lines(proj)
        self._add_lith_surf(proj, ['ovb', 'dacite'])
        return proj

    @classmethod
    def _add_points(self, proj):
        Point(
            project=proj,
            mesh=Mesh0D(
                vertices=self.drill_vertices
            ),
            data=[
                dict(
                    location='N',
                    data=DataArray(
                        title=k,
                        array=self.drill_data[k]
                    )
                ) for k in self.drill_data
            ],
            title='Borehole Drill Locations'
        )

    @classmethod
    def _add_lines(self, proj):
        Line(
            project=proj,
            mesh=Mesh1D(
                vertices=self.borehole_vertices,
                segments=self.borehole_segments
            ),
            data=[
                dict(
                    location='CC',
                    data=DataArray(
                        title=k,
                        array=self.borehole_data[k]
                    )
                ) for k in self.borehole_data
            ],
            title='Boreholes'
        )

    @classmethod
    def _add_cu_surf(self, proj):
        for i, prefix in enumerate(self.cu_names):
            Surface(
                project=proj,
                mesh=Mesh2D(
                    vertices=self.cu_vertices[i],
                    triangles=self.cu_triangles[i]
                ),
                title=prefix
            )

    @classmethod
    def _add_lith_surf(self, proj, include=None):
        for i, prefix in enumerate(self.lith_names):
            if include is not None and prefix not in include:
                continue
            if prefix == 'diorite_early':
                lith_data = [dict(
                                location='N',
                                data=DataArray(
                                    title='Distance to Borehole',
                                    array=self.lith_diorite_early_data
                                )
                            )]
            else:
                lith_data = []
            Surface(
                project=proj,
                mesh=Mesh2D(
                    vertices=self.lith_vertices[i],
                    triangles=self.lith_triangles[i]
                ),
                data=lith_data,
                title=prefix
            )

    @classmethod
    def _add_topo(self, proj):
        Surface(
            project=proj,
            mesh=Mesh2D(
                vertices=self.topo_vertices,
                triangles=self.topo_triangles
            ),
            data=dict(
                location='N',
                data=DataArray(
                    title='Elevation',
                    array=self.topo_data
                )
            ),
            textures=Texture2DImage(
                image=self.topo_image,
                **self.topo_image_orientation
            ),
            title='Topography Surface'
        )

    @classmethod
    def _add_xsect(self, proj):
        Surface(
            project=proj,
            mesh=Mesh2D(
                vertices=self.xsect_vertices,
                triangles=self.xsect_triangles
            ),
            data=[
                dict(
                    location='CC',
                    data=DataArray(
                        title=k,
                        array=self.xsect_data[k]
                    )
                ) for k in self.xsect_data
            ],
            title='Cross-Sections'
        )

    @classmethod
    def _add_lith_vol(self, proj):
        Volume(
            project=proj,
            mesh=Mesh3DGrid(
                x0=self.lith_origin,
                **self.lith_tensor
            ),
            data=[
                dict(
                    location='CC',
                    data=DataArray(
                        title=k,
                        array=self.lith_data[k]
                    )
                ) for k in self.lith_data
            ],
            title='Lithology Volume'
        )
