from django.http import HttpResponse
from django.shortcuts import render

from .forms import ConvolutionForm, FourierForm

from numpy import *
import matplotlib
matplotlib.use("AGG")
import matplotlib.pylab as plt
import PIL, PIL.Image
from io import BytesIO

from .utils import *

def index_path(request):
    conv_form = ConvolutionForm()
    fourier_form = FourierForm()
    return render(request, "index.html",
                  {"conv_form": conv_form,
                   "fourier_form": fourier_form})


def convolve_path(request):
    if request.method == 'POST':
        form = ConvolutionForm(request.POST)
        if form.is_valid():
            if not form.cleaned_data['func1'].startswith("lambda"):
                form.cleaned_data['func1'] = 'lambda x: ' + form.cleaned_data['func1']
            if not form.cleaned_data['func2'].startswith("lambda"):
                form.cleaned_data['func2'] = 'lambda x: ' + form.cleaned_data['func2']

            buffer = _convolve_helper(form)
            return HttpResponse(buffer.getvalue(), content_type="image/png")

    else:
        form = ConvolutionForm()
        # form.method.prepare_value('full')# = 'full'
        form.points = 10000

    return render(request, "index.html", {'form':form})


def fourier_series_path(request):
    if request.method == 'POST':
        form = FourierForm(request.POST)
        if form.is_valid():
            if not form.cleaned_data['c_k'].startswith("lambda"):
                form.cleaned_data['c_k'] = 'lambda k: ' + form.cleaned_data['c_k']

            if form.cleaned_data['sweep_k'] or form.cleaned_data['custom_sweep']:
                buffer = _fourier_series_sweep(form)
            else:
                buffer = _fourier_series_helper(form)

            return HttpResponse(buffer.getvalue(), content_type="image/png")
    else:
        form = ConvolutionForm()

    return render(request, "index.html", {'fourier_form': form})




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


    ax1: plt.axis = plt.subplot2grid((3,2),(0,0), rowspan=2, colspan=2)
    if form.cleaned_data['show_func1']:
        ax1.plot(new_x, [f1(i) for i in new_x], label="Function 1",
                   color="orange", alpha=0.5)
    if form.cleaned_data['show_func2']:
        ax1.plot(new_x, [f2(i) for i in new_x], label="Function 2",
                   color="red", alpha=0.5)

    ax1.plot(new_x, convx, label="Convolution", color="blue")
    if form.cleaned_data["shade"]:
        ax1.fill_between(new_x, convx, 0, color="blue", alpha=0.15)

    ax1.set_title("$F_1(x) * F_2(x)$")
    plt.grid()
    plt.legend()

    ax2: plt.axis = plt.subplot2grid((3,2), (2,0))
    ax2.plot(new_x, [f1(i) for i in new_x])
    ax2.set_title("$F_1(x)$")

    ax3: plt.axis = plt.subplot2grid((3,2), (2,1))
    ax3.plot(new_x, [f2(i) for i in new_x])
    ax3.set_title("$F_2(x)$")

    plt.tight_layout()

    buffer = BytesIO()
    canvas = plt.get_current_fig_manager().canvas
    canvas.draw()

    pilImage = PIL.Image.frombytes("RGB", canvas.get_width_height(),
                                   canvas.tostring_rgb())
    pilImage.save(buffer, "PNG")
    plt.close()

    return buffer


def _fourier_series_helper(form):
    c_k = eval(form.cleaned_data['c_k'])
    n = float(form.cleaned_data['series_len'])
    l = float(form.cleaned_data['lower_bound'])
    u = float(form.cleaned_data['upper_bound'])
    f = float(form.cleaned_data['fundamental'])

    if form.cleaned_data['method'] != "all":
        # n = 2 * n
        if form.cleaned_data['method'] == "even":
            c_k = lambda k: eval(form.cleaned_data['c_k'])(k) * (1 - (k % 2))
        else:
            c_k = lambda k: eval(form.cleaned_data['c_k'])(k) * (k % 2)

    kl = -(n // 2)

    x = linspace(l, u, form.cleaned_data['points'])
    k = arange(kl, kl + n)
    ck = c_k(k)
    ck[(isinf(ck)) | (isnan(ck))] = 0

    s = matmul(ck, exp(2.0j * pi * outer(k, x) * f))
    print(s)

    plt.figure()
    plt.plot(x, real(s))

    buffer = BytesIO()
    canvas = plt.get_current_fig_manager().canvas
    canvas.draw()

    pilImage = PIL.Image.frombytes("RGB", canvas.get_width_height(),
                                   canvas.tostring_rgb())
    pilImage.save(buffer, "PNG")
    return buffer


def _fourier_series_sweep(form):
    c_k = eval(form.cleaned_data['c_k'])

    l = float(form.cleaned_data['lower_bound'])
    u = float(form.cleaned_data['upper_bound'])
    f = float(form.cleaned_data['fundamental'])

    if form.cleaned_data["custom_sweep"]:
        all_k = array(list(map(int, form.cleaned_data["k_terms"].split(","))))
    else:
        kstart = int(form.cleaned_data['k_start'])
        kend = int(form.cleaned_data['k_end'])
        kstep = int(form.cleaned_data['k_step'])
        all_k = arange(kstart, kend + 1, kstep)

    if form.cleaned_data['method'] != "all":
        if form.cleaned_data['method'] == "even":
            c_k = lambda k: eval(form.cleaned_data['c_k'])(k) * (1 - (k % 2))
        else:
            c_k = lambda k: eval(form.cleaned_data['c_k'])(k) * (k % 2)

    use_labels = all_k
    if all_k.shape[0] > 5:
        use_labels = all_k[::int(all_k.shape[0] / 5)]
        
    plt.figure()

    x = linspace(l, u, form.cleaned_data['points'])
    for n in all_k:

        kl = -(n // 2)


        k = arange(kl, kl + n)
        ck = c_k(k)
        ck[(isinf(ck)) | (isnan(ck))] = 0
        s = matmul(ck, exp(2.0j * pi * outer(k, x) * f))

        if n in use_labels:
            plt.plot(x, real(s), label=f"{n} terms")
        else:
            plt.plot(x, real(s), label=None)
        
    
    plt.legend()
    plt.grid()

    buffer = BytesIO()
    canvas = plt.get_current_fig_manager().canvas
    canvas.draw()

    pilImage = PIL.Image.frombytes("RGB", canvas.get_width_height(),
                                   canvas.tostring_rgb())
    pilImage.save(buffer, "PNG")
    return buffer

