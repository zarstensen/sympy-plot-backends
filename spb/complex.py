from sympy import Tuple, Expr
from spb.series import ComplexSeries, _set_discretization_points
from spb.vectors import _preprocess
from spb.utils import _plot_sympify
from spb.utils import _check_arguments
from spb.backends.base_backend import Plot
from spb.defaults import TWO_D_B, THREE_D_B

def _build_series(expr, ranges, label, kwargs):
    pass

def complex_plot(*args, show=True, **kwargs):
    """ Plot complex numbers or complex functions. By default, the aspect ratio 
    of the plot is set to ``aspect="equal"``.
    
    Depending on the provided expression, this function will produce different 
    types of plots:
    * list of complex numbers: creates a scatter plot.
    * complex function over a line range:
        1. line plot separating the real and imaginary parts.
        2. line plot of the modulus of the complex function colored by its
            argument.
    * complex function over a complex range: domain coloring plot.

    Arguments
    =========
        expr : Expr
            Represent the complex number or complex function to be plotted.
        
        range : 3-element tuple
            Denotes the range of the variables. For example:
            * (z, -5, 5): plot a line from complex point (-5 + 0*I) to (5 + 0*I)
            * (z, -5 + 2*I, 5 + 2*I): plot a line from complex point (-5 + 2*I)
                to (5 + 2 * I). Note the same imaginary part for the start/end
                point.
            * (z, -5 - 3*I, 5 + 3*I): domain coloring plot of the complex
                function over the specified domain.

        label : str
            The name of the complex function to be eventually shown on the
            legend. If none is provided, the string representation of the 
            function will be used.
        
        To specify multiple complex functions, wrap them into a tuple.
        Refer to the examples to learn more.

    Keyword Arguments
    =================

        absarg : boolean
            If True, plot the modulus of the complex function colored by its
            argument. If False, separately plot the real and imaginary parts.
            Default to False. 
        
        n1, n2 : int
            Number of discretization points in the real/imaginary-directions,
            respectively. Default to 300.
        
        n : int
            Set the same number of discretization points in all directions.
            Default to 300.

        nc : int
            Number of discretization points for the scalar contour plot.
            Default to 100.
        
        show : boolean
            Default to True, in which case the plot will be shown on the screen.
        
        use_cm : boolean
            If `absarg=True` and `use_cm=True` then plot the modulus of the 
            complex function colored by its argument. If `use_cm=False`, plot 
            the modulus of the complex function with a solid color.
            Default to True.

    Domain Coloring Arguments
    =========================

        alpha : float
            Default to 1. Can be `0 <= alpha <= 1`. It adjust the use of colors.
            A value less than 1 adds more color which can help isolating the
            roots and poles (which are still black and white, respectively).
            alpha=0 ignores the magnitude of f(z) completely.
        
        colorspace : str
            Default to `"cam16"`. Other options are `"cielab", "oklab", "hsl"`.
            It can be set to `"hsl"` to get the common fully saturated, vibrant
            colors. This is usually a bad idea since it creates artifacts which
            are not related with the underlying data.

    Examples
    ========

    Plot individual complex points:

    .. code-block:: python
        complex_plot(3 + 2 * I, 4 * I, 2, aspect="equal", legend=True)

    Plot two lists of complex points:

    .. code-block:: python
        z = symbols("z")
        expr1 = z * exp(2 * pi * I * z)
        expr2 = 2 * expr1
        l1 = [expr1.subs(z, t / 20) for t in range(20)]
        l2 = [expr2.subs(z, t / 20) for t in range(20)]
        complex_plot((l1, "f1"), (l2, "f2"), aspect="equal", legend=True)

    Plot the real and imaginary part of a function:

    .. code-block:: python
        z = symbols("z")
        complex_plot(sqrt(z), (z, -3, 3), legend=True)
    
    .. code-block:: python
        z = symbols("z")
        complex_plot((cos(z) + sin(I * z), "f"), (z, -2, 2), legend=True)

    Plot the modulus of a complex function colored by its magnitude:

    .. code-block:: python
        z = symbols("z")
        complex_plot((cos(z) + sin(I * z), "f"), (z, -2, 2), legend=True,
            absarg=True)
    
    Domain coloring plot. Note that it might be necessary to increase the number
    of discretization points in order to get a smoother plot:

    .. code-block:: python
        z = symbols("z")
        complex_plot(gamma(z), (z, -3 - 3*I, 3 + 3*I), colorspace="hsl", n=500)
    


    TODO: problems...
        p = complex_plot(exp(2 * pi * I * z), (z, 0, 0.1), 
             legend=True, backend=BB, absarg=True)
    """
    args = _plot_sympify(args)
    kwargs = _set_discretization_points(kwargs, ComplexSeries)
    if not "aspect" in kwargs.keys():
        kwargs["aspect"] = "equal"
    series = []
    
    if all([a.is_complex for a in args]):
        # args is a list of complex numbers
        for a in args:
            series.append(ComplexSeries([a], None, str(a), **kwargs))
    elif ((len(args) > 0) and 
            all([isinstance(a, (list, tuple, Tuple)) for a in args]) and
            all([len(a) > 0 for a in args]) and
            all([isinstance(a[0], (list, tuple, Tuple)) for a in args])):
        # args is a list of tuples of the form (list, label) where list 
        # contains complex points
        for a in args:
            series.append(ComplexSeries(a[0], None, a[-1], **kwargs))
    else:
        args = _check_arguments(args, 1, 1)
        
        for a in args:
            expr, ranges, label = a[0], a[1:-1], a[-1]

            # ranges need to contain complex numbers
            ranges = list(ranges)
            for i, r in enumerate(ranges):
                ranges[i] = (r[0], complex(r[1]), complex(r[2]))

            if expr.is_complex:
                # complex number
                series.append(ComplexSeries([expr], None, label, **kwargs))
            else:
                if ((ranges[0][1].imag == ranges[0][2].imag) and
                        not kwargs.get('absarg', False)):
                    # complex expression evaluated over a line: need to add two
                    # series, one for the real and imaginary part, respectively

                    # NOTE: as a design choice, a complex function plotted over 
                    # a line will create two data series, one for the real part,
                    # the other for the imaginary part. This is undoubtely
                    # inefficient as we must evaluate the same expression two
                    # times. On the other hand, it allows to maintain a 
                    # one-to-one correspondance between Plot.series and 
                    # backend.data, which doesn't require a redesign of the
                    # backend in order to work with iplot
                    # (backend._update_interactive).

                    kw1, kw2 = kwargs.copy(), kwargs.copy()
                    kw1["real"], kw1["imag"] = True, False
                    kw2["real"], kw2["imag"] = False, True
                    series.append(ComplexSeries(expr, *ranges, label, **kw1))
                    series.append(ComplexSeries(expr, *ranges, label, **kw2))
                else:
                    series.append(ComplexSeries(expr, *ranges, label, **kwargs))
    
    if not "backend" in kwargs:
        kwargs["backend"] = TWO_D_B
        
    p = Plot(*series, **kwargs)
    if show:
        p.show()
    return p
