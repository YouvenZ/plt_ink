"""
Plotly Line Chart
Basic interactive-style line chart rendered statically via Kaleido.
note: Plotly backend — assign your figure to 'fig'
tags: plotly, line
"""

x = np.linspace(0, 2 * np.pi, 200)
y_sin = np.sin(x)
y_cos = np.cos(x)

fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=y_sin, mode='lines', name='sin(x)',
                         line=dict(width=2)))
fig.add_trace(go.Scatter(x=x, y=y_cos, mode='lines', name='cos(x)',
                         line=dict(width=2, dash='dash')))

fig.update_layout(
    title='Sine and Cosine',
    xaxis_title='x',
    yaxis_title='y',
    width=int(_fig_width * 96),
    height=int(_fig_height * 96),
    showlegend=_show_legend,
)
