import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, text

# 1. THE PALETTE
COLORS = {'background': '#F4F7F9', 'text': '#2C3E50', 'primary': '#3498DB', 
          'secondary': '#E67E22', 'accent': '#2ECC71', 'grid': '#DCDDE1'}

# 2. THE CONNECTION (Bulletproof Version)
# We use a raw string for the query and a legacy-compatible connection style
engine = create_engine('postgresql://pipeline_user:mypassword@localhost:5432/sales_db')

query = """
    SELECT 
        f.total_amount, f.order_date, f.customer_id, f.quantity,
        p.product_name, p.category,
        r.region_name
    FROM warehouse.fact_sales f
    JOIN warehouse.dim_products p ON f.product_id = p.product_id
    JOIN warehouse.dim_regions r ON f.region_id = r.region_id
"""

# Bypassing the text() wrapper entirely to stop the TypeError
# 2. DATABASE CONNECTION (Optimized)
with engine.connect() as conn:
    result = conn.execute(text(query))
    df = pd.DataFrame(result.mappings().all())

# --- ADD THESE LINES HERE ---
df['total_amount'] = pd.to_numeric(df['total_amount'], errors='coerce')
df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
# ----------------------------

# --- THE REST OF YOUR DATA PREP ---
df['order_date'] = pd.to_datetime(df['order_date'])
df['month'] = df['order_date'].dt.strftime('%Y-%m')
df['weekday'] = pd.Categorical(df['order_date'].dt.day_name(), 
                              categories=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'], 
                              ordered=True)

# KPI CALCULATIONS
total_revenue = df['total_amount'].sum()
total_orders = len(df)
avg_order = df['total_amount'].mean()
unique_customers = df['customer_id'].nunique()

# --- DASHBOARD LAYOUT ---
app = dash.Dash(__name__)

# Re-using the helper for consistent style
def apply_layout(fig, title):
    fig.update_layout(
        title={'text': f"<b>{title}</b>", 'x': 0.05, 'font': {'size': 20, 'color': COLORS['text']}},
        paper_bgcolor='white', plot_bgcolor='white', margin=dict(l=50, r=30, t=80, b=50),
        font_family="Arial, sans-serif"
    )
    fig.update_xaxes(showgrid=True, gridcolor=COLORS['grid'])
    fig.update_yaxes(showgrid=True, gridcolor=COLORS['grid'])
    return fig

app.layout = html.Div(style={'backgroundColor': COLORS['background'], 'fontFamily': 'sans-serif', 'padding': '20px'}, children=[
    html.H1("EXECUTIVE SALES INTELLIGENCE", style={'color': COLORS['text'], 'marginBottom': '30px'}),
    
    # KPIs
    html.Div([
        html.Div([html.P("Revenue"), html.H2(f"${total_revenue:,.0f}")], className='kpi-card'),
        html.Div([html.P("Orders"), html.H2(f"{total_orders:,}")], className='kpi-card'),
        html.Div([html.P("Avg Ticket"), html.H2(f"${avg_order:,.0f}")], className='kpi-card'),
        html.Div([html.P("Customers"), html.H2(f"{unique_customers:,}")], className='kpi-card'),
    ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '30px'}),

    # CHARTS
    html.Div([
        dcc.Graph(figure=apply_layout(px.bar(df.groupby('product_name')['total_amount'].sum().nlargest(10).reset_index(), 
                  x='total_amount', y='product_name', orientation='h', color_discrete_sequence=[COLORS['primary']]), "Top Products")),
        dcc.Graph(figure=apply_layout(px.treemap(df, path=[px.Constant("Total"), 'category', 'product_name'], values='total_amount', 
                  color_discrete_sequence=px.colors.sequential.Blues_r), "Category Mix")),
    ], style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '20px'}),
    
    html.Div([
        dcc.Graph(figure=apply_layout(px.line(df.groupby('month')['total_amount'].sum().reset_index(), x='month', y='total_amount', 
                  color_discrete_sequence=[COLORS['accent']]), "Monthly Trend")),
        dcc.Graph(figure=apply_layout(px.bar(df.groupby('weekday', observed=True)['total_amount'].sum().reset_index(), x='weekday', y='total_amount', 
                  color_discrete_sequence=[COLORS['secondary']]), "Weekly Velocity")),
    ], style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '20px', 'marginTop': '20px'})
])

# Styling the cards
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>{%metas%}<title>Dashboard</title>{%css%}
        <style>
            .kpi-card { flex: 1; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; border-top: 5px solid #3498DB; }
            .kpi-card p { color: #7F8C8D; font-weight: bold; margin: 0; }
            .kpi-card h2 { color: #2C3E50; margin: 5px 0 0 0; }
        </style>
    </head>
    <body>{%app_entry%}<footer>{%config%}{%scripts%}{%renderer%}</footer></body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)