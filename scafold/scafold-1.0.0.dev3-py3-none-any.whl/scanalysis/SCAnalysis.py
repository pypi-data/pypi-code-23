import os
import urllib.request
from math import log, fabs

import numpy as np
from ipywidgets.embed import embed_snippet
from numpy import amax, extract, zeros, dot, outer
from scipy.stats import norm
from scipy.cluster.hierarchy import linkage, fclusterdata
from sklearn.metrics import silhouette_score
from skbio import TabularMSA, Protein
from skbio.alignment import local_pairwise_align_ssw
from skbio.alignment._pairwise import blosum50
from Bio.PDB.PDBParser import PDBParser
from Bio.PDB.Polypeptide import PPBuilder
import plotly.offline as py
import plotly.graph_objs as go
import plotly.figure_factory as FF
import nglview as nv

class MSA(object):
    """Store multiple sequence alignment data and associated metadata.
    
    Parameters
    ----------
    aln_dir : str
        Name of the text file containing a multiple sequence alignment.
        supports 'clustal' or 'fasta' file formats.
    truncate_idx : positive int
        Index of the master sequence in the alignment. Will delete all
        positions in the multiple sequence alignment for which the master
        sequence has a gap.
    percent_gap : float between 0 and 1, optional
        The threshold of gap percentage for removing a position from the
        alignment. For example, if percent_gap = 0.2, will remove all
        positions that contain more than 20% gaps. Default is 1.
    pdb_id : str, optional
        The pdb id for the master sequence. Will use the id to extract
        the structure from RCSB Protein Data Bank.
    """
    def __init__(self, aln_dir, truncate_idx, percent_gap=1, pdb_id=None):
        aln = TabularMSA.read(aln_dir, constructor=Protein)
        if aln_dir.lower().endswith('.fasta'):
            aln.reassign_index(minter='id')
            
        trunc_aln = self._truncate_algn(aln, truncate_idx)
        filtered_aln, map_idx = self._filter_gaps(
            trunc_aln, truncate_idx, percent_gap)
        self.aln = filtered_aln
        
        if pdb_id is not None:
            algned_idx, chain = self._algn_to_structure(
                pdb_id, truncate_idx, map_idx, trunc_aln)
            self.idx = algned_idx
            self.chain = chain
        else:
            self.idx = map_idx
            self.chain = None
    
    # Alignment Processing
    def _truncate_algn(self, aln, truncate_idx):
        """Remove positions where the master sequence has a gap.
        """
        gap = np.full(aln.shape[1], True, dtype=bool)
        for i in range(aln.shape[1]):
            if str(aln[truncate_idx - 1][i]) == '-':
                gap[i] = False
        trunc_aln = aln[:, gap]
        
        return trunc_aln
    
    def _filter_gaps(self, aln, truncate_idx, percent_gap):
        """Remove positions with more than a specified percentage of gap
        occurance.
        """
        gap_frequencies = aln.gap_frequencies(relative=True)
        filtered_aln = aln[:, gap_frequencies <= percent_gap]
        idx = np.where(gap_frequencies <= percent_gap)[0] + 1
        
        map_idx = []
        for i in range(len(idx)):
            map_idx.append((idx[i], str(filtered_aln[truncate_idx - 1])[i]))
                    
        return (filtered_aln, map_idx)
    
    def _algn_to_structure(self, pdb_id, truncate_idx, map_idx, trunc_aln):
        """Align the master sequence to its structure retrieved from the
        PDB server.
        """
        if not os.path.exists('PDB'): os.mkdir('PDB')
        
        urllib.request.urlretrieve(
            'http://files.rcsb.org/download/{}.pdb1'.format(pdb_id),
            'PDB/{}.pdb'.format(pdb_id)
        )
        
        structure = PDBParser(QUIET=True).get_structure(
            pdb_id, 'PDB/{}.pdb'.format(pdb_id)
        )
        
        seq = trunc_aln[truncate_idx - 1]
        
        algns = {}
        for chain in structure[0]:
            pps = PPBuilder().build_peptides(chain)
            pdb_sequence = ''
            for pp in pps:
                pdb_sequence = pdb_sequence + str(pp.get_sequence())
                
            if pdb_sequence != '':
                pdb_seq = Protein(pdb_sequence)
                alignment = local_pairwise_align_ssw(
                    seq, pdb_seq, protein = True,
                    substitution_matrix = blosum50
                )
                
                pp_hf, pp_idx, pp_ic = pps[0][0].get_id()
                algn, score, algn_idx = alignment
                loc_idx, glo_idx = algn_idx
                idx = (pp_idx - 1) + glo_idx[0] - loc_idx[0]
                algns[(chain.id, idx)] = score
                
        max_score = max(algns.values())
        algn = [k for (k,v) in algns.items() if v == max_score]
        
        algned_idx = []
        for i, r in map_idx:
            algned_idx.append((i+algn[0][1], r))
            
        return (algned_idx, algn[0][0])

class SCA(object):
    
    def __init__(self, msa, max_ev=None, pdb_id=None,
                 weight_m=None, weighted_freq=None):
        
        self.msa = msa
        self.max_ev = max_ev
        self.pdb_id = pdb_id
        
        self.tensor = None
        self.weight_m = weight_m
        self.weighted_freq = weighted_freq
        
        self.covariance_p = None
        self.covariance_clean = None
        self.covariance_cluster = None
        
        self.eig = None
        self.eig_rnd = None
        
        self.sig_sec = None
        self.sorted_secs = None
        self.sectors = None
        self.view = None
        
        if type(self.msa) is MSA:
            self._calc_sca()
        
    @classmethod
    def read(cls, msa_dir, truncate_idx, percent_gap=1,
             max_ev=None, pdb_id=None):
        msa = MSA(msa_dir, truncate_idx, percent_gap, pdb_id)
        return cls(msa, max_ev=max_ev, pdb_id=pdb_id)
        
    def plot_conservation(self, pynb = True):
        positional_conservation = self.msa.aln.conservation(
            metric='inverse_shannon_uncertainty',
            degenerate_mode='nan',
            gap_mode='include')
        
        res = np.array([i for (i,r) in self.msa.idx]).astype('object')
        all_res = np.array(range(min(res), max(res))).astype('object')
        res_idx = np.where(np.in1d(all_res, res))[0]
        mask = np.full(all_res.shape, True, dtype=bool)
        mask[res_idx] = False
        all_res[mask] = np.nan
        
        trace = go.Scatter(
            x = list(all_res),
            y = positional_conservation.tolist()
        )
        
        layout = go.Layout(
            height = 500,
            width = 1000,
        )
        
        fig = go.Figure(data=[trace], layout=layout)
        
        if pynb:
            py.iplot(fig)
        else:
            return py.plot(fig, include_plotlyjs=False, output_type='div')
    
    def _calc_sca(self, type='msa', aln=None):
        if type == 'msa' and aln is None:
            tensor = self._tensor_rep(self.msa.aln)
        elif type == 'arr' and aln is not None:
            tensor = self._tensor_rep(aln, seq_id = False, lst = True)
        self.tensor = tensor
        
        if type == 'msa':
            back_freq = self._bg_freq()
            freq_aa = self._aa_freq()
            weight_m = self._weight_matrix(back_freq, freq_aa)
            self.weight_m = weight_m
            weighted_freq = self._weight_freq(weight_m, freq_aa)
            self.weighted_freq = weighted_freq
        
        weighted_tesnor = self._weight_tensor(self.weight_m)            
        
        projected_aln = self._project_aln(weighted_tesnor, self.weighted_freq)
        
        covariance_p = self._covariance(projected_aln)
        self.covariance_p = covariance_p
        
    # SCA calculations
    # Step 1: conversion of the MSA to a 3d tensor
    def _tensor_rep(self, aln, seq_id = True, lst = False):
        code = {'A': 0, 'C': 1, 'D': 2, 'E': 3, 'F': 4,
                'G': 5, 'H': 6, 'I': 7, 'K': 8, 'L': 9,
                'M': 10, 'N': 11, 'P': 12, 'Q': 13, 'R': 14,
                'S': 15, 'T': 16, 'V': 17, 'W': 18, 'Y': 19}
        tensor = {}
        
        for s in range(len(aln)):
            m_seq = np.zeros(shape=(len(code), aln.shape[1]))
            if lst is False:
                seq_list = list(str(aln[s]))
            else:
                seq_list = aln[s]
            
            for i in range(len(seq_list)):
                if seq_list[i] in code:
                    m_seq[code[seq_list[i]], i] = 1
            
            if seq_id:
                seq = aln[s].metadata['id']            
            else:
                seq = 'seq' + str(s)
                
            tensor[seq] = m_seq
            del m_seq
        
        return tensor
    
    # Step 2: calculation of the weight matrix and the weighted 3d tensor
    # 1) calculate background frequencies
    def _bg_freq(self):
        aa_code = 'ACDEFGHIKLMNPQRSTVWY'
        aa_count = dict.fromkeys(aa_code, 0)
        
        for seq in self.msa.aln:
            for aa in aa_code:
                aa_count[aa] = aa_count[aa] + str(seq).count(aa)
            
        bg_freq = {}
        count = sum(aa_count.values())
        
        for key, value in aa_count.items():
            bg_freq[key] = value / count
            
        back_freq = [bg_freq[key] for key in sorted(bg_freq)]
        
        return back_freq
    
    # 2) calculate the frequencies of amino acids at each position
    def _aa_freq(self):
        n_seq = len(self.tensor)
        freq = sum(self.tensor.values()) / n_seq
        
        return freq
    
    # 3) compute the weight matrix
    def _weight_matrix(self, back_freq, freq_aa):
        weight_m = np.ones(shape = freq_aa.shape)
        
        for a in range(freq_aa.shape[0]):
            for i in range(freq_aa.shape[1]):
                if freq_aa[a][i] > 0 and freq_aa[a][i] < 1:
                    weight_m[a][i] = fabs(
                        log((freq_aa[a][i] * (1. - back_freq[a]))
                            / (back_freq[a] * (1. - freq_aa[a][i])))
                        )
                    
        return weight_m
    
    # 4) compute the weighted 3d tensor
    def _weight_tensor(self, weight_m):
        weighted_tensor = {}
        
        for key, value in self.tensor.items():
            weighted_tensor[key] = value * weight_m
            
        return weighted_tensor
    
    # Step 3: calculation of the 2D "projected" alignment matrix
    # 1) calculate weighted frequencies of aa at each position
    def _weight_freq(self, weight_m, freq_aa):
        weighted_freq = weight_m * freq_aa
        normalized_freq = np.zeros(shape = weighted_freq.shape)
        
        for i in range(weighted_freq.shape[1]):
            norm = np.linalg.norm(weighted_freq[:,i])
            if norm > 0:
                normalized_freq[:,i] = weighted_freq[:,i] / norm
            
        return normalized_freq
    
    # 2) calculating the 2D "projected" alignment matrix
    def _project_aln(self, weighted_tensor, weighted_freq):
        projected_aln = {}
        for key, value in weighted_tensor.items():
            weighted_val = value * weighted_freq
            projected_aln[key] = np.sum(weighted_val, axis=0)
        
        return projected_aln
    
    def _covariance(self, projected_aln):
        matrix = np.array(list(projected_aln.values()))
        matrix_T = np.transpose(matrix)
        mean = np.mean(matrix, axis=0)
        n_seq = matrix.shape[0]
        covariance_p = np.absolute(np.dot(matrix_T, matrix) / n_seq
                                   - outer(mean, mean))
        
        return covariance_p
    
    # Visualization of the SCA matrix
    def plot_covariance(self, m_type='raw', pynb=True):
        
        if m_type == 'raw':
            #title = 'Heatmap visualization of SCA matrix'
            covariance = self.covariance_p
            label = [str(r)+str(i) for i,r in self.msa.idx]
        elif m_type == 'clean':
            #title = 'Heatmap visualization of cleaned SCA matrix'
            covariance = self.covariance_clean
            label = [str(r)+str(i) for i,r in self.msa.idx]
        elif m_type == 'clustered':
            #title = 'Heatmap visualization of SCA sectors'
            covariance = self.covariance_cluster
            res = [j for i in list(self.sectors.values()) for j in i]
            label = ['{}{}'.format(r,i) for i,r in res]
        
        data = [
            go.Heatmap(
                x = label,
                y = label,
                z = covariance,
                zmin = 0,
                zmax = 2,
                colorscale = 'Viridis'
            )
        ]
        
        layout = go.Layout(
            #title = title,
            xaxis = dict(showgrid = False, zeroline = False,
                             showticklabels = False, ticks = ''),
            yaxis = dict(showgrid = False, zeroline = False,
                             showticklabels = False, ticks = '',
                             autorange = 'reversed'),
            width = len(covariance) + 350,
            height = len(covariance) + 350
        )
        
        fig = go.Figure(data=data, layout=layout)
        
        if pynb:
            py.iplot(fig)
        else:
            return py.plot(fig, include_plotlyjs=False, output_type='div')
    
    # Spectral cleaning
    def clean_spectrum(self, hist=True):
        eig_vals, eig_vecs, loadings = self._eig_decom()
        self.eig = (eig_vals, eig_vecs, loadings)
        
        eigval_rnd, eigvec_rnd, loadings_rnd = self._rnd_sampling()
        self.eig_rnd = (eigval_rnd, eigvec_rnd, loadings_rnd)
        
        if hist:
            self.hist_eigval()
        
        covariance_clean = self._clean_sca(eig_vals, eig_vecs, eigval_rnd)
        self.covariance_clean = covariance_clean
            
    # eigenvalue decomposition
    def _eig_decom(self):
        eig_vals, eig_vecs = np.linalg.eigh(self.covariance_p)
        idx = eig_vals.argsort()[::-1]
        eig_vals = eig_vals[idx]
        eig_vecs = eig_vecs[:, idx]
        num_pos = (eig_vals >= 0).sum()
        eig_vecs[:, num_pos:] = np.zeros(eig_vecs[:, num_pos:].shape)
        eig_vals[num_pos:] = np.zeros(eig_vals[num_pos:].shape)
        loadings = eig_vecs * np.sqrt(eig_vals)
        
        return (eig_vals, eig_vecs, loadings)
    
    # Sample 100 randomly scrambled alignments: shuffle aas for each position
    # over the alignment
    # 1) shuffle the filtered msa
    def _shuffle_msa(self):
        msa_lst = []
        
        for seq in self.msa.aln:
            msa_lst.append(list(str(seq)))
        
        msa_arr = np.array(msa_lst)
        
        for i in range(msa_arr.shape[1]):
            np.random.shuffle(msa_arr[:,i])
            
        return msa_arr
    
    # 2) calculate the SCA matrics for the shuffled msas
    def _rnd_sampling(self):
        n_samples = 100
        eigval_lst = []
        eigvec_lst = []
        loadings_lst = []
        
        for i in range(n_samples):
            rnd_msa = self._shuffle_msa()
            rnd_sca = SCA(rnd_msa, weight_m=self.weight_m,
                          weighted_freq=self.weighted_freq)
            rnd_sca._calc_sca(type='arr',aln=rnd_msa)
            eig_vals, eig_vecs, loadings = rnd_sca._eig_decom()
            eigval_lst.append(eig_vals)
            eigvec_lst.append(eig_vecs)
            loadings_lst.append(loadings)
                    
        eigval_rnd = np.array(eigval_lst)
        eigvec_rnd = np.array(eigvec_lst)
        loadings_rnd = np.array(loadings_lst)
        
        return (eigval_rnd, eigvec_rnd, loadings_rnd)
    
    # histogram comparing the eigenvalue distribution of the actual alignment
    # and randomized alignments
    # percentage rather than actual count is used to scale the 100 randomized
    # alignments for comparison
    def hist_eigval(self, pynb=True):
        eigval_rnd, eigvec_rnd, loadings_rnd = self.eig_rnd
        eig_vals, eig_vecs, loadings = self.eig
        
        trace1 = go.Histogram(
            name = 'actual alignment',
            y = eig_vals,
            opacity = 0.6,
            autobiny = False,
            ybins = dict(
                start = -0.5,
                end = 30,
                size = 1
            ),
            histnorm = 'probability'
        )
        
        trace2 = go.Histogram(
            name = 'randomized alignments',
            y = eigval_rnd.ravel(),
            opacity = 0.6,
            autobiny = False,
            ybins = dict(
                start = -0.5,
                end = 30,
                size = 1
            ),
            histnorm = 'probability'
        )
        
        layout = go.Layout(
            barmode = 'overlay',
            height = 500,
            width = 1000,
            xaxis = dict(
                title = 'Percentage',
                side = 'top'
            ),
            yaxis = dict(
                title = 'Eigenvalues',
                autorange = 'reversed'
            )
        )
        
        data = [trace1, trace2]
        fig = go.Figure(data=data, layout=layout)
        
        if pynb:
            py.iplot(fig)
        else:
            return py.plot(fig, include_plotlyjs=False, output_type='div')
    
    # recalculate the covariance matrix using top/significant eigenvalues and
    # their corresponding eigenvectors
    def _clean_sca(self, eig_vals, eig_vecs, eigval_rnd):
        thres = amax(eigval_rnd)
        n = len(extract(eig_vals > thres, eig_vals))
        
        # if the number of eigenvalues to use is not specified or greater than
        # the number of significant values, use significant ones
        if self.max_ev is None or self.max_ev > n:
            self.max_ev = n
        
        covariance_clean = zeros(shape = eig_vecs.shape)
        
        for i in range(self.max_ev):
            covariance_clean = covariance_clean + outer(
                dot(eig_vecs[:,i], eig_vals[i]), eig_vecs[:,i].T
                )
        
        return covariance_clean
    
    def significant_residues(self, plot=True):
        sig_sec = self._id_residues()
        self.sig_sec = sig_sec
        if plot:
            self.plot_sigsecs()
    
    # Identification of residues of interest
    def _id_residues(self, threshold=1.96):
        eig_vals, eig_vecs, loadings = self.eig
        eigval_rnd, eigvec_rnd, loadings_rnd = self.eig_rnd
        
        sig_sec = np.array([]).astype(int)
        
        for i in range(0, self.max_ev):
            # for the first principal component, fit eigenvectors of the
            # randomized alignments to normal distribution (t distribution)
            if i == 0: 
                mu, sigma = norm.fit(eigvec_rnd[:,:,i])
            # for subsequent components, fit eigenvectors of the actual
            # alignment to normal distribution (t distribution)
            else: 
                mu, sigma = norm.fit(eig_vecs[:,i])
               
            thres = (mu - threshold * sigma, mu + threshold * sigma)
            sig_sec = np.unique(
                np.concatenate((sig_sec, np.where(
                    (eig_vecs[:,i] < thres[0]) |
                    (eig_vecs[:,i] > thres[1]))[0]),0)
                )
            
        return sig_sec
    
    def plot_sigsecs(self, pynb=True):
        loadings = self.eig[-1]
        mask = np.full(loadings[:,0].shape, True, dtype=bool)
        mask[self.sig_sec] = False
        
        map_idx = np.array([str(r)+str(i) for i,r in self.msa.idx])
        
        trace1 = go.Scatter3d(
            x = loadings[mask, 0],
            y = loadings[mask, 1],
            z = loadings[mask, 2],
            mode = 'markers',
            text = map_idx[mask],
            hoverinfo = 'text',
            name = 'Nonsignificant',
            marker = dict(
                size = 9,
                color = 'rgb(55, 128, 191)',
                opacity = 0.8
            )
        )
        
        trace2 = go.Scatter3d(
            x = loadings[self.sig_sec, 0],
            y = loadings[self.sig_sec, 1],
            z = loadings[self.sig_sec, 2],
            mode = 'markers',
            text = map_idx[self.sig_sec],
            hoverinfo='text',
            name = 'Significant',
            marker = dict(
                size = 9,
                color = 'rgb(50, 160, 96)',
                opacity = 0.8
            )
        )
        
        layout = go.Layout(
            #title = '3D plot of significant residues',
            height=500,
            width=1000,
            margin = dict(
                t=0,
                l=0,
                r=0,
                b=0
            ),
            scene = go.Scene(
                xaxis = go.XAxis(title='PC1',
                                 showgrid=False, showline=False),
                yaxis = go.YAxis(title='PC2',
                                 showgrid=False, showline=False),
                zaxis = go.ZAxis(title='PC3',
                                 showgrid=False, showline=False)
            )
        )
        
        data = [trace1, trace2]
        fig = go.Figure(data=data, layout=layout)
        
        if pynb:
            py.iplot(fig)
        else:
            return py.plot(fig, include_plotlyjs=False, output_type='div')
    
    def _map_residues(self, sort):
        residues = []
        map_idx = np.array([str(r)+str(i) for i,r in self.msa.idx])
        
        for i in range(len(sort)):
            residues.append(map_idx[sort[i]])
            
        return residues
    
    # Clustering
    def cluster(self, dendrogram = True):
        if dendrogram:
            self.cluster_secs()
        n_secs, sectors = self._iter_clust()
        secs_sor, mag_sor, cluster = self._extract_secs(n_secs, sectors)
        
        self.sectors = self._map_sectors(secs_sor)
        self.magnitude = mag_sor
        self.covariance_cluster = cluster
        self.sorted_secs = secs_sor
    
    # hierarchical clustering of residues based on loading value
    def cluster_secs(self, pynb=True):
        component_range = np.array(range(self.max_ev))
        
        eig_vals, eig_vecs, loadings = self.eig
        
        data = loadings[self.sig_sec,:][:,component_range]
        
        figure = FF.create_dendrogram(
            data,
            orientation='right',
            labels = self.sig_sec,
            linkagefun = lambda x: linkage(data,'average',metric='cosine')
        )
        
        for i in range(len(figure['data'])):
            figure['data'][i]['xaxis'] = 'x2'
            
        sort = figure['layout']['yaxis']['ticktext']
        heat_data = loadings[sort,:][:,component_range]
        
        residues = self._map_residues(sort)
        
        heatmap = go.Data([go.Heatmap(
            z = heat_data,
            y = residues,
            colorscale = 'YlGnBu',
            colorbar = dict(
                x = 1.15
            )
        )])
        
        heatmap[0]['y'] = figure['layout']['yaxis']['tickvals']
        
        figure['data'].extend(go.Data(heatmap))
        figure['layout'].update(
            {#'title': 'Hierarchical clustering of residues',
             'width': 550,
             'height': 300 + 9 * len(self.sig_sec)})
        figure['layout']['xaxis'].update(
            {'domain':[.2, 1], 'mirror': False,
                'showgrid': False, 'showline': False,
                'zeroline': False,
                'showticklabels': False, 'ticks': ''})
        figure['layout'].update({'xaxis2':
            {'domain':[0, 0.19], 'mirror': False,
                'showgrid': False, 'showline': False,
                'zeroline': False,
                'showticklabels': False, 'ticks': ''}})
        figure['layout']['yaxis'].update(
            {'side':'right', 'mirror': False,
             'showgrid': False, 'showline': False,
             'zeroline': False,
             'ticktext': residues, 'ticks': ''})
        
        if pynb:
            py.iplot(figure)
        else:
            return py.plot(figure, include_plotlyjs=False, output_type='div')
    
    # iterative clustering, evaluated by (delta)Silhouette
    def _iter_clust(self):
        component_range = np.array(range(self.max_ev))
        eig_vals, eig_vecs, loadings = self.eig
        data = loadings[self.sig_sec,:][:,component_range]
        sca_dist = self.covariance_clean[self.sig_sec,:][:,self.sig_sec]
        sca_dist[sca_dist < 0] = 0
        
        T = fclusterdata(data, t=2, criterion='maxclust',
                         metric='cosine', method='average')
        s = silhouette_score(sca_dist, T, metric='precomputed')
        optimum = (2,0)
        p = s
        
        for k in range(3,11):
            T = fclusterdata(data, t=k, criterion='maxclust',
                             metric='cosine', method='average')
            s=silhouette_score(sca_dist, T, metric='precomputed')
            ds = -(s - p)
            p = s
            if ds > optimum[1]:
                optimum = (k, ds)
                
        S = fclusterdata(data, t=optimum[0], criterion='maxclust',
                         metric='cosine', method='average')
        n_secs = optimum[0]
        
        sectors = {}
        for i in range(1, n_secs + 1):
            sectors[i] = self.sig_sec[S==i]
            
        return (n_secs, sectors)
    
    def _extract_secs(self, n_secs, sectors):
        eig_vals, eig_vecs, loadings = self.eig
        component_range = np.array(range(self.max_ev))
        magnitude = np.sqrt(
            np.sum((loadings[:,component_range] ** 2), axis = 1)
            )
        mag_sor = {}
        
        for k in range(1, n_secs + 1):
            idx = np.argsort(magnitude[sectors[k]])[::-1]
            mag_sor['sector {}'.format(str(k))] = magnitude[sectors[k]][idx]
            
            # normalized to the greatest magnitude
            mag_sor['sector {}'.format(str(k))] = (
                mag_sor['sector {}'.format(str(k))]
                / mag_sor['sector {}'.format(str(k))][0]) 
            sectors[k] = sectors[k][idx]
            
        res = np.concatenate(list(sectors.values()))
        
        return (sectors, mag_sor, self.covariance_clean[res,:][:,res])
    
    def _map_sectors(self, sectors):
        mapped_sectors = {}
        
        for key, value in sectors.items():
            value_map = []
            for i in range(len(value)):
                value_map.append(self.msa.idx[value[i]])
            sector_name = 'sector {}'.format(str(key))
            mapped_sectors[sector_name] = value_map
            
        return mapped_sectors
    
    def plot_sectors(self, pynb=True):
        data = []
        eig_vals, eig_vecs, loadings = self.eig
        map_idx = np.array([str(r)+str(i) for i,r in self.msa.idx])
        colors = ['rgb(0, 51, 141)', 'rgb(27,94,32)', 'rgb(184, 7, 0)',
                  'rgb(230,81,0)', 'rgb(49, 27, 141)']
        
        for key, values in self.sorted_secs.items():
            trace = go.Scatter3d(
                x = loadings[values, 0],
                y = loadings[values, 1],
                z = loadings[values, 2],
                mode = 'markers',
                text = map_idx[values],
                hoverinfo = 'text',
                name = 'sector {}'.format(key),
                marker = dict(
                    color = colors[key-1],
                    size = 9,
                    opacity = 0.9
                )
            )
            data.append(trace)
            
        layout = go.Layout(
            #title = '3D plot of the SCA sectors',
            height=500,
            width=1000,
            margin = dict(
                t = 0,
                l = 0,
                r = 0,
                b = 0
            ),
            scene = go.Scene(
                xaxis = go.XAxis(title = 'PC1',
                                 showgrid = False, showline = False),
                yaxis = go.YAxis(title = 'PC2',
                                 showgrid = False, showline = False),
                zaxis = go.ZAxis(title = 'PC3',
                                 showgrid = False, showline = False)
            )
        )
        
        fig = go.Figure(data = data, layout = layout)
        
        if pynb:
            py.iplot(fig)
        else:
            return py.plot(fig, include_plotlyjs=False, output_type='div')
            
    def tertiary_plot(self):
        view = nv.show_structure_file('PDB/{}.pdb'.format(self.pdb_id))
        view.clear()
        view.add_representation('cartoon', color='burlywood')
        
        tones = {'Blues': np.array([0, 51, 141]),
                 'Greens': np.array([27,94,32]),
                 'Reds': np.array([184, 7, 0]), 
                 'Oranges': np.array([230,81,0]),
                 'Purples': np.array([49, 27, 141])}
        tone_list = list(tones.keys())

        for key, values in self.sectors.items():
            tone = tone_list[int(key[-1]) - 1]
            for i in range(len(values)):
                res = values[i]
                white = np.array([255,255,255])
                color = 'rgb' + str(tuple(
                    (tones[tone] * self.magnitude[key][i]
                     + white * (1 - self.magnitude[key][i])).astype(int)
                    ))
                
                sel = str(res[0]) + ':{}'.format(self.msa.chain)
                view.add_representation(
                    repr_type='surface', selection=sel, color=color
                )
                
        view.clear_representations(component=1)
        
        self.view = view
        return self.view
        
    def summary_report(self):
        html = '''
        <html>
        <head>
            <title>SCAnalysis Report</title>
            <style>body{ margin:50 100; background:white; }</style>
        </head>
        <body>
          <h1>SCAnalysis Report</h1>
        '''
        
        str_conservation = self.plot_conservation(pynb=False)
        html += '''
            <h2>Positional Conservation</h2>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            {}'''.format(str_conservation)
        
        str_covariance_raw = self.plot_covariance(m_type='raw', pynb=False)
        html += '''
            <h2>Covariance Matrix (raw)</h2>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            {}'''.format(str_covariance_raw)
        
        if self.covariance_clean is None:
            self.clean_spectrum(hist=False)
            
        str_hist = self.hist_eigval(pynb=False)
        html += '''
            <h2>Histogram of Eigenvalues</h2>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            {}'''.format(str_hist)
        
        str_covariance_clean = self.plot_covariance(m_type='clean', pynb=False)
        html += '''
            <h2>Covariance Matrix (clean)</h2>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            {}'''.format(str_covariance_clean)
        
        if self.sig_sec is None:
            self.significant_residues(plot=False)
            
        str_sigsecs = self.plot_sigsecs(pynb=False)
        html += '''
            <h2>Significant Sectors (loadings)</h2>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            {}'''.format(str_sigsecs)
        
        if self.covariance_cluster is None:
            self.cluster(dendrogram=False)
            
        str_dendro = self.cluster_secs(pynb=False)
        html += '''
            <h2>SCA Sectors (dendrogram)</h2>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            {}'''.format(str_dendro)
        
        str_covariance_cluster = self.plot_covariance(m_type='clustered',
                                                      pynb=False)
        html += '''
            <h2>Covariance Matrix (sorted by sectors)</h2>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            {}'''.format(str_covariance_cluster)
        
        str_sectors = self.plot_sectors(pynb=False)
        html += '''
            <h2>SCA Sectors (loadings)</h2>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            {}'''.format(str_sectors)
            
        if self.view is not None:
            view = self.view
            view._set_serialization()
            snippet = embed_snippet([view])
            html += '''
            <h2>SCA Sectors (Tertiary Structure)</h2>
            {snippet}
            </body>
            </html>'''.format(snippet=snippet)
            
        else:
            html += '''
            </body>
            </html>'''
        
        with open('{}_summary_report.html'.format(self.pdb_id),'w') as file:
            file.write(html)
    
    