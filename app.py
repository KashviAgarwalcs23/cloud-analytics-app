import streamlit as st
import pandas as pd
from pymongo import MongoClient
import matplotlib.pyplot as plt

st.title("Cloud Data Analytics App")

client = MongoClient("mongodb+srv://kashviagarwalcs23:<db_password>@cluster0.t3yni.mongodb.net/?appName=Cluster0")
db = client["cloudDB"]
collection = db["dataset"]

file = st.file_uploader("Upload CSV")

if file:
    df = pd.read_csv(file)

    st.write(df.head())

    data = df.to_dict("records")
    collection.insert_many(data)

    st.success("Stored in MongoDB")

    st.write(df.describe())

    column = st.selectbox("Select column", df.columns)

    fig, ax = plt.subplots()
    df[column].hist(ax=ax)

    st.pyplot(fig)