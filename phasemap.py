# This file is part of pyEMAPS.
# Copyright (C) 2021-2026 EMLab Solutions, Inc.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Additional permission under GPLv3 Section 7:
# See license-exception.txt for the exception permitting
# combination with the separately licensed backend, emaps.

'''
Phase maps of 4D-STEM scans: which of several crystal phases each pattern belongs to, made by
:py:meth:`StackImage.mapPhases <pyemaps.stackimg.StackImage.mapPhases>`. Phase mapping is
experimental, as orientation mapping is.
'''

import numpy as np

from .orientmap import OrientationMap, _FIELDS

#: The phase of a pattern no phase could be scored for (no peaks).
PM_NONE = -1

# a colour per phase, then grey for ambiguous patterns and black for none
_PHASE_COLOURS = np.array([[0.12, 0.47, 0.71], [1.0, 0.5, 0.05], [0.17, 0.63, 0.17],
                           [0.84, 0.15, 0.16], [0.58, 0.4, 0.74], [0.55, 0.34, 0.29],
                           [0.89, 0.47, 0.76], [0.74, 0.74, 0.13], [0.09, 0.75, 0.81],
                           [0.5, 0.5, 0.0]])
_AMBIGUOUS_COLOUR = np.array([0.6, 0.6, 0.6])

_SCORES = ('spacing', 'explained', 'predicted')


class PhaseMap:
    '''
    The crystal phase at each pattern of a 4D-STEM scan, from
    :py:meth:`StackImage.mapPhases <pyemaps.stackimg.StackImage.mapPhases>`, with each phase's
    orientation map. Arrays have the scan's shape, ``(rows, columns)``; the scores have one more
    axis, for the phase. Phase mapping is experimental; see *mapPhases*.

    Each pattern is indexed against every phase's database, and emaps scores each phase from
    0 to 1:

    - ``spacing``: how well the distances of the pattern's peaks from its centre match the
      phase's reflection spacings, with the camera constant. It needs no orientation, and it
      tells apart phases that differ only in their lattice constants.
    - ``explained``: the share of the peaks the indexing matched to the phase's database.
    - ``predicted``: the share of the matched database pattern's predicted intensity that has a
      peak where it's predicted.

    The phase is the one with the best score: the spacing, plus, with a nonzero
    *orientation_weight*, the harmonic mean of explained and predicted where that phase's
    indexing is reliable. ``confidence`` is how far it leads the second best; patterns below the
    threshold are ``ambiguous``.

    :ivar names: the phases' names, in order; ``phase`` indexes them.
    :ivar phase: the phase of each pattern, or :py:data:`PM_NONE`.
    :ivar ambiguous: True where the best phase doesn't lead clearly.
    :ivar confidence: the best phase's lead over the second.
    :ivar maps: each phase's :py:class:`~pyemaps.orientmap.OrientationMap`.
    '''

    def __init__(self, names, maps, phase, ambiguous, confidence, best, spacing, explained,
                 predicted, params=None):
        self.names = tuple(str(n) for n in names)
        self.maps = list(maps)
        self.scan_shape = self.maps[0].scan_shape
        shape = self.scan_shape
        n = len(self.names)
        self.phase = np.asarray(phase, dtype=np.int8).reshape(shape)
        self.ambiguous = np.asarray(ambiguous, dtype=bool).reshape(shape)
        self.confidence = np.asarray(confidence, dtype=np.float32).reshape(shape)
        self.best = np.asarray(best, dtype=np.float32).reshape(shape)
        self.spacing = np.asarray(spacing, dtype=np.float32).reshape(shape + (n,))
        self.explained = np.asarray(explained, dtype=np.float32).reshape(shape + (n,))
        self.predicted = np.asarray(predicted, dtype=np.float32).reshape(shape + (n,))
        self.params = dict(params or {})

    def __repr__(self):
        f = self.fractions()
        parts = ', '.join(f'{k} {100 * v:.0f}%' for k, v in f.items())
        return (f'PhaseMap({self.scan_shape[0]} x {self.scan_shape[1]} patterns: {parts}; '
                f'{np.count_nonzero(self.ambiguous)} ambiguous)')

    def decided(self):
        '''True where the pattern has a phase that leads clearly.'''
        return (self.phase >= 0) & ~self.ambiguous

    def fractions(self, include_ambiguous=False):
        '''
        Each phase's share of the decided patterns (or, with *include_ambiguous*, of all the
        patterns with a phase), as ``{name: fraction}``.
        '''
        mask = (self.phase >= 0) if include_ambiguous else self.decided()
        total = max(int(np.count_nonzero(mask)), 1)
        return {name: np.count_nonzero(mask & (self.phase == p)) / total
                for p, name in enumerate(self.names)}

    def orientation(self):
        '''
        Each pattern's orientation from its phase's orientation map, shape
        ``(rows, columns, 3, 3)``; NaN where the pattern has no phase or that phase's indexing
        failed.
        '''
        out = np.full(self.scan_shape + (3, 3), np.nan)
        for p, m in enumerate(self.maps):
            sel = self.phase == p
            out[sel] = m.orientation[sel]
        return out

    def ipf_colors(self, min_rindex=5.0, background=(0.0, 0.0, 0.0)):
        '''
        Inverse pole figure colours of each pattern's orientation, from its phase's orientation
        map (see :py:meth:`OrientationMap.ipf_colors
        <pyemaps.orientmap.OrientationMap.ipf_colors>`), shape ``(rows, columns, 3)``.
        Ambiguous patterns, and those without a reliable orientation, get *background*.
        '''
        rgb = np.empty(self.scan_shape + (3,))
        rgb[:] = background
        for p, m in enumerate(self.maps):
            sel = self.decided() & (self.phase == p)
            rgb[sel] = m.ipf_colors(min_rindex, background)[sel]
        return rgb

    def phase_colors(self):
        '''A colour per phase at each pattern, shape ``(rows, columns, 3)``: grey where
        ambiguous, black where no phase.'''
        rgb = np.zeros(self.scan_shape + (3,))
        for p in range(len(self.names)):
            rgb[self.phase == p] = _PHASE_COLOURS[p % len(_PHASE_COLOURS)]
        rgb[(self.phase >= 0) & self.ambiguous] = _AMBIGUOUS_COLOUR
        return rgb

    def show(self, kind='phase', min_rindex=5.0, title=None, show=True):
        '''
        Plot the map.

        :param kind: ``'phase'`` for the phases, with a legend; ``'confidence'``; ``'ipf'`` for
            each pattern's orientation colours from its phase; or ``'spacing'``,
            ``'explained'`` or ``'predicted'`` for that score of each phase.
        :param min_rindex: for ``'ipf'``, the reliability index below which a pattern is
            black.
        :param title: the figure title.
        :param show: call ``matplotlib.pyplot.show``; with False, the figure is returned.
        :return: the matplotlib figure.
        '''
        import matplotlib.pyplot as plt
        from matplotlib.patches import Patch

        if kind in _SCORES:
            values = getattr(self, kind)
            n = len(self.names)
            fig, axes = plt.subplots(1, n, figsize=(4.5 * n, 4.2), squeeze=False)
            for p, ax in enumerate(axes[0]):
                im = ax.imshow(values[..., p], interpolation='nearest', cmap='viridis',
                               vmin=0, vmax=1)
                ax.set_title(f'{kind}: {self.names[p]}')
                ax.set_xlabel('scan column')
                ax.set_ylabel('scan row')
            fig.colorbar(im, ax=axes[0].tolist())
            if title:
                fig.suptitle(title)
        else:
            fig, ax = plt.subplots(figsize=(6.5, 5))
            if kind == 'phase':
                ax.imshow(self.phase_colors(), interpolation='nearest')
                f = self.fractions()
                handles = [Patch(color=_PHASE_COLOURS[p % len(_PHASE_COLOURS)],
                                 label=f'{name} ({100 * f[name]:.0f}%)')
                           for p, name in enumerate(self.names)]
                handles.append(Patch(color=_AMBIGUOUS_COLOUR, label='ambiguous'))
                ax.legend(handles=handles, loc='upper left', bbox_to_anchor=(1.02, 1.0),
                          fontsize=9)
                ax.set_title(title or 'Phase map')
            elif kind == 'confidence':
                im = ax.imshow(self.confidence, interpolation='nearest', cmap='viridis')
                fig.colorbar(im, ax=ax)
                ax.set_title(title or 'Phase confidence')
            elif kind == 'ipf':
                ax.imshow(self.ipf_colors(min_rindex), interpolation='nearest')
                ax.set_title(title or 'Orientation map, each phase its own colour key')
            else:
                raise ValueError("kind must be 'phase', 'confidence', 'ipf', 'spacing', "
                                 f"'explained' or 'predicted', not {kind!r}")
            ax.set_xlabel('scan column')
            ax.set_ylabel('scan row')
            fig.tight_layout()
        if show:
            plt.show()
        return fig

    def save(self, path):
        '''Save the map, with each phase's orientation map, to a NumPy ``.npz`` file, to load
        with :py:meth:`load`.'''
        data = {'names': np.array(self.names), 'phase': self.phase,
                'ambiguous': self.ambiguous, 'confidence': self.confidence, 'best': self.best,
                'spacing': self.spacing, 'explained': self.explained,
                'predicted': self.predicted, 'params': np.array(repr(self.params))}
        for p, m in enumerate(self.maps):
            data[f'map{p}_scan_shape'] = np.array(m.scan_shape)
            data[f'map{p}_basis'] = m.basis
            data[f'map{p}_corners'] = m.corners
            data[f'map{p}_database'] = np.array(m.database)
            data[f'map{p}_params'] = np.array(repr(m.params))
            for f in _FIELDS:
                data[f'map{p}_{f}'] = getattr(m, f)
        np.savez_compressed(path, **data)

    @classmethod
    def load(cls, path):
        '''Load a map saved by :py:meth:`save`.'''
        import ast
        with np.load(path, allow_pickle=False) as z:
            names = [str(n) for n in z['names']]
            maps = []
            for p in range(len(names)):
                kw = {f: z[f'map{p}_{f}'] for f in _FIELDS}
                maps.append(OrientationMap(
                    tuple(z[f'map{p}_scan_shape']), basis=z[f'map{p}_basis'],
                    corners=z[f'map{p}_corners'], database=str(z[f'map{p}_database']),
                    params=ast.literal_eval(str(z[f'map{p}_params'])), **kw))
            return cls(names, maps, z['phase'], z['ambiguous'], z['confidence'], z['best'],
                       z['spacing'], z['explained'], z['predicted'],
                       params=ast.literal_eval(str(z['params'])))
