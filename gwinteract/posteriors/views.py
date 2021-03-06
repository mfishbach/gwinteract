# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse

from django.shortcuts import render
from .forms import PosteriorForm
from ligo.gracedb.rest import GraceDb, HTTPError
from gwpy.table import EventTable

import seaborn

from matplotlib import use
use('agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

# Create your views here.
def index(request):
    form = PosteriorForm()
    return render(request, 'form.html', {'form': form})


def posteriors(request):
    # if this is a POST request we need to process the form data
    if request.method == 'GET':

        # create a form instance and populate it with data from the request:
        form = PosteriorForm(request.GET)
        # check whether it's valid:
        if form.is_valid():
            graceid = form.cleaned_data['graceid']
            param1 = form.cleaned_data['param1']
            param2 = form.cleaned_data['param2']
            param1_min = form.cleaned_data['param1_min']
            param1_max = form.cleaned_data['param1_max']
            param2_min = form.cleaned_data['param2_min']
            param2_max = form.cleaned_data['param2_max']
            client = GraceDb("https://gracedb-playground.ligo.org/api/")
            #event = client.event(graceid)
            #filename = client.files(graceid, 'event.log')
            ps = EventTable.fetch('gravityspy', '\"{0}\"'.format(graceid),
                                  selection=['{0}<{1}<{2}'.format(param1_min, param1, param1_max),
                                             '{0}<{1}<{2}'.format(param2_min, param2, param2_max)],
                                  columns=[param1, param2])
            ps = ps.to_pandas().iloc[0:1000]
            old = 'posteriors'
            new = 'histogram'
            histogramurl = (request.get_full_path()[::-1].replace(old[::-1], new[::-1], 1))[::-1]

            return render(request, 'gracedb.html', {'results' : ps.iloc[0:1000].to_dict(orient='records'), 'histogramurl' : histogramurl})
        else:
            return render(request, 'form.html', {'form': form})


def histogram(request):
    # if this is a POST request we need to process the form data
    if request.method == 'GET':

        # create a form instance and populate it with data from the request:
        form = PosteriorForm(request.GET)
        # check whether it's valid:
        if form.is_valid():
            graceid = form.cleaned_data['graceid']
            param1 = form.cleaned_data['param1']
            param2 = form.cleaned_data['param2']
            param1_min = form.cleaned_data['param1_min']
            param1_max = form.cleaned_data['param1_max']
            param2_min = form.cleaned_data['param2_min']
            param2_max = form.cleaned_data['param2_max']
            client = GraceDb("https://gracedb-playground.ligo.org/api/")
            #event = client.event(graceid)
            #filename = client.files(graceid, 'event.log')
            ps = EventTable.fetch('gravityspy', '\"{0}\"'.format(graceid),
                                  selection=['{0}<{1}<{2}'.format(param1_min, param1, param1_max),
                                             '{0}<{1}<{2}'.format(param2_min, param2, param2_max)],
                                  columns=[param1, param2])
            ps = ps.to_pandas().iloc[0:1000]

            with seaborn.axes_style('white'):
                plot = seaborn.jointplot(param1, param2, ps, kind='kde')

            fig = plot.fig
            canvas = FigureCanvas(fig)

            import io
            buf = io.BytesIO()
            canvas.print_png(buf)
            response=HttpResponse(buf.getvalue(),content_type='image/png')
            fig.clear()
            return response
