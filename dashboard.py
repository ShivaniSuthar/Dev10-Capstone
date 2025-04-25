import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots
from sqlalchemy import create_engine


st.set_page_config(
    page_title="Credit Card Fraud Analysis",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)


def create_card(content):
    st.markdown(f'<div class="card">{content}</div>', unsafe_allow_html=True)


st.title("Credit/Debit Card Fraud Analysis")
st.markdown("""
### Overview
            
This dashboard provides insights into credit card transaction patterns and fraud detection.
Use the filters in sidebar to explore different aspects of the data to identify potential fraud patterns.
""")

st.sidebar.header("Filters")


@st.cache_data
def load_data():
    username = "root"
    password = "mysqlpassword"
    host = "localhost"
    port = "3306"
    database = "fraud_project"

    connection_string = (
        f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
    )
    engine = create_engine(connection_string)

    query = "SELECT * FROM fraud_analysis_table"
    df = pd.read_sql(query, engine)

    df["date"] = pd.to_datetime(df["date"])

    return df


try:
    df = load_data()
    st.sidebar.success("Data loaded!")
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()


min_date = df["date"].min().date()
max_date = df["date"].max().date()

st.sidebar.markdown("### Time Range")
date_range = st.sidebar.date_input(
    "Select date range", [min_date, max_date], min_value=min_date, max_value=max_date
)

if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = df[
        (df["date"].dt.date >= start_date) & (df["date"].dt.date <= end_date)
    ]
else:
    filtered_df = df

st.sidebar.markdown("### Transaction Filters")
min_amount = float(df["amount"].min())
max_amount = float(df["amount"].max())

amount_range = st.sidebar.slider(
    "Transaction amount range ($)", min_amount, max_amount, (min_amount, max_amount)
)

filtered_df = filtered_df[
    (filtered_df["amount"] >= amount_range[0])
    & (filtered_df["amount"] <= amount_range[1])
]

card_brands = ["All"] + sorted(df["card_brand"].unique().tolist())
brand_selected = st.sidebar.selectbox("Card Brand", card_brands)

if brand_selected != "All":
    filtered_df = filtered_df[filtered_df["card_brand"] == brand_selected]

st.header("Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_transactions = len(filtered_df)
    st.metric("Total Transactions", f"{total_transactions:,}")

with col2:
    fraud_count = filtered_df["is_fraud"].sum()
    st.metric("Fraudulent Transactions", f"{fraud_count:,}")

with col3:
    fraud_rate = (
        (fraud_count / total_transactions) * 100 if total_transactions > 0 else 0
    )
    st.metric("Fraud Rate", f"{fraud_rate:.2f}%")

with col4:
    avg_amount = filtered_df["amount"].mean()
    st.metric("Average Amount", f"${avg_amount:.2f}")

fig1 = go.Figure()

fig1.add_trace(
    go.Histogram(
        x=filtered_df[filtered_df["is_fraud"] == 0]["amount"],
        name="Legitimate",
        opacity=0.75,
        marker=dict(color="green"),
        xbins=dict(start=0, end=max(500, filtered_df["amount"].max()), size=20),
    )
)

fig1.add_trace(
    go.Histogram(
        x=filtered_df[filtered_df["is_fraud"] == 1]["amount"],
        name="Fradulent",
        opacity=0.75,
        marker=dict(color="red"),
        xbins=dict(start=0, end=max(500, filtered_df["amount"].max()), size=20),
    )
)

fig1.update_layout(
    xaxis_title="Transaction Amount ($)",
    yaxis_title="Count",
    barmode="overlay",
    height=400,
    template="plotly_white",
)

st.plotly_chart(fig1, use_container_width=True)

st.header("Geographic Analysis")

map_col1, map_col2 = st.columns([3, 1])

state_data = (
    filtered_df.groupby("merchant_state")["is_fraud"]
    .agg(["mean", "count"])
    .reset_index()
)
state_data.columns = ["State", "Fraud Rate", "Transaction Count"]
state_data["Fraud Rate"] = state_data["Fraud Rate"] * 100

state_abbrev = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
    "DC": "District of Columbia",
}

state_data["State Name"] = state_data["State"].map(state_abbrev)

fig_map = px.choropleth(
    state_data,
    locations="State",
    locationmode="USA-states",
    color="Fraud Rate",
    hover_name="State Name",
    hover_data=["Transaction Count", "Fraud Rate"],
    color_continuous_scale="Reds",
    scope="usa",
    labels={"Fraud Rate": "Fraud Rate (%)"},
)

fig_map.update_layout(
    geo=dict(showlakes=True, lakecolor="rgb(255, 255, 255)", bgcolor="rgba(0,0,0,0)"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    height=600,
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    coloraxis_colorbar=dict(
        title="Fraud Rate (%)",
        thicknessmode="pixels",
        thickness=20,
        lenmode="pixels",
        len=400,
        yanchor="top",
        y=1,
        xanchor="left",
        x=0,
    ),
)


st.plotly_chart(fig_map, use_container_width=True)

fraud_col, volume_col = st.columns(2)

with fraud_col:
    st.subheader("Top Fraud States")
    top_fraud_states = state_data.sort_values("Fraud Rate", ascending=False).head(5)

    for i, row in top_fraud_states.iterrows():
        st.metric(
            row["State Name"],
            f"{row['Fraud Rate']:.2f}%",
        )

with volume_col:
    st.subheader("Highest Volume")
    top_volume_states = state_data.sort_values(
        "Transaction Count", ascending=False
    ).head(5)

    for i, row in top_volume_states.iterrows():
        st.metric(
            row["State Name"],
            f"{row['Transaction Count']} transactions",
        )


def sample_dataframe(df, sample_size=0.1, random_state=42):
    fraud_df = df[df["is_fraud"] == 1]
    non_fraud_df = df[df["is_fraud"] == 0]

    if len(fraud_df) > 100:
        sampled_fraud = fraud_df.sample(frac=sample_size, random_state=random_state)
    else:
        sampled_fraud = fraud_df

    sampled_non_fraud = non_fraud_df.sample(frac=sample_size, random_state=random_state)

    sampled_df = pd.concat([sampled_fraud, sampled_non_fraud])
    return sampled_df.sample(frac=1, random_state=random_state).reset_index(drop=True)


st.header("Additional Fraud Analysis")

sample_size = 0.1
orig_len = len(filtered_df)
filtered_df = sample_dataframe(filtered_df, sample_size=sample_size)

st.info(
    f"Using {sample_size * 100:.0f}% sample ({len(filtered_df):,} of {orig_len} transactions) for complex visualizations to improve performance."
)

st.subheader("Transaction Patterns by Hour and Day")
st.markdown("""
This heatmap visualization shows how transaction patterns vary throughout the week and by hour of day. 
Use the tabs below to toggle between transaction volume and fraud rate views. 
From these heatmaps, we can:
- Identify peak transaction hours and days
- Spot time periods with higher fraud risk
- Detect anomalous patterns that may indicate suspicious activity
""")

heatmap_count = filtered_df.pivot_table(
    index="hour_of_day", columns="day_of_week", values="transaction_id", aggfunc="count"
).fillna(0)

heatmap_fraud = (
    filtered_df.pivot_table(
        index="hour_of_day", columns="day_of_week", values="is_fraud", aggfunc="mean"
    ).fillna(0)
    * 100
)

# Map day numbers to names
day_names = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat", 7: "Sun"}
heatmap_count.columns = [day_names.get(day, day) for day in heatmap_count.columns]
heatmap_fraud.columns = [day_names.get(day, day) for day in heatmap_fraud.columns]

# Create tabs for different heatmaps
tab1, tab2 = st.tabs(["Transaction Volume", "Fraud Rate"])

with tab1:
    # Volume heatmap
    fig_heatmap1 = px.imshow(
        heatmap_count,
        labels=dict(x="Day of Week", y="Hour of Day", color="Transaction Count"),
        x=heatmap_count.columns,
        y=heatmap_count.index,
        color_continuous_scale="Blues",
        aspect="auto",
    )

    fig_heatmap1.update_layout(
        height=500,
        xaxis_title="Day of Week",
        yaxis_title="Hour of Day",
        coloraxis_colorbar=dict(title="Transaction Count"),
        template="plotly_white",
    )

    st.plotly_chart(fig_heatmap1, use_container_width=True)

    st.markdown("""
    **Transaction Volume:**
    - Darker blue indicates higher transaction volume
    - Look for patterns in customer activity throughout the day
    - Compare weekday vs. weekend transaction patterns
    - Identify your busiest hours for resource planning
    """)

with tab2:
    # Fraud rate heatmap
    fig_heatmap2 = px.imshow(
        heatmap_fraud,
        labels=dict(x="Day of Week", y="Hour of Day", color="Fraud Rate (%)"),
        x=heatmap_fraud.columns,
        y=heatmap_fraud.index,
        color_continuous_scale="Reds",
        aspect="auto",
    )

    fig_heatmap2.update_layout(
        height=500,
        xaxis_title="Day of Week",
        yaxis_title="Hour of Day",
        coloraxis_colorbar=dict(title="Fraud Rate (%)"),
        template="plotly_white",
    )

    st.plotly_chart(fig_heatmap2, use_container_width=True)

    st.markdown("""
    **Fraud Rate Insights:**
    - Darker red indicates higher fraud rates
    - Fraud occurs most on Mondays
    - Early afternoon hours often show elevated fraud risk
    - Compare fraud patterns against normal transaction volume
    - Identify time periods that might need enhanced monitoring
    """)

st.subheader("Multi-Dimensional Fraud Pattern Analysis")
st.markdown("""
This parallel coordinates plot allows you to explore relationships between multiple transaction attributes simultaneously. 
Each line represents a transaction, with blue lines showing legitimate transactions and red lines showing fraudulent ones.
If we observe where the red lines cluster, we can identify combinations of factors associated with higher fraud risk.
""")

dimensions = ["amount", "hour_of_day", "day_of_week", "is_fraud"]
dims = []

for dim in dimensions:
    if dim == "is_fraud":
        dims.append(
            dict(
                range=[0, 1],
                label="Fraud Status",
                values=filtered_df[dim],
                tickvals=[0, 1],
                ticktext=["Legitimate", "Fraudulent"],
            )
        )
    else:
        dims.append(
            dict(
                range=[filtered_df[dim].min(), filtered_df[dim].max()],
                label=dim.replace("_", " ").title(),
                values=filtered_df[dim],
            )
        )

fig_parallel = go.Figure(
    data=go.Parcoords(
        line=dict(
            color=filtered_df["is_fraud"],
            colorscale=[[0, "blue"], [1, "red"]],
            showscale=True,
            colorbar=dict(
                title="Fraud Status",
                tickvals=[0, 1],
                ticktext=["Legitimate", "Fraudulent"],
            ),
        ),
        dimensions=dims,
    )
)

fig_parallel.update_layout(height=500, margin=dict(l=80, r=80, t=60, b=30))

st.plotly_chart(fig_parallel, use_container_width=True)

st.markdown("""
**How to interpret this visualization:**
- Each vertical axis represents a different transaction attribute
- Each line represents an individual transaction
- Red lines are fraudulent transactions, blue lines are legitimate
- Look for patterns where the red lines converge
- You can click and drag along any axis to filter transactions
""")

st.subheader("User Demographics and Fraud")
st.markdown("""
This bubble chart visualizes the relationship between customer age, credit score, and fraud risk.
Each bubble represents a demographic group, with color indicating fraud rate and size showing transaction volume.
""")

demo_stats = (
    filtered_df.groupby(["current_age", "gender"])
    .agg({"transaction_id": "count", "is_fraud": "mean", "credit_score": "mean"})
    .reset_index()
)

demo_stats["Fraud Rate"] = demo_stats["is_fraud"] * 100

fig_demo = px.scatter(
    demo_stats,
    x="current_age",
    y="credit_score",
    size="transaction_id",
    color="Fraud Rate",
    color_continuous_scale="Reds",
    hover_name="gender",
    size_max=50,
    labels={
        "current_age": "Age",
        "credit_score": "Credit Score",
        "transaction_id": "Transaction Count",
        "Fraud Rate": "Fraud Rate (%)",
    },
)

fig_demo.update_layout(
    height=500,
    xaxis_title="Age",
    yaxis_title="Credit Score",
    coloraxis_colorbar=dict(title="Fraud Rate (%)"),
    template="plotly_white",
)

st.plotly_chart(fig_demo, use_container_width=True)

st.markdown("""
**How to interpret this visualization:**
- Each bubble represents a demographic group (age + gender)
- The x-axis shows customer age
- The y-axis shows average credit score
- Bubble size indicates transaction volume
- Color intensity (red) indicates fraud rate
- Fraud rates are more varied for older clients
""")

st.subheader("Financial Profile and Fraud Risk")

st.markdown("""
This heatmap shows how income and debt levels relate to fraud vulnerability.
Deeper red indicates higher fraud rates for that income-debt combination.
""")

income_bins = [0, 30000, 60000, 90000, 120000, float("inf")]
income_labels = ["<30K", "30K-60K", "60K-90K", "90K-120K", ">120K"]

debt_bins = [0, 10000, 25000, 50000, 100000, float("inf")]
debt_labels = ["<10K", "10K-25K", "25K-50K", "50K-100K", ">100K"]

financial_df = filtered_df.copy()
financial_df["income_group"] = pd.cut(
    financial_df["yearly_income"], bins=income_bins, labels=income_labels
)
financial_df["debt_group"] = pd.cut(
    financial_df["total_debt"], bins=debt_bins, labels=debt_labels
)

fin_heatmap = (
    financial_df.pivot_table(
        index="income_group", columns="debt_group", values="is_fraud", aggfunc="mean"
    ).fillna(0)
    * 100
)

fig_fin = px.imshow(
    fin_heatmap,
    labels=dict(x="Total Debt", y="Yearly Income", color="Fraud Rate (%)"),
    x=fin_heatmap.columns,
    y=fin_heatmap.index,
    color_continuous_scale="Reds",
    aspect="auto",
)

fig_fin.update_layout(
    height=500,
    xaxis_title="Total Debt",
    yaxis_title="Yearly Income",
    coloraxis_colorbar=dict(title="Fraud Rate (%)"),
    template="plotly_white",
)

st.plotly_chart(fig_fin, use_container_width=True)

st.markdown("""
**Key insight:** Credit/debit card fraud tends to target lower-income clients, but varies across levels of debt.        
""")

st.subheader("Fraud Evolution by Transaction Method")

st.markdown("""
This visualization shows how fraud rates vary by transaction method across different hours of the day.
Understanding these patterns can help identify when specific transaction methods are most vulnerable to fraud.
""")

hourly_method = (
    filtered_df.groupby(["hour_of_day", "use_chip"])
    .agg({"transaction_id": "count", "is_fraud": "mean", "amount": "mean"})
    .reset_index()
)

hourly_method["Fraud Rate"] = hourly_method["is_fraud"] * 100

fig_method = px.scatter(
    hourly_method,
    x="hour_of_day",
    y="Fraud Rate",
    size="transaction_id",
    color="use_chip",
    animation_frame="hour_of_day",
    range_x=[0, 23],
    range_y=[0, hourly_method["Fraud Rate"].max() * 1.2],
    labels={
        "hour_of_day": "Hour of Day",
        "Fraud Rate": "Fraud Rate (%)",
        "transaction_id": "Transaction Count",
        "use_chip": "Transaction Method",
    },
    size_max=50,
)

fig_method.update_layout(
    height=500,
    xaxis_title="Hour of Day",
    yaxis_title="Fraud Rate (%)",
    template="plotly_white",
)

st.plotly_chart(fig_method, use_container_width=True)

st.subheader("Credit Limit Utilization and Fraud Risk")

st.markdown("""
This visualization explores the relationship between transaction amount relative to available credit limit and fraud risk.
The chart shows both transaction volume (blue bars) and fraud rates (red line) across different utilization ratio ranges.
""")

ratio_df = filtered_df.copy()
ratio_df["utilization_ratio"] = (ratio_df["amount"] / ratio_df["credit_limit"]) * 100
ratio_df["ratio_group"] = pd.cut(
    ratio_df["utilization_ratio"],
    bins=[0, 1, 5, 10, 25, 50, 100, float("inf")],
    labels=["0-1%", "1-5%", "5-10%", "10-25%", "25-50%", "50-100%", ">100%"],
)

ratio_stats = (
    ratio_df.groupby("ratio_group")
    .agg({"transaction_id": "count", "is_fraud": ["sum", "mean"]})
    .reset_index()
)

ratio_stats.columns = [
    "Utilization Ratio",
    "Transaction Count",
    "Fraud Count",
    "Fraud Rate",
]
ratio_stats["Fraud Rate"] = ratio_stats["Fraud Rate"] * 100

fig_ratio = make_subplots(specs=[[{"secondary_y": True}]])

fig_ratio.add_trace(
    go.Bar(
        x=ratio_stats["Utilization Ratio"],
        y=ratio_stats["Transaction Count"],
        name="Transaction Count",
        marker_color="lightblue",
    ),
    secondary_y=False,
)

fig_ratio.add_trace(
    go.Scatter(
        x=ratio_stats["Utilization Ratio"],
        y=ratio_stats["Fraud Rate"],
        name="Fraud Rate",
        mode="lines+markers",
        marker=dict(color="red", size=10),
        line=dict(color="red", width=2),
    ),
    secondary_y=True,
)

fig_ratio.update_layout(
    height=500,
    template="plotly_white",
    title="Transaction Amount to Credit Limit Ratio",
    legend=dict(orientation="h", y=1.1),
)

fig_ratio.update_yaxes(title_text="Transaction Count", secondary_y=False)
fig_ratio.update_yaxes(title_text="Fraud Rate (%)", secondary_y=True)
fig_ratio.update_xaxes(title_text="Transaction to Credit Limit Ratio")

st.plotly_chart(fig_ratio, use_container_width=True)

st.markdown("""
**Understanding Credit Limit Utilization and Fraud:**

This visualization reveals important patterns about how fraudsters exploit credit limits:
- **Utilization Ratio Definition**: The utilization ratio represents what percentage of a customer's total credit limit is being used in a single transaction.
- **Normal vs. Suspicious Patterns**: Most legitimate transactions use a small percentage of available credit (typically under 25%), while transactions approaching or exceeding credit limits may indicate card testing or fraud.
- **Risk Assessment**: Transactions with unusually high utilization ratios should receive heightened scrutiny.
- **Customer Segmentation**: Different customer segments may have different "normal" utilization patterns, so fraud detection should be calibrated accordingly.

This analysis helps balance fraud prevention with customer experience by focusing enhanced security measures on genuinely high-risk transactions.
""")

st.subheader("Age to Retirement Age Gap and Fraud Risk")

st.markdown("""
This visualization examines how vulnerability to fraud relates to a customer's proximity to retirement age.
The chart compares fraud rates across different life stages, segmented by gender, to identify demographic patterns.
""")

retirement_df = filtered_df.copy()
retirement_df["years_to_retirement"] = (
    retirement_df["retirement_age"] - retirement_df["current_age"]
)
retirement_df["retirement_group"] = pd.cut(
    retirement_df["years_to_retirement"],
    bins=[-1, 5, 10, 20, 30, 40, float("inf")],
    labels=[
        "<5 years",
        "5-10 years",
        "10-20 years",
        "20-30 years",
        "30-40 years",
        ">40 years",
    ],
)

retirement_stats = (
    retirement_df.groupby(["retirement_group", "gender"])
    .agg({"transaction_id": "count", "is_fraud": "mean", "amount": "mean"})
    .reset_index()
)

retirement_stats["Fraud Rate"] = retirement_stats["is_fraud"] * 100

fig_retirement = px.bar(
    retirement_stats,
    x="retirement_group",
    y="Fraud Rate",
    color="gender",
    barmode="group",
    text_auto=".2f",
    labels={"retirement_group": "Years to Retirement", "Fraud Rate": "Fraud Rate (%)"},
)

fig_retirement.update_layout(
    height=500,
    template="plotly_white",
    xaxis_title="Years to Retirement",
    yaxis_title="Fraud Rate (%)",
)

st.plotly_chart(fig_retirement, use_container_width=True)

st.markdown("""
**Understanding Age to Retirement Patterns and Fraud Risk:**

- **Life Stage Vulnerability**: The chart reveals how fraud risk varies based on how many years a customer is from their expected retirement age.

- **Demographic Targeting**: The gender breakdown helps identify if fraudsters are targeting specific demographic groups differently, which may indicate specialized fraud schemes.

- **Financial Life Cycle Context**: People at different distances from retirement typically have different financial behaviors, assets, and concerns:
  - Those near retirement often have larger savings and may be making significant financial decisions
  - Middle-career individuals may have established credit histories and higher income
  - Early-career customers might have less financial experience and different spending patterns, as evidenced in females further from retirement being most susceptible to fraud
""")