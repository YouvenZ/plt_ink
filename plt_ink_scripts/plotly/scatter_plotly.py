# Plotly Scatter Plot with Color Scale
# Backend: Plotly + Kaleido

rng = np.random.default_rng(42)
n = 120
x = rng.normal(0, 1, n)
y = x * 0.8 + rng.normal(0, 0.5, n)
size = rng.uniform(5, 20, n)
color = rng.uniform(0, 1, n)

fig = go.Figure(go.Scatter(
    x=x, y=y,
    mode='markers',
    marker=dict(
        size=size,
        color=color,
        colorscale=_colormap,
        showscale=True,
        colorbar=dict(title='Value'),
        opacity=0.8,
    ),
    text=[f'Point {i}' for i in range(n)],
    hovertemplate='<b>%{text}</b><br>x=%{x:.2f}<br>y=%{y:.2f}<extra></extra>',
))

fig.update_layout(
    title='Scatter Plot',
    xaxis_title='X',
    yaxis_title='Y',
    width=int(_fig_width * 96),
    height=int(_fig_height * 96),
)
