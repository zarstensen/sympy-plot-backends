from spb.backends.base_backend import Plot
from spb.backends.matplotlib import MB
import matplotlib.pyplot as plt
import numpy as np
import panel as pn
from matplotlib.gridspec import GridSpec

plt.ioff()


def _nrows_ncols(nr, nc, nplots):
    """Define the correct number of rows and/or columns based on the number
    of plots to be shown.
    """
    if (nc <= 0) and (nr <= 0):
        nc = 1
        nr = nplots
    elif nr <= 0:
        nr = int(np.ceil(nplots / nc))
    elif nc <= 0:
        nc = int(np.ceil(nplots / nr))
    elif nr * nc < nplots:
        nr += 1
        return _nrows_ncols(nr, nc, nplots)
    return nr, nc

def _create_mpl_figure(mapping):
    fig = plt.figure()
    for spec, p in mapping.items():
        kw = {"projection": "3d"} if (len(p.series) > 0 and
            p.series[0].is_3D) else {}
        cur_ax = fig.add_subplot(spec, **kw)
        # cpa: current plot attributes
        cpa = p._copy_kwargs()
        cpa["backend"] = MB
        cpa["fig"] = fig
        cpa["ax"] = cur_ax
        p = Plot(*p.series, **cpa)
    return fig

def _create_panel_figure(mapping):
    fig = pn.GridSpec(sizing_mode="stretch_width")
    for spec, p in mapping.items():
        rs = spec.rowspan
        cs = spec.colspan
        fig[slice(rs.start, rs.stop), slice(cs.start, cs.stop)] = p.fig
    return fig

def plotgrid(*args, **kwargs):
    """Combine multiple plots into a grid-like layout.
    This function has two modes of operation, depending on the input arguments.
    Make sure to read the examples to fully understand them.

    Parameters
    ==========

    args : sequence (optional)
        A sequence of aldready created plots. This, in combination with
        `nr` and `nc` represents the first mode of operation, where a basic
        grid with (nc * nr) subplots will be created.

    nr, nc : int (optional)
        Number of rows and columns.
        By default, `nc = 1` and `nr = -1`: this will create as many rows
        as necessary, and a single column.
        By setting `nc = 1` and `nc = -1`, it will create a single row and
        as many columns as necessary.

    gs : dict (optional)
        A dictionary mapping Matplotlib's ``GridSpec`` objects to the plots.
        The keys represent the cells of the layout. Each cell will host the
        associated plot.
        This represents the second mode of operation, as it allows to create
        more complicated layouts.
    
    show : boolean (optional)
        It applies only to Matplotlib figures. Default to True.

    Returns
    =======

    fig : ``plt.Figure`` or ``pn.GridSpec``
        If all input plots are instances of ``MatplotlibBackend``, than a
        Matplotlib ``Figure`` will be returned. Otherwise an instance of
        Holoviz Panel's ``GridSpec`` will be returned.


    Examples
    ========

    First mode of operation with instances of MatplotlibBackend:

    .. code-block:: python
        from sympy import *
        from spb.backends.matplotlib import MB
        from spb import *

        x, y, z = symbols("x, y, z")
        p1 = plot(sin(x), backend=MB, show=False)
        p2 = plot(tan(x), backend=MB, detect_poles=True, show=False)
        p3 = plot(exp(-x), backend=MB, show=False)
        plotgrid(p1, p2, p3)

    First mode of operation with different backends. Try this on a Jupyter
    Notebook. Note that Matplotlib has been integrated as a picture, thus it
    loses its interactivity.

    .. code-block:: python
        p1 = plot(sin(x), backend=MB, show=False)
        p2 = plot(tan(x), backend=MB, detect_poles=True, show=False)
        p3 = plot(exp(-x), backend=MB, show=False)
        plotgrid(p1, p2, p3, nr=1, nc=3)

    Second mode of operation: using Matplotlib GridSpec with all plots being
    instances of MatplotlibBackend:

    .. code-block:: python
        from matplotlib.gridspec import GridSpec

        p1 = plot(sin(x), cos(x), show=False, backend=MB)
        p2 = plot_contour(cos(x**2 + y**2), (x, -3, 3), (y, -3, 3), show=False, backend=BB)
        p3 = complex_plot(sqrt(x), show=False, backend=PB)
        p4 = plot_vector(Matrix([-y, x]), (x, -5, 5), (y, -5, 5), show=False, backend=MB)
        p5 = complex_plot(gamma(z), (z, -3-3*I, 3+3*I), show=False, backend=MB)

        gs = GridSpec(3, 3)
        mapping = {
            gs[0, :1]: p1,
            gs[1, :1]: p2,
            gs[2:, :1]: p3,
            gs[2:, 1:]: p4,
            gs[0:2, 1:]: p5,
        }
        plotgrid(gs=mapping)

    """
    show = kwargs.get("show", True)
    gs = kwargs.get("gs", None)

    if (gs is None) and (len(args) == 0):
        fig = plt.figure()

    elif (gs is None):
        ### First mode of operation
        # default layout: 1 columns, as many rows as needed
        nr = kwargs.get("nr", -1)
        nc = kwargs.get("nc", 1)
        nr, nc = _nrows_ncols(nr, nc, len(args))

        gs = GridSpec(nr, nc)
        mapping = {}
        c = 0
        for i in range(nr):
            for j in range(nc):
                mapping[gs[i, j]] = args[c]
                c += 1

        if all(isinstance(a, MB) for a in args):
            fig = _create_mpl_figure(mapping)
        else:
            fig = _create_panel_figure(mapping)

    else:
        ### Second mode of operation
        if not isinstance(gs, dict):
            raise TypeError("``gs`` must be a dictionary.")
        
        from matplotlib.gridspec import SubplotSpec
        if not isinstance(list(gs.keys())[0], SubplotSpec):
            raise ValueError(
                "Keys of ``gs`` must be of elements of type "
                "matplotlib.gridspec.SubplotSpec. Use "
                "matplotlib.gridspec.GridSpec to create them.")

        if all(isinstance(a, MB) for a in gs.values()):
            fig = _create_mpl_figure(gs)
        else:
            fig = _create_panel_figure(gs)

    if isinstance(fig, plt.Figure):
        fig.tight_layout()
        if show:
            fig.show()
    return fig
