#Grafici interattivi dati inquinamento
#import plotly.plotly as py
from chart_studio import plotly as py
import plotly.graph_objs as go
import plotly.offline as pyoff
#from plotly.offline import iplot
from plotly.offline import plot


from datetime import datetime
import pandas as pd

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv')
df.columns = [col.replace('AAPL.', '') for col in df.columns]

trace_high = go.Scatter(x=list(df.index),
                        y=list(df.High),
                        name='High',
                        line=dict(color='#33CFA5'))

trace_high_avg = go.Scatter(x=list(df.index),
                            y=[df.High.mean()]*len(df.index),
                            name='High Average',
                            visible=False,
                            line=dict(color='#33CFA5', dash='dash'))

trace_low = go.Scatter(x=list(df.index),
                       y=list(df.Low),
                       name='Low',
                       line=dict(color='#F06A6A'))

trace_low_avg = go.Scatter(x=list(df.index),
                           y=[df.Low.mean()]*len(df.index),
                           name='Low Average',
                           visible=False,
                           line=dict(color='#F06A6A', dash='dash'))

data = [trace_high, trace_high_avg, trace_low, trace_low_avg]

high_annotations=[dict(x='2016-03-01',
                       y=df.High.mean(),
                       xref='x', yref='y',
                       text='High Average:<br>'+str(df.High.mean()),
                       ax=0, ay=-40),
                  dict(x=df.High.idxmax(),
                       y=df.High.max(),
                       xref='x', yref='y',
                       text='High Max:<br>'+str(df.High.max()),
                       ax=0, ay=-40)]
low_annotations=[dict(x='2015-05-01',
                      y=df.Low.mean(),
                      xref='x', yref='y',
                      text='Low Average:<br>'+str(df.Low.mean()),
                      ax=0, ay=40),
                 dict(x=df.High.idxmin(),
                      y=df.Low.min(),
                      xref='x', yref='y',
                      text='Low Min:<br>'+str(df.Low.min()),
                      ax=0, ay=40)]

updatemenus = list([
    dict(type="buttons",
         active=-1,
         buttons=list([
            dict(label = 'High',
                 method = 'update',
                 args = [{'visible': [True, True, False, False]},
                         {'title': 'Yahoo High',
                          'annotations': high_annotations}]),
            dict(label = 'Low',
                 method = 'update',
                 args = [{'visible': [False, False, True, True]},
                         {'title': 'Yahoo Low',
                          'annotations': low_annotations}]),
            dict(label = 'Both',
                 method = 'update',
                 args = [{'visible': [True, True, True, True]},
                         {'title': 'Yahoo',
                          'annotations': high_annotations+low_annotations}]),
            dict(label = 'Reset',
                 method = 'update',
                 args = [{'visible': [True, False, True, False]},
                         {'title': 'Yahoo',
                          'annotations': []}])
        ]),
    )
])

layout = dict(title='Yahoo', showlegend=False,
              updatemenus=updatemenus)

fig = dict(data=data, layout=layout)
plot(fig, filename='update_button')
plot(fig)
