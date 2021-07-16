from sympy import lambdify, Tuple, sympify, Expr, S, Symbol, Dummy
from sympy.matrices.dense import DenseMatrix
from sympy.vector import Vector, BaseScalar
from sympy.vector.operators import _get_coord_systems
from sympy.utilities.iterables import ordered
from sympy.core.relational import Relational
from sympy.logic.boolalg import BooleanFunction
import numpy as np


def get_lambda(expr, **kwargs):
    """Create a lambda function to numerically evaluate expr by sorting
    alphabetically the function arguments.
    Parameters
    ----------
        expr : Expr
            The Sympy expression to convert.
        **kwargs
            Other keyword arguments to the function lambdify.
    Returns
    -------
        s : list
            The function signature: a list of the ordered function arguments.
        f : lambda
            The generated lambda function.ò
    """
    signature = list(ordered(expr.free_symbols))
    return signature, lambdify(signature, expr, **kwargs)


def _create_ranges(free_symbols, ranges, npar):
    """This function does two things:
    1. Check if the number of free symbols is in agreement with the type of plot
        chosen. For example, plot() requires 1 free symbol; plot3d() requires 2
        free symbols.
    2. Sometime users create plots without providing ranges for the variables.
        Here we create the necessary ranges.

    free_symbols
        The free symbols contained in the expressions to be plotted

    ranges
        The limiting ranges provided by the user

    npar
        The number of free symbols required by the plot functions. For example,
        npar=1 for plot, npar=2 for plot3d, ...

    """

    get_default_range = lambda symbol: Tuple(symbol, -10, 10)

    if len(free_symbols) > npar:
        raise ValueError(
            "Too many free symbols.\n"
            + "Expected {} free symbols.\n".format(npar)
            + "Received {}: {}".format(len(free_symbols), free_symbols)
        )

    # TODO: should I keep it?
    if len(ranges) > npar:
        raise ValueError(
            "Too many ranges. Received %s, expected %s" % (len(ranges), npar)
        )

    # free symbols in the ranges provided by the user
    rfs = set().union([r[0] for r in ranges])
    if len(rfs) != len(ranges):
        raise ValueError("Multiple ranges with the same symbol")

    if len(ranges) < npar:
        symbols = free_symbols.difference(rfs)
        if symbols != set():
            # add a range for each missing free symbols
            for s in symbols:
                ranges.append(get_default_range(s))
        # if there is still room, fill them with dummys
        for i in range(npar - len(ranges)):
            ranges.append(get_default_range(Dummy()))

    if len(free_symbols) == npar:
        # there could be times when this condition is not met, for example
        # plotting the function f(x, y) = x (which is a plane); in this case,
        # free_symbols = {x} whereas rfs = {x, y} (or x and Dummy)
        rfs = set().union([r[0] for r in ranges])
        if free_symbols.difference(rfs) != set():
            raise ValueError(
                "Incompatible free symbols of the expressions with the ranges.\n"
                + "Free symbols in the expressions: {}\n".format(free_symbols)
                + "Free symbols in the ranges: {}".format(rfs)
            )
    return ranges


def _check_arguments(args, nexpr, npar):
    """Checks the arguments and converts into tuples of the
    form (exprs, ranges, name_expr).

    Parameters
    ==========

    args
        The arguments provided to the plot functions

    nexpr
        The number of sub-expression forming an expression to be plotted. For
        example:
        nexpr=1 for plot.
        nexpr=2 for plot_parametric: a curve is represented by a tuple of two
            elements.
        nexpr=1 for plot3d.
        nexpr=3 for plot3d_parametric_line: a curve is represented by a tuple
            of three elements.

    npar
        The number of free symbols required by the plot functions. For example,
        npar=1 for plot, npar=2 for plot3d, ...

    Examples
    ========

    .. plot::
       :context: reset
       :format: doctest
       :include-source: True

       >>> from sympy import cos, sin, symbols
       >>> from sympy.plotting.plot import _check_arguments
       >>> x = symbols('x')
       >>> _check_arguments([cos(x), sin(x)], 2, 1)
           [(cos(x), sin(x), (x, -10, 10), '(cos(x), sin(x))')]

       >>> _check_arguments([x, x**2], 1, 1)
           [(x, (x, -10, 10), 'x'), (x**2, (x, -10, 10), 'x**2')]
    """
    if not args:
        return []
    output = []

    if all([isinstance(a, (Expr, Relational, BooleanFunction)) for a in args[:nexpr]]):
        # In this case, with a single plot command, we are plotting either:
        #   1. one expression
        #   2. multiple expressions over the same range

        res = [not (_is_range(a) or isinstance(a, str)) for a in args]
        exprs = [a for a, b in zip(args, res) if b]
        ranges = [r for r in args[nexpr:] if _is_range(r)]
        label = args[-1] if isinstance(args[-1], str) else ""

        if not all([_is_range(r) for r in ranges]):
            raise ValueError(
                "Expressions must be followed by ranges. Received:\n"
                "Expressions: %s\n"
                "Others: %s" % (exprs, ranges)
            )
        free_symbols = set().union(*[e.free_symbols for e in exprs])
        ranges = _create_ranges(free_symbols, ranges, npar)

        if nexpr > 1:
            # in case of plot_parametric or plot3d_parametric_line, there will
            # be 2 or 3 expressions defining a curve. Group them together.
            if len(exprs) == nexpr:
                exprs = (tuple(exprs),)
        for expr in exprs:
            # need this if-else to deal with both plot/plot3d and
            # plot_parametric/plot3d_parametric_line
            e = (
                (expr,)
                if isinstance(expr, (Expr, Relational, BooleanFunction))
                else expr
            )
            current_label = (
                label
                if label
                else (
                    str(expr)
                    if isinstance(expr, (Expr, Relational, BooleanFunction))
                    else str(e)
                )
            )
            output.append((*e, *ranges, current_label))

    else:
        # In this case, we are plotting multiple expressions, each one with its
        # range. Each "expression" to be plotted has the following form:
        # (expr, range, label) where label is optional

        # look for "global" range and label
        labels = [a for a in args if isinstance(a, str)]
        ranges = [a for a in args if _is_range(a)]
        n = len(ranges) + len(labels)
        new_args = args[:-n] if n > 0 else args
        # at this point, new_args might just be [expr]. But I need it to be
        # [[expr]] in order to be able to loop over [expr, range [opt], label [opt]]
        if not isinstance(new_args[0], (list, tuple, Tuple)):
            new_args = [new_args]

        # Each arg has the form (expr1, expr2, ..., range1 [optional], ...,
        #   label [optional])
        for arg in new_args:
            # look for "local" range and label. If there is not, use "global".
            l = [a for a in arg if isinstance(a, str)]
            if not l:
                l = labels
            r = [a for a in arg if _is_range(a)]
            if not r:
                r = ranges.copy()

            arg = arg[:nexpr]
            free_symbols = set().union(*[a.free_symbols for a in arg])
            if len(r) != npar:
                r = _create_ranges(free_symbols, r, npar)
            label = (str(arg[0]) if nexpr == 1 else str(arg)) if not l else l[0]
            output.append((*arg, *r, label))
    return output


def _plot_sympify(args):
    """By allowing the users to set custom labels to the expressions being
    plotted, a critical issue is raised: whenever a special character like $,
    {, }, ... is used in the label (type string), sympify will raise an error.
    This function recursively loop over the arguments passed to the plot
    functions: the sympify function will be applied to all arguments except
    those of type string.
    """
    if isinstance(args, Expr):
        return args

    args = list(args)
    for i, a in enumerate(args):
        if isinstance(a, (list, tuple)):
            args[i] = Tuple(*_plot_sympify(a), sympify=False)
        elif not isinstance(a, str):
            args[i] = sympify(a)
    if isinstance(args, tuple):
        return Tuple(*args, sympify=False)
    return args


def _is_range(r):
    """A range is defined as (symbol, start, end). start and end should
    be numbers.
    """
    return (
        isinstance(r, Tuple)
        and (len(r) == 3)
        and r.args[1].is_number
        and r.args[2].is_number
    )


def _unpack_args(*args, matrices=False, fill_ranges=True):
    """Given a list/tuple of arguments previously processed by _plot_sympify(),
    separates and returns its components: expressions, ranges, label.

    Parameters
    ==========
        matrices : boolean
            Default to False. If True, when a single DenseMatrix is given as
            the expression, it will be converted to a list. This is useful in
            order to deal with vectors (written in form of matrices) for
            iplot.

        fill_ranges : boolean
            Default to True. If not enough ranges are provided, the algorithm
            will try to create the missing ones.

    Examples
    ========

    >>> from sympy import cos, sin, symbols
    >>> x, y = symbols('x, y')
    >>> args = (sin(x), (x, -10, 10), "f1")
    >>> args = _plot_sympify(args)
    >>> _unpack_args(*args)
        ([sin(x)], [(x, -2, 2)], 'f1')

    >>> args = (sin(x**2 + y**2), (x, -2, 2), (y, -3, 3), "f2")
    >>> args = _plot_sympify(args)
    >>> _unpack_args(*args)
        ([sin(x**2 + y**2)], [(x, -2, 2), (y, -3, 3)], 'f2')

    >>> args = (sin(x + y), cos(x - y), x + y, (x, -2, 2), (y, -3, 3), "f3")
    >>> args = _plot_sympify(args)
    >>> _unpack_args(*args)
        ([sin(x + y), cos(x - y), x + y], [(x, -2, 2), (y, -3, 3)], 'f3')
    """
    ranges = [t for t in args if _is_range(t)]
    labels = [t for t in args if isinstance(t, str)]
    label = "" if not labels else labels[0]
    results = [not (_is_range(a) or isinstance(a, str)) for a in args]
    exprs = [a for a, b in zip(args, results) if b]

    if label == "":
        if len(exprs) == 1:
            label = str(exprs[0])
        else:
            label = str(tuple(exprs))

    if matrices and (len(exprs) == 1):
        if isinstance(exprs[0], (list, tuple, Tuple, DenseMatrix)):
            exprs = list(exprs[0])
        elif isinstance(exprs[0], Vector):
            exprs, ranges = _split_vector(exprs[0], ranges, fill_ranges)
            if exprs[-1] is S.Zero:
                exprs = exprs[:-1]
    return exprs, ranges, label


def ij2k(cols, i, j):
    """Create the connectivity for the mesh.
    https://github.com/K3D-tools/K3D-jupyter/issues/273
    """
    return cols * i + j


def get_vertices_indices(x, y, z):
    """Compute the vertices matrix (Nx3) and the connectivity list for
    triangular faces.

    Parameters
    ==========
        x, y, z : np.array
            2D arrays
    """
    rows, cols = x.shape
    x = x.flatten()
    y = y.flatten()
    z = z.flatten()
    vertices = np.vstack([x, y, z]).T
    indices = []
    for i in range(1, rows):
        for j in range(1, cols):
            indices.append(
                [ij2k(cols, i, j), ij2k(cols, i - 1, j), ij2k(cols, i, j - 1)]
            )
            indices.append(
                [ij2k(cols, i - 1, j - 1), ij2k(cols, i, j - 1), ij2k(cols, i - 1, j)]
            )
    return vertices, indices


def _split_vector(expr, ranges, fill_ranges=True):
    """Extract the components of the given vector or matrix.

    Parameters
    ==========
        expr : Vector, DenseMatrix or list/tuple
        ranges : list/tuple

    Returns
    =======
        split_expr : tuple
            Tuple of the form (x_expr, y_expr, z_expr). If a 2D vector is
            provided, z_expr = S.Zero.
        ranges : list/tuple

    NOTE: this function is located in utils.py module (and not in vectors.py)
    in order to avoid circular import.
    """
    if isinstance(expr, Vector):
        N = list(_get_coord_systems(expr))[0]
        expr = expr.to_matrix(N)
        # TODO: experimental_lambdify is not able to deal with base scalars.
        # Need to replace them both in the vector as well in the ranges.
        # Sympy's lambdify is able to deal with them. Once experimental_lambdify
        # is removed, the following code shouldn't be necessary anymore.
        bs = list(expr.atoms(BaseScalar))
        bs = sorted(bs, key=str)
        bs_dict = {b: Symbol(t) for b, t in zip(bs, ["x", "y", "z"])}
        expr = expr.subs(bs_dict)
        ranges = [r.subs(bs_dict) for r in ranges]
    elif not isinstance(expr, (DenseMatrix, list, tuple, Tuple)):
        raise TypeError(
            "The provided expression must be a symbolic vector, or a "
            "symbolic matrix, or a tuple/list with 2 or 3 symbolic "
            + "elements.\nReceived type = {}".format(type(expr))
        )
    elif (len(expr) < 2) or (len(expr) > 3):
        raise ValueError(
            "This function only plots 2D or 3D vectors.\n"
            + "Received: {}. Number of elements: {}".format(expr, len(expr))
        )

    if fill_ranges:
        ranges = list(ranges)
        fs = set().union(*[e.free_symbols for e in expr])
        if len(ranges) < len(fs):
            fs_ranges = set().union([r[0] for r in ranges])
            for s in fs:
                if s not in fs_ranges:
                    ranges.append(Tuple(s, -10, 10))

    if len(expr) == 2:
        xexpr, yexpr = expr
        zexpr = S.Zero
    else:
        xexpr, yexpr, zexpr = expr
    split_expr = xexpr, yexpr, zexpr
    return split_expr, ranges


def get_seeds_points(xx, yy, zz, uu, vv, ww):
    """Returns an optimal list of seeds points to be used to generate 3D
    streamlines.

    Parameters
    ==========
        xx, yy, zz: np.ndarray
            3D discretization of the space from meshgrid.

        uu, vv, ww: np.ndarray
            Vector components calculated at the discretized points in space.

    Returns
    =======
        points : np.ndarray
            [n x 3] matrix of seed-points coordinates.
    """

    # TODO: OPTIMIZE THIS CODE PLEASE!!!!!!!!!

    coords = np.stack([xx, yy, zz])
    # vector field
    vf = np.stack([uu, vv, ww])

    # extract the coordinate of the points at planes:
    # x_min, x_max, y_min, y_max, z_min, z_max
    c_xmin = coords[:, :, 0, :]
    c_xmax = coords[:, :, -1, :]
    c_ymin = coords[:, 0, :, :]
    c_ymax = coords[:, -1, :, :]
    c_zmin = coords[:, :, :, 0]
    c_zmax = coords[:, :, :, -1]

    # extract the vector field points at planes:
    # x_min, x_max, y_min, y_max, z_min, z_max
    vf_xmin = vf[:, :, 0, :]
    vf_xmax = vf[:, :, -1, :]
    vf_ymin = vf[:, 0, :, :]
    vf_ymax = vf[:, -1, :, :]
    vf_zmin = vf[:, :, :, 0]
    vf_zmax = vf[:, :, :, -1]

    def find_points_at_input_vectors(vf_plane, coords, i, sign="g"):
        check = {
            "g": lambda x: x > 0,
            "l": lambda x: x < 0,
        }
        # extract coordinates where the vectors are entering the plane
        tmp = np.where(
            check[sign](vf_plane[i, :, :]), coords, np.nan * np.zeros_like(coords)
        )
        # reshape the matrix to obtain an [n x 3] array of coordinates
        tmp = np.array(
            [tmp[0, :, :].flatten(), tmp[1, :, :].flatten(), tmp[2, :, :].flatten()]
        ).T
        # remove NaN entries
        tmp = [a for a in tmp if not np.all([np.isnan(t) for t in a])]
        return tmp

    p_xmin = find_points_at_input_vectors(vf_xmin, c_xmin, 0, "g")
    p_xmax = find_points_at_input_vectors(vf_xmax, c_xmax, 0, "l")
    p_ymin = find_points_at_input_vectors(vf_ymin, c_ymin, 1, "g")
    p_ymax = find_points_at_input_vectors(vf_ymax, c_ymax, 1, "l")
    p_zmin = find_points_at_input_vectors(vf_zmin, c_zmin, 2, "g")
    p_zmax = find_points_at_input_vectors(vf_zmax, c_zmax, 2, "l")
    # TODO: there could be duplicates
    points = np.array(p_xmin + p_xmax + p_ymin + p_ymax + p_zmin + p_zmax)
    return points
