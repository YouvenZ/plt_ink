"""
Plotly Grouped Bar Chart
Grouped bars rendered statically via Kaleido.
note: Plotly backend — assign your figure to 'fig'
tags: plotly, bars
"""

categories = ['Category A', 'Category B', 'Category C', 'Category D']
group1 = [23, 45, 30, 50]
group2 = [18, 35, 42, 38]
group3 = [32, 28, 55, 44]

fig = go.Figure(data=[
    go.Bar(name='Group 1', x=categories, y=group1),
    go.Bar(name='Group 2', x=categories, y=group2),
    go.Bar(name='Group 3', x=categories, y=group3),
])

fig.update_layout(
    barmode='group',
    title='Grouped Bar Chart',
    xaxis_title='Category',
    yaxis_title='Value',
    showlegend=_show_legend,
    width=int(_fig_width * 96),
    height=int(_fig_height * 96),
)
