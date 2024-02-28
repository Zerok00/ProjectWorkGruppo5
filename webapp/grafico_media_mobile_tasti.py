#Grafici interattivi dati inquinamento

import plotly.graph_objs as go
from plotly.offline import plot
import pandas as pd

#QUERY PER SELZIONARE DATI DA PRENDERE (STAZIONE E POLLUTIONS)
#query =

df = pd.read_csv('rilevazione1.csv')
print(df)
#df.columns = [col.replace('AAPL.', '') for col in df.columns]

trace = go.Bar(x=list(df.data),
                        y=list(df.valore),
                        name='Valore',
                        marker=dict(color='#33CFA5'),)

# trace_high_avg = go.Scatter(x=list(df.index),
#                             y=[df.High.mean()]*len(df.index),
#                             name='High Average',
#                             visible=False,
#                             line=dict(color='#33CFA5', dash='dash'))
#
# trace_low = go.Scatter(x=list(df.index),
#                        y=list(df.Low),
#                        name='Low',
#                        line=dict(color='#F06A6A'))
#
# trace_low_avg = go.Scatter(x=list(df.index),
#                            y=[df.Low.mean()]*len(df.index),
#                            name='Low Average',
#                            visible=False,
#                            line=dict(color='#F06A6A', dash='dash'))

data = [ trace ]
#
# high_annotations=[dict(x='2016-03-01',
#                        y=df.High.mean(),
#                        xref='x', yref='y',
#                        text='High Average:<br>'+str(df.High.mean()),
#                        ax=0, ay=-40),
#                   dict(x=df.High.idxmax(),
#                        y=df.High.max(),
#                        xref='x', yref='y',
#                        text='High Max:<br>'+str(df.High.max()),
#                        ax=0, ay=-40)]
# low_annotations=[dict(x='2015-05-01',
#                       y=df.Low.mean(),
#                       xref='x', yref='y',
#                       text='Low Average:<br>'+str(df.Low.mean()),
#                       ax=0, ay=40),
#                  dict(x=df.High.idxmin(),
#                       y=df.Low.min(),
#                       xref='x', yref='y',
#                       text='Low Min:<br>'+str(df.Low.min()),
#                       ax=0, ay=40)]
#
updatemenus = list([
    dict(type="buttons",
         active=-1,
         buttons=list([
            dict(label = 'High',
                 method = 'update',
                 args = [{'visible': [True, True, False, False]},
                         {'title': 'Yahoo High',
                          'annotations': ""}]),
            dict(label = 'Low',
                 method = 'update',
                 args = [{'visible': [False, False, True, True]},
                         {'title': 'Yahoo Low',
                          'annotations': ""}]),
            dict(label = 'Both',
                 method = 'update',
                 args = [{'visible': [True, True, True, True]},
                         {'title': 'Yahoo',
                          'annotations': ""}]),
            dict(label = 'Reset',
                 method = 'update',
                 args = [{'visible': [True, False, True, False]},
                         {'title': 'Yahoo',
                          'annotations': ""}])
        ]),
    )
])

layout = dict(title='Provaaaaaaaaaaaaaaaaaaaaaaaaaaa', showlegend=False,
              updatemenus=updatemenus)

fig = dict(data=data, layout=layout)
plot(fig, filename='rilevazione.html')
# plot(fig)
