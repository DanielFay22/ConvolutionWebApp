from django import forms

class ConvolutionForm(forms.Form):
    func1 = forms.CharField(label="Function 1")
    func2 = forms.CharField(label="Function 2")

    lower_bound = forms.DecimalField(label="Lower Bound")
    upper_bound = forms.DecimalField(label="Upper Bound")

    points = forms.DecimalField(label="Number of points",
                                initial=10000, required=False)

    method = forms.ChoiceField(
        widget=forms.RadioSelect(),
        choices=[("full", "Full"), ("same", "Same")],
        label="Convolution Method"
    )

    include_zero = forms.BooleanField(
        label="Shift to include 0",
        required=False
    )

    shade = forms.BooleanField(
        label="Fill Under Curve",
        required=False
    )

    show_func1 = forms.BooleanField(
        label="Show Function 1",
        required=False
    )

    show_func2 = forms.BooleanField(
        label="Show Function 2",
        required=False
    )


class FourierForm(forms.Form):

    c_k = forms.CharField(label="C_k")

    series_len = forms.IntegerField(label="Number of terms")

    lower_bound = forms.DecimalField(label="X Lower Bound")

    upper_bound = forms.DecimalField(label="X Upper Bound")

    points = forms.IntegerField(label="Number of Points")

    fundamental = forms.DecimalField(label="Fundamental Frequency")

    method = forms.ChoiceField(
        widget=forms.RadioSelect(),
        choices=[("all", "All K"),("even", "Only Even K"), ("odd", "Only Odd K")],
        label="Include Terms"
    )

    sweep_k = forms.BooleanField(
        label="Sweep k",
        required=False
    )

    k_start = forms.IntegerField(required=False)
    k_end = forms.IntegerField(required=False)
    k_step = forms.IntegerField(required=False)


    custom_sweep = forms.BooleanField(
        label="Custom Sweep",
        required=False
    )

    k_terms = forms.CharField(label="Comma-Separated K Values", required=False)


