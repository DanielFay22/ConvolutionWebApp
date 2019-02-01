from django.http import HttpResponse
from django.shortcuts import render

from .forms import FunctionForm

from numpy import *
import matplotlib
matplotlib.use("AGG")
from matplotlib import pylab
import PIL, PIL.Image
from io import BytesIO

from .utils import *


def convolve_path(request):
    if request.method == 'GET':
        form = FunctionForm(request.GET)
        if form.is_valid():
            if not form.cleaned_data['func1'].startswith("lambda"):
                form.cleaned_data['func1'] = 'lambda x: ' + form.cleaned_data['func1']
            if not form.cleaned_data['func2'].startswith("lambda"):
                form.cleaned_data['func2'] = 'lambda x: ' + form.cleaned_data['func2']

            buffer = _convolve_helper(form)
            return HttpResponse(buffer.getvalue(), content_type="image/png")

    else:
        form = FunctionForm()
        # form.method.prepare_value('full')# = 'full'
        form.points = 10000



    return render(request, "input.html", {'form':form})



def _convolve_helper(form):
    f1 = eval(form.cleaned_data['func1'])
    f2 = eval(form.cleaned_data['func2'])
    l = float(form.cleaned_data['lower_bound'])
    u = float(form.cleaned_data['upper_bound'])

    x = linspace(l, u, form.cleaned_data['points'])
    if form.cleaned_data['include_zero']:
        x += min(abs(x))

    x1 = [f1(i) for i in x]
    x2 = [f2(i) for i in x]

    convx = convolve(x1, x2, form.cleaned_data['method'].lower()) * (x[1] - x[0])

    new_x = linspace(l, u, 2 * x.shape[0] - 1) * 2
    if form.cleaned_data['method'].lower() == 'same':
        new_x = new_x[int(0.25 * new_x.shape[0]):-int(0.25 * new_x.shape[0]) - 1]


    ax1: pylab.axis = pylab.subplot2grid((3,2),(0,0), rowspan=2, colspan=2)
    if form.cleaned_data['show_func1']:
        ax1.plot(new_x, [f1(i) for i in new_x], label="Function 1",
                   color="orange", alpha=0.4)
    if form.cleaned_data['show_func2']:
        ax1.plot(new_x, [f2(i) for i in new_x], label="Function 2",
                   color="red", alpha=0.4)

    ax1.plot(new_x, convx, label="Convolution", color="blue")
    if form.cleaned_data["shade"]:
        ax1.fill_between(new_x, convx, 0, color="blue", alpha=0.15)

    ax1.set_title("$F_1(x) * F_2(x)$")
    pylab.grid()
    pylab.legend()

    ax2: pylab.axis = pylab.subplot2grid((3,2), (2,0))
    ax2.plot(new_x, [f1(i) for i in new_x])
    ax2.set_title("$F_1(x)$")

    ax3: pylab.axis = pylab.subplot2grid((3,2), (2,1))
    ax3.plot(new_x, [f2(i) for i in new_x])
    ax3.set_title("$F_2(x)$")

    pylab.tight_layout()

    buffer = BytesIO()
    canvas = pylab.get_current_fig_manager().canvas
    canvas.draw()

    pilImage = PIL.Image.frombytes("RGB", canvas.get_width_height(),
                                   canvas.tostring_rgb())
    pilImage.save(buffer, "PNG")
    pylab.close()

    return buffer