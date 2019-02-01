from django import forms

class FunctionForm(forms.Form):
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