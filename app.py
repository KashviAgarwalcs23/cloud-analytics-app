import streamlit as st
import pandas as pd
from pymongo import MongoClient
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
import ssl
import certifi

st.set_page_config(layout="wide")
st.title("📊 Cloud Data Analytics App")

# Use environment variable for MongoDB URI
mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    mongo_uri = "mongodb+srv://kashviagarwalcs23:<db_password>@cluster0.t3yni.mongodb.net/?appName=Cluster0&tlsCAFile=/etc/ssl/certs/ca-certificates.crt"

# Initialize MongoDB connection with proper SSL settings
@st.cache_resource
def init_mongo_connection():
    try:
        client = MongoClient(
            mongo_uri,
            tlsCAFile=certifi.where(),  # Use certifi's CA bundle
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            retryWrites=False
        )
        # Test connection
        client.admin.command('ping')
        return client
    except Exception as e:
        st.error(f"❌ Failed to connect to MongoDB: {str(e)}")
        return None

client = init_mongo_connection()

if client:
    db = client["cloudDB"]
    collection = db["dataset"]
    mongo_available = True
else:
    mongo_available = False

file = st.file_uploader("📁 Upload CSV File", type="csv")

if file:
    df = pd.read_csv(file)
    
    # Store in MongoDB (non-blocking)
    if mongo_available:
        try:
            data = df.to_dict("records")
            collection.insert_many(data)
            st.success("✅ Data Successfully Stored in MongoDB")
        except Exception as e:
            st.warning(f"⚠️ MongoDB connection issue: Data visualizations work, but MongoDB storage failed. {str(e)[:100]}")
    else:
        st.info("ℹ️ MongoDB not available - data will be visualized but not stored")

    # Display tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Data", "📈 Statistics", "📊 Interactive Charts", "🔥 Heatmap", "🎯 Distribution"])
    
    # Tab 1: Data View
    with tab1:
        st.subheader("Dataset Preview")
        st.write(df.head(10))
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Rows", len(df))
        col2.metric("Total Columns", len(df.columns))
        col3.metric("Missing Values", df.isnull().sum().sum())
    
    # Tab 2: Statistics
    with tab2:
        st.subheader("Statistical Summary")
        st.write(df.describe())
        st.subheader("Data Types")
        st.write(df.dtypes)
        st.subheader("Missing Values Per Column")
        st.write(df.isnull().sum())
    
    # Tab 3: Interactive Charts
    with tab3:
        st.subheader("Interactive Visualizations")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        chart_type = st.selectbox("Select Chart Type", ["Bar Chart", "Line Chart", "Scatter Plot", "Box Plot"])
        
        if numeric_cols:
            if chart_type == "Bar Chart":
                col = st.selectbox("Select Column for Bar Chart", numeric_cols)
                fig = px.bar(df, y=col, title=f"Bar Chart - {col}", color=col)
                st.plotly_chart(fig, use_container_width=True)
            
            elif chart_type == "Line Chart":
                col = st.selectbox("Select Column for Line Chart", numeric_cols)
                fig = px.line(df, y=col, title=f"Line Chart - {col}", markers=True)
                st.plotly_chart(fig, use_container_width=True)
            
            elif chart_type == "Scatter Plot":
                if len(numeric_cols) >= 2:
                    col1 = st.selectbox("Select X-axis", numeric_cols)
                    col2 = st.selectbox("Select Y-axis", numeric_cols, index=1 if len(numeric_cols) > 1 else 0)
                    fig = px.scatter(df, x=col1, y=col2, title=f"Scatter Plot: {col1} vs {col2}", trendline="ols")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Need at least 2 numeric columns for scatter plot")
            
            elif chart_type == "Box Plot":
                col = st.selectbox("Select Column for Box Plot", numeric_cols)
                fig = px.box(df, y=col, title=f"Box Plot - {col}")
                st.plotly_chart(fig, use_container_width=True)
    
    # Tab 4: Correlation Heatmap
    with tab4:
        st.subheader("Correlation Matrix Heatmap")
        numeric_df = df.select_dtypes(include=[np.number])
        if len(numeric_df.columns) > 1:
            corr_matrix = numeric_df.corr()
            fig = go.Figure(data=go.Heatmap(z=corr_matrix.values, 
                                           x=corr_matrix.columns, 
                                           y=corr_matrix.columns, 
                                           colorscale="RdBu",
                                           zmid=0))
            fig.update_layout(height=600, width=600)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Need at least 2 numeric columns for correlation heatmap")
    
    # Tab 5: Distribution Analysis
    with tab5:
        st.subheader("Distribution Plots")
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            selected_cols = st.multiselect("Select Columns to Analyze", numeric_cols, default=[numeric_cols[0]])
            for col in selected_cols:
                fig = px.histogram(df, x=col, nbins=30, title=f"Distribution - {col}", opacity=0.8)
                st.plotly_chart(fig, use_container_width=True)
