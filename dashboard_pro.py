# === DASHBOARD PRO: Real Estate E-commerce ===
import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Load data
@st.cache_data
def load_data():
    df = pd.read_csv("Combined_RealEstate.csv", low_memory=False)
    return df

df = load_data()

# 2. Copy & Clean
df_clean = df.copy()

# Ép kiểu numeric cho Price, Area
for col in ["Price", "Area", "Price.1", "Area.1"]:
    if col in df_clean.columns:
        df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

# Tính Price_per_m2 nếu chưa có
if "Price_per_m2" not in df_clean.columns:
    df_clean["Price_per_m2"] = df_clean["Price"] / df_clean["Area"]

# Xử lý NaN cơ bản (chỉ trên bản clean)
df_clean = df_clean.dropna(subset=["Price_per_m2", "District", "Property_Type"])

# 3. Sidebar filter
st.sidebar.header("🔍 Bộ lọc dữ liệu")

districts = st.sidebar.multiselect(
    "Chọn Quận/Huyện",
    options=sorted(df_clean["District"].dropna().unique()),
    default=None
)

property_types = st.sidebar.multiselect(
    "Chọn loại BĐS",
    options=sorted(df_clean["Property_Type"].dropna().unique()),
    default=None
)

# Apply filter
filtered_df = df_clean.copy()
if districts:
    filtered_df = filtered_df[filtered_df["District"].isin(districts)]
if property_types:
    filtered_df = filtered_df[filtered_df["Property_Type"].isin(property_types)]

# 4. KPI Cards
st.title("🏠 Dashboard Bất động sản - E-commerce")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Số lượng tin", f"{len(filtered_df):,}")
col2.metric("Giá TB (triệu/m²)", f"{filtered_df['Price_per_m2'].mean():,.0f}")
col3.metric("Giá cao nhất (triệu/m²)", f"{filtered_df['Price_per_m2'].max():,.0f}")
col4.metric("Giá thấp nhất (triệu/m²)", f"{filtered_df['Price_per_m2'].min():,.0f}")

# 5. Biểu đồ interactive
st.subheader("📊 Giá trung bình theo Quận")
fig1 = px.bar(
    filtered_df.groupby("District")["Price_per_m2"].mean().reset_index(),
    x="District", y="Price_per_m2", title="Giá TB theo Quận",
    color="Price_per_m2", color_continuous_scale="Viridis"
)
st.plotly_chart(fig1, use_container_width=True)

st.subheader("📈 Phân bố giá BĐS")
fig2 = px.histogram(
    filtered_df, x="Price_per_m2", nbins=50,
    title="Histogram giá trên m²", marginal="box"
)
st.plotly_chart(fig2, use_container_width=True)

st.subheader("🏷 Giá theo loại BĐS")
fig3 = px.box(
    filtered_df, x="Property_Type", y="Price_per_m2",
    title="So sánh giá theo loại BĐS"
)
st.plotly_chart(fig3, use_container_width=True)

# 6. Xuất dữ liệu CSV sau khi lọc
st.subheader("📥 Tải dữ liệu đã lọc")
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Tải CSV",
    data=csv,
    file_name="real_estate_filtered.csv",
    mime="text/csv",
)
