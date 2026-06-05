import streamlit as st


def apply_custom_styles():
    st.markdown("""
    <style>

    .stApp {
        background-color: #F8F5F0;
        color: #374151;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3 {
        color: #1F2937;
        font-weight: 700;
    }

    p, label, li {
        color: #374151;
    }

    [data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E5E0D8;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }

    [data-testid="stMetricValue"] {
        color: #374151;
        font-weight: 700;
    }

    [data-testid="stFileUploader"] {
        background-color: #FFFFFF;
        border: 1px solid #E5E0D8;
        border-radius: 16px;
        padding: 14px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }

    [data-testid="stFileUploader"] section {
        background-color: #F3F4F6 !important;
        border: 2px dashed #C7C2BA !important;
        border-radius: 14px !important;
    }

    [data-testid="stFileUploader"] section button {
        background-color: #FFFFFF !important;
        color: #374151 !important;
        border: 1px solid #D6D3D1 !important;
        border-radius: 10px !important;
    }

    [data-testid="stFileUploader"] section * {
        color: #374151 !important;
    }

    [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] {
        background-color: #F3F4F6 !important;
        color: #374151 !important;
        border: 1px solid #D6D3D1 !important;
        border-radius: 14px !important;
    }

    [data-testid="stFileUploader"] [data-testid="stFileUploaderFile"] * {
        color: #374151 !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #D6D3D1 !important;
        color: #374151 !important;
    }

    div[data-baseweb="tag"] {
        background-color: #D8E2F0 !important;
        color: #2F3A4A !important;
        border-radius: 10px !important;
    }

    div[data-baseweb="tag"] span {
        color: #2F3A4A !important;
    }

    div[data-baseweb="tag"] svg {
        fill: #2F3A4A !important;
    }

    [data-testid="stCheckbox"] svg {
        fill: #7C8DB5 !important;
    }

    [data-testid="stCheckbox"] label span {
        color: #374151 !important;
    }

    [data-testid="stDataFrame"],
    div[data-testid="stPlotlyChart"] {
        background-color: #FFFFFF;
        border: 1px solid #E5E0D8;
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        overflow: visible;
    }

    .stAlert {
        border-radius: 14px;
        border: 1px solid #E5E0D8;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        margin-bottom: 22px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #FAF7F2;
        border: 1px solid #E5E0D8;
        border-radius: 999px;
        color: #4B5563;
        padding: 10px 18px;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background-color: #7C8DB5;
        color: #FFFFFF;
        border-color: #7C8DB5;
    }

    .stTabs [aria-selected="true"] p {
        color: #FFFFFF !important;
    }
                
    /* Uploaded file item after upload */
    [data-testid="stFileUploaderFile"] {
        background-color: #FFFFFF !important;
        border: 1px solid #D6D3D1 !important;
        border-radius: 14px !important;
    }

    [data-testid="stFileUploaderFile"] * {
        color: #374151 !important;
    }

    [data-testid="stFileUploaderFile"] button {
        background-color: #EEF2F7 !important;
        border-radius: 50% !important;
        border: 1px solid #D6D3D1 !important;
    }

    [data-testid="stFileUploaderFile"] svg {
        fill: #374151 !important;
    }
    
    .stButton button {
        background-color: #FFFFFF !important;
        color: #374151 !important;
        border: 1px solid #D6D3D1 !important;
        border-radius: 12px !important;
        padding: 0.6rem 1rem !important;
    }

    .stButton button:hover {
        background-color: #F3F4F6 !important;
        color: #1F2937 !important;
        border: 1px solid #C7C2BA !important;
    }

    </style>
    """, unsafe_allow_html=True)