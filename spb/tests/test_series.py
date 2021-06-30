from sympy import (
    symbols, cos, sin, log, Eq, I, Abs, exp, pi, gamma, Matrix, Tuple, Plane, S
)
from spb.series import (
    LineOver1DRangeSeries, Parametric2DLineSeries, Parametric3DLineSeries,
    ParametricSurfaceSeries, SurfaceOver2DRangeSeries, InteractiveSeries,
    ImplicitSeries, Vector2DSeries, Vector3DSeries, ComplexSeries,
    ComplexInteractiveSeries, SliceVector3DSeries
)
import numpy as np

def test_lin_log_scale():
    # Verify that data series create the correct spacing in the data.
    x, y, z = symbols("x, y, z")

    s = LineOver1DRangeSeries(x, (x, 1, 10),
                adaptive=False, n=50, xscale="linear")
    xx, _ = s.get_data()
    assert np.isclose(xx[1] - xx[0], xx[-1] - xx[-2])

    s = LineOver1DRangeSeries(x, (x, 1, 10),
                adaptive=False, n=50, xscale="log")
    xx, _ = s.get_data()
    assert not np.isclose(xx[1] - xx[0], xx[-1] - xx[-2])

    s = Parametric2DLineSeries(cos(x), sin(x), (x, pi / 2, 1.5 * pi),
                adaptive=False, n=50, xscale="linear")
    _, _, param = s.get_data()
    assert np.isclose(param[1] - param[0], param[-1] - param[-2])

    s = Parametric2DLineSeries(cos(x), sin(x), (x, pi / 2, 1.5 * pi),
                adaptive=False, n=50, xscale="log")
    _, _, param = s.get_data()
    assert not np.isclose(param[1] - param[0], param[-1] - param[-2])

    s = Parametric3DLineSeries(cos(x), sin(x), x, (x, pi / 2, 1.5 * pi),
                adaptive=False, n=50, xscale="linear")
    _, _, _, param = s.get_data()
    assert np.isclose(param[1] - param[0], param[-1] - param[-2])

    s = Parametric3DLineSeries(cos(x), sin(x), x, (x, pi / 2, 1.5 * pi),
                adaptive=False, n=50, xscale="log")
    _, _, _, param = s.get_data()
    assert not np.isclose(param[1] - param[0], param[-1] - param[-2])

    s = SurfaceOver2DRangeSeries(cos(x**2 + y**2), (x, 1, 5), (y, 1, 5),
                n=10, xscale="linear", yscale="linear")
    xx, yy, _ = s.get_data()
    assert np.isclose(xx[0, 1] - xx[0, 0], xx[0, -1] - xx[0, -2])
    assert np.isclose(yy[1, 0] - yy[0, 0], yy[-1, 0] - yy[-2, 0])

    s = SurfaceOver2DRangeSeries(cos(x**2 + y**2), (x, 1, 5), (y, 1, 5),
                n=10, xscale="log", yscale="log")
    xx, yy, _ = s.get_data()
    assert not np.isclose(xx[0, 1] - xx[0, 0], xx[0, -1] - xx[0, -2])
    assert not np.isclose(yy[1, 0] - yy[0, 0], yy[-1, 0] - yy[-2, 0])

    s = ImplicitSeries(cos(x**2 + y**2) > 0, (x, 1, 5), (y, 1, 5),
                n=10, xscale="linear", yscale="linear", adaptive=False)
    xx, yy, _, _, _ = s.get_data()
    assert np.isclose(xx[1] - xx[0], xx[-1] - xx[-2])
    assert np.isclose(yy[1] - yy[0], yy[-1] - yy[-2])

    s = ImplicitSeries(cos(x**2 + y**2) > 0, (x, 1, 5), (y, 1, 5),
                n=10, xscale="log", yscale="log", adaptive=False)
    xx, yy, _, _, _ = s.get_data()
    assert not np.isclose(xx[1] - xx[0], xx[-1] - xx[-2])
    assert not np.isclose(yy[1] - yy[0], yy[-1] - yy[-2])

    s = InteractiveSeries([log(x)], [(x, 1e-05, 1e05)],
                n=10, xscale="linear")
    xx, yy = s.get_data()
    assert np.isclose(xx[1] - xx[0], xx[-1] - xx[-2])


    s = InteractiveSeries([log(x)], [(x, 1e-05, 1e05)],
                n=10, xscale="log")
    xx, yy = s.get_data()
    assert not np.isclose(xx[1] - xx[0], xx[-1] - xx[-2])

    s = ComplexSeries(cos(x), (x, 1e-05, 1e05), real=True, imag=False,
                n=10, xscale="linear")
    xx, yy = s.get_data()
    assert np.isclose(xx[1] - xx[0], xx[-1] - xx[-2])

    s = ComplexSeries(cos(x), (x, 1e-05, 1e05), real=True, imag=False,
                n=10, xscale="log")
    xx, yy = s.get_data()
    assert not np.isclose(xx[1] - xx[0], xx[-1] - xx[-2])

    s = Vector3DSeries(x, y, z, (x, 1, 1e05), (y, 1, 1e05),
                (z, 1, 1e05), xscale="linear", yscale="linear", zscale="linear")
    xx, yy, zz, _, _, _ = s.get_data()
    assert np.isclose(xx[0, :, 0][1] - xx[0, :, 0][0], xx[0, :, 0][-1] - xx[0, :, 0][-2])
    assert np.isclose(yy[:, 0, 0][1] - yy[:, 0, 0][0], yy[:, 0, 0][-1] - yy[:, 0, 0][-2])
    assert np.isclose(zz[0, 0, :][1] - zz[0, 0, :][0], zz[0, 0, :][-1] - zz[0, 0, :][-2])

    s = Vector3DSeries(x, y, z, (x, 1, 1e05), (y, 1, 1e05),
                (z, 1, 1e05), xscale="log", yscale="log",zscale="log")
    xx, yy, zz, _, _, _ = s.get_data()
    assert not np.isclose(xx[0, :, 0][1] - xx[0, :, 0][0], xx[0, :, 0][-1] - xx[0, :, 0][-2])
    assert not np.isclose(yy[:, 0, 0][1] - yy[:, 0, 0][0], yy[:, 0, 0][-1] - yy[:, 0, 0][-2])
    assert not np.isclose(zz[0, 0, :][1] - zz[0, 0, :][0], zz[0, 0, :][-1] - zz[0, 0, :][-2])

def test_data_shape():
    # Verify that the series produces the correct data shape when the input
    # expression is a number.
    u, x, y, z = symbols("u, x:z")

    # scalar expression: it should return a numpy ones array
    s = LineOver1DRangeSeries(1, (x, -5, 5))
    xx, yy = s.get_data()
    assert len(xx) == len(yy)
    assert np.all(yy == 1)

    s = LineOver1DRangeSeries(1, (x, -5, 5), adaptive=False)
    xx, yy = s.get_data()
    assert len(xx) == len(yy)
    assert np.all(yy == 1)

    s = Parametric2DLineSeries(sin(x), 1, (x, 0, pi))
    xx, yy, param = s.get_data()
    assert (len(xx) == len(yy)) and (len(xx) == len(param))
    assert np.all(yy == 1)

    s = Parametric2DLineSeries(1, sin(x), (x, 0, pi))
    xx, yy, param = s.get_data()
    assert (len(xx) == len(yy)) and (len(xx) == len(param))
    assert np.all(xx == 1)

    s = Parametric2DLineSeries(sin(x), 1, (x, 0, pi), adaptive=False)
    xx, yy, param = s.get_data()
    assert (len(xx) == len(yy)) and (len(xx) == len(param))
    assert np.all(yy == 1)

    s = Parametric2DLineSeries(1, sin(x), (x, 0, pi), adaptive=False)
    xx, yy, param = s.get_data()
    assert (len(xx) == len(yy)) and (len(xx) == len(param))
    assert np.all(xx == 1)

    s = Parametric3DLineSeries(cos(x), sin(x), 1, (x, 0, 2 * pi))
    xx, yy, zz, param = s.get_data()
    assert ((len(xx) == len(yy)) and (len(xx) == len(zz)) and 
        (len(xx) == len(param)))
    assert np.all(zz == 1)

    s = Parametric3DLineSeries(cos(x), 1, x, (x, 0, 2 * pi))
    xx, yy, zz, param = s.get_data()
    assert ((len(xx) == len(yy)) and (len(xx) == len(zz)) and 
        (len(xx) == len(param)))
    assert np.all(yy == 1)

    s = Parametric3DLineSeries(1, sin(x), x, (x, 0, 2 * pi))
    xx, yy, zz, param = s.get_data()
    assert ((len(xx) == len(yy)) and (len(xx) == len(zz)) and 
        (len(xx) == len(param)))
    assert np.all(xx == 1)

    s = SurfaceOver2DRangeSeries(1, (x, -2, 2), (y, -3, 3))
    xx, yy, zz = s.get_data()
    assert (xx.shape == yy.shape) and (xx.shape == zz.shape)
    assert np.all(zz == 1)

    s = ParametricSurfaceSeries(1, x, y, (x, 0, 1), (y, 0, 1))
    xx, yy, zz = s.get_data()
    assert (xx.shape == yy.shape) and (xx.shape == zz.shape)
    assert np.all(xx == 1)

    s = ParametricSurfaceSeries(1, 1, y, (x, 0, 1), (y, 0, 1))
    xx, yy, zz = s.get_data()
    assert (xx.shape == yy.shape) and (xx.shape == zz.shape)
    assert np.all(yy == 1)

    s = ParametricSurfaceSeries(x, 1, 1, (x, 0, 1), (y, 0, 1))
    xx, yy, zz = s.get_data()
    assert (xx.shape == yy.shape) and (xx.shape == zz.shape)
    assert np.all(zz == 1)

    s = ComplexSeries(1, (x, -5, 5), real = True, imag = False)
    xx, yy = s.get_data()
    assert len(xx) == len(yy)
    assert np.all(yy == 1)

    s = ComplexSeries(1, (x, -5, 5), real = False, imag = True)
    xx, yy = s.get_data()
    assert len(xx) == len(yy)
    assert np.all(yy == 0)

    s = ComplexSeries(1, (x, -5, 5), absarg = True)
    xx, mag, arg = s.get_data()
    assert (len(xx) == len(mag)) and (len(xx) == len(arg))
    assert np.all(mag == 1)

    s = ComplexSeries(1, (x, - 5 - 2 * I, 5 + 2 * I))
    rr, ii, mag_arg, colors, _ = s.get_data()
    assert (rr.shape == ii.shape) and (rr.shape[:2] == colors.shape[:2])

    # Corresponds to LineOver1DRangeSeries
    s = InteractiveSeries([S.One], [Tuple(x, -5, 5)])
    s.update_data(dict())
    xx, yy = s.get_data()
    assert len(xx) == len(yy)
    assert np.all(yy == 1)

    # Corresponds to Parametric2DLineSeries
    s = InteractiveSeries([S.One, sin(x)], [Tuple(x, 0, pi)])
    s.update_data(dict())
    xx, yy, param = s.get_data()
    assert (len(xx) == len(yy)) and (len(xx) == len(param))
    assert np.all(xx == 1)

    s = InteractiveSeries([sin(x), S.One], [Tuple(x, 0, pi)])
    s.update_data(dict())
    xx, yy, param = s.get_data()
    assert (len(xx) == len(yy)) and (len(xx) == len(param))
    assert np.all(yy == 1)

    # Corresponds to Parametric3DLineSeries
    s = InteractiveSeries([cos(x), sin(x), S.One], [(x, 0, 2 * pi)])
    s.update_data(dict())
    xx, yy, zz, param = s.get_data()
    assert ((len(xx) == len(yy)) and (len(xx) == len(param)) and 
        (len(xx) == len(zz)))
    assert np.all(zz == 1)

    s = InteractiveSeries([S.One, sin(x), x], [(x, 0, 2 * pi)])
    s.update_data(dict())
    xx, yy, zz, param = s.get_data()
    assert ((len(xx) == len(yy)) and (len(xx) == len(param)) and 
        (len(xx) == len(zz)))
    assert np.all(xx == 1)

    s = InteractiveSeries([cos(x), S.One, x], [(x, 0, 2 * pi)])
    s.update_data(dict())
    xx, yy, zz, param = s.get_data()
    assert ((len(xx) == len(yy)) and (len(xx) == len(param)) and 
        (len(xx) == len(zz)))
    assert np.all(yy == 1)
    
    # Corresponds to SurfaceOver2DRangeSeries
    s = InteractiveSeries([S.One], [(x, -2, 2), (y, -3, 3)])
    s.update_data(dict())
    xx, yy, zz = s.get_data()
    assert (xx.shape == yy.shape) and (xx.shape == zz.shape)
    assert np.all(zz == 1)

    # Corresponds to ParametricSurfaceSeries
    s = InteractiveSeries([S.One, x, y], [(x, 0, 1), (y, 0, 1)])
    s.update_data(dict())
    xx, yy, zz = s.get_data()
    assert (xx.shape == yy.shape) and (xx.shape == zz.shape)
    assert np.all(xx == 1)

    s = InteractiveSeries([x, S.One, y], [(x, 0, 1), (y, 0, 1)])
    s.update_data(dict())
    xx, yy, zz = s.get_data()
    assert (xx.shape == yy.shape) and (xx.shape == zz.shape)
    assert np.all(yy == 1)

    s = InteractiveSeries([x, y, S.One], [(x, 0, 1), (y, 0, 1)])
    s.update_data(dict())
    xx, yy, zz = s.get_data()
    assert (xx.shape == yy.shape) and (xx.shape == zz.shape)
    assert np.all(zz == 1)

    s = ComplexInteractiveSeries(S.One, (x, -5, 5), real=True, imag=False)
    s.update_data(dict())
    xx, yy = s.get_data()
    assert len(xx) == len(yy)


def test_interactive():
    u, x, y, z = symbols("u, x:z")

    # verify that InteractiveSeries produces the same numerical data as their
    # corresponding non-interactive series.
    def do_test(data1, data2):
        assert len(data1) == len(data2)
        for d1, d2 in zip(data1, data2):
            assert np.array_equal(d1, d2)

    s1 = InteractiveSeries([u * cos(x)], [(x, -5, 5)], "", params={u: 1}, n1=50)
    s2 = LineOver1DRangeSeries(cos(x), (x, -5, 5), "", adaptive=False, n=50)
    do_test(s1.get_data(), s2.get_data())
    
    s1 = InteractiveSeries([u * cos(x), u* sin(x)], [(x, -5, 5)], "", params={u: 1}, n1=50)
    s2 = Parametric2DLineSeries(cos(x), sin(x), (x, -5, 5), "", adaptive=False, n=50)
    do_test(s1.get_data(), s2.get_data())
    
    s1 = InteractiveSeries([u * cos(x), u* sin(x), u * x], [(x, -5, 5)], "", 
            params={u: 1}, n1=50)
    s2 = Parametric3DLineSeries(cos(x), sin(x), x, (x, -5, 5), "", 
            adaptive=False, n=50)
    do_test(s1.get_data(), s2.get_data())
    
    s1 = InteractiveSeries([cos(x**2 + y**2)], [(x, -3, 3), (y, -3, 3)], "", 
            params={u: 1}, n1=50, n2=50)
    s2 = SurfaceOver2DRangeSeries(cos(x**2 + y**2), (x, -3, 3), (y, -3, 3), "", 
            adaptive=False, n1=50, n2=50)
    do_test(s1.get_data(), s2.get_data())
    
    s1 = InteractiveSeries([cos(x + y), sin(x + y), x - y], 
            [(x, -3, 3), (y, -3, 3)], "", 
            params={u: 1}, n1=50, n2=50)
    s2 = ParametricSurfaceSeries(cos(x + y), sin(x + y), x - y, 
            (x, -3, 3), (y, -3, 3), "", 
            adaptive=False, n1=50, n2=50)
    do_test(s1.get_data(), s2.get_data())
    
    s1 = InteractiveSeries([-u * y, u * x], [(x, -3, 3), (y, -2, 2)], 
            "", params={u: 1}, n1=15, n2=15)
    s2 = Vector2DSeries(-y, x, (x, -3, 3), (y, -2, 2), "", 
            n1=15, n2=15)
    do_test(s1.get_data(), s2.get_data())
    
    s1 = InteractiveSeries([u * z, -u * y, u * x], [(x, -3, 3), (y, -2, 2),
            (z, -1, 1)], "", params={u: 1}, n1=15, n2=15, n3=15)
    s2 = Vector3DSeries(z, -y, x, (x, -3, 3), (y, -2, 2), (z, -1, 1), "", 
            n1=15, n2=15, n3=15)
    do_test(s1.get_data(), s2.get_data())

    s1 = InteractiveSeries([u * z, -u * y, u * x], [(x, -3, 3), (y, -2, 2),
            (z, -1, 1)], "", params={u: 1},
            slice = Plane((-1, 0, 0), (1, 0, 0)),
            n1=15, n2=15, n3=15)
    s2 = SliceVector3DSeries(Plane((-1, 0, 0), (1, 0, 0)),
            z, -y, x, (x, -3, 3), (y, -2, 2), (z, -1, 1), "", 
            n1=15, n2=15, n3=15)
    do_test(s1.get_data(), s2.get_data())

    
    ### Test ComplexInteractiveSeries

    # real and imag
    s1 = ComplexInteractiveSeries((z**2 + 1) / (z**2 - 1), (z, -3, 3), 
            "", n1=50)
    s2 = ComplexSeries((z**2 + 1) / (z**2 - 1), (z, -3, 3), 
            "", n1=50)
    do_test(s1.get_data(), s2.get_data())

    # only real
    s1 = ComplexInteractiveSeries((z**2 + 1) / (z**2 - 1), (z, -3, 3), 
            "", n1=50, imag=False)
    s2 = ComplexSeries((z**2 + 1) / (z**2 - 1), (z, -3, 3), 
            "", n1=50, imag=False)
    do_test(s1.get_data(), s2.get_data())

    # only imag
    s1 = ComplexInteractiveSeries((z**2 + 1) / (z**2 - 1), (z, -3, 3), 
            "", n1=50, real=False)
    s2 = ComplexSeries((z**2 + 1) / (z**2 - 1), (z, -3, 3), 
            "", n1=50, real=False)
    do_test(s1.get_data(), s2.get_data())

    # magnitude and argument
    s1 = ComplexInteractiveSeries((z**2 + 1) / (z**2 - 1), (z, -3, 3), 
            "", n1=50, absarg=True)
    s2 = ComplexSeries((z**2 + 1) / (z**2 - 1), (z, -3, 3), 
            "", n1=50, absarg=True)
    do_test(s1.get_data(), s2.get_data())

    # domai coloring or 3D
    s1 = ComplexInteractiveSeries((z**2 + 1) / (z**2 - 1), 
            (z, -3 - 4 * I, 3 + 4 * I), "", n1=50)
    s2 = ComplexSeries((z**2 + 1) / (z**2 - 1),
            (z, -3 - 4 * I, 3 + 4 * I), "", n1=50)
    do_test(s1.get_data(), s2.get_data())


