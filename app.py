import streamlit as st
import pandas as pd

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(page_title="Prawn Feed Dashboard", layout="wide")

# -------------------------------
# Custom Styling (Premium UI)
# -------------------------------
st.markdown("""
    <style>
    .main {
        background-color: #f7f9fc;
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
    }
    .block-container {
        padding-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------------
# Core Logic
# -------------------------------

def calculate_biomass(abw, population):
    return (abw * population) / 1000


def get_feed_percentage(abw):
    if abw <= 1:
        return 12
    elif abw <= 5:
        return 8
    elif abw <= 10:
        return 5
    elif abw <= 20:
        return 3
    elif abw <= 40:
        return 2
    else:
        return 1.5


def calculate_base_feed(biomass, abw):
    return biomass * (get_feed_percentage(abw) / 100)


def adjust_feed(prev_feed, base_feed, consumption, molting):
    if molting:
        return max(base_feed * 0.7, prev_feed * 0.75)

    if consumption == 0:
        return max(base_feed, prev_feed * 1.05)
    elif consumption < 2:
        return max(base_feed * 0.95, prev_feed * 1.02)
    elif consumption < 5:
        return max(base_feed * 0.9, prev_feed * 0.95)
    elif consumption < 10:
        return max(base_feed * 0.75, prev_feed * 0.85)
    else:
        return max(base_feed * 0.6, prev_feed * 0.7)


def distribute_feed(total_feed):
    return {
        "🌅 Morning": round(total_feed * 0.225, 2),
        "🌞 Noon": round(total_feed * 0.275, 2),
        "🌆 Evening": round(total_feed * 0.265, 2),
        "🌙 Night": round(total_feed * 0.235, 2),
    }

# -------------------------------
# Session State
# -------------------------------
if "data" not in st.session_state:
    st.session_state.data = []

# -------------------------------
# Sidebar (Cleaner)
# -------------------------------
st.sidebar.title("Farm Setup")

pond_area = st.sidebar.number_input("Pond Area (sq.m)", min_value=100.0, value=100000.0)
population = st.sidebar.number_input("Total Population", min_value=1000, value=50000)

st.sidebar.markdown("---")
st.sidebar.title("📅 Daily Entry")

abw = st.sidebar.number_input("Average Body Weight (g)", min_value=0.1, value=10.0)
consumption = st.sidebar.slider("Leftover Feed (%)", 0, 100)
molting = st.sidebar.checkbox("Molting Phase")

# -------------------------------
# Header
# -------------------------------
st.title("🍤 Prawn Feed Optimization Dashboard")
st.caption("Smart feeding system for efficient aquaculture management")

# -------------------------------
# Calculate Button
# -------------------------------
if st.button("🚀 Calculate Feed"):

    biomass = calculate_biomass(abw, population)
    base_feed = calculate_base_feed(biomass, abw)

    if len(st.session_state.data) == 0:
        final_feed = base_feed
    else:
        prev_feed = st.session_state.data[-1]["Feed"]
        final_feed = adjust_feed(prev_feed, base_feed, consumption, molting)

    final_feed = max(final_feed, base_feed * 0.5)

    distribution = distribute_feed(final_feed)

    day = len(st.session_state.data) + 1

    st.session_state.data.append({
        "Day": day,
        "ABW": abw,
        "Feed": round(final_feed, 2),
        "Consumption": consumption
    })

    # -------------------------------
    # KPI Cards
    # -------------------------------
    col1, col2, col3 = st.columns(3)

    col1.metric("📊 Daily Feed (kg)", round(final_feed, 2))
    col2.metric("⚖️ Biomass (kg)", round(biomass, 2))
    col3.metric("📈 Feed %", get_feed_percentage(abw))

    st.markdown("---")

    # -------------------------------
    # Distribution
    # -------------------------------
    st.subheader("🍽️ Feeding Schedule")
    cols = st.columns(4)

    for i, (k, v) in enumerate(distribution.items()):
        cols[i].metric(k, f"{v} kg")

    st.markdown("---")

    # -------------------------------
    # Alerts
    # -------------------------------
    if consumption > 10:
        st.warning("⚠️ Overfeeding detected! Reduce feed.")
    if molting:
        st.warning("⚠️ Molting phase → feed reduced.")
    if abw > 40:
        st.info("ℹ️ Large prawns → lower feeding applied.")

    # -------------------------------
    # Debug Panel
    # -------------------------------
    with st.expander("🔍 Technical Details"):
        st.write("ABW:", abw)
        st.write("Biomass:", biomass)
        st.write("Base Feed:", base_feed)

# -------------------------------
# History Table
# -------------------------------
if len(st.session_state.data) > 0:

    st.markdown("## 📋 Feeding History")

    df = pd.DataFrame(st.session_state.data)
    st.dataframe(df, use_container_width=True)

    # Summary
    st.markdown("## 📊 Summary")

    total_feed = df["Feed"].sum()
    avg_feed = df["Feed"].mean()

    col1, col2 = st.columns(2)
    col1.metric("Total Feed Used", f"{round(total_feed,2)} kg")
    col2.metric("Average Feed / Day", f"{round(avg_feed,2)} kg")