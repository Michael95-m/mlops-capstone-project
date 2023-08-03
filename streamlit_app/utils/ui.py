import streamlit as st
import streamlit.components.v1 as components

def set_page_container_style():
    margins_css = """
    <style>
        /* Configuration of paddings of containers inside main area */
        .main > div {
            max-width: 100%;
            padding-left: 10%;
        }

        /*Font size in tabs */
        button[data-baseweb="tab"] div p {
            font-size: 18px;
            font-weight: bold;
        }
    </style>
    """
    st.markdown(margins_css, unsafe_allow_html=True)

def display_sidebar_header():

    with st.sidebar:
        col1, col2 = st.columns(2)
        repo_link = '#'
        evidently_docs = 'https://docs.evidentlyai.com/'
        col1.markdown(
            f"<a style='display: block; text-align: center;' href={repo_link}>Source code</a>",
            unsafe_allow_html=True,
        )
        col2.markdown(
            f"<a style='display: block; text-align: center;' href={evidently_docs}>Evidently docs</a>",
            unsafe_allow_html=True,
        )
        st.header('')

def display_header(report_name, window_size):
    """Display report header.

    Args:
        report_name (Text): Report name.
        window_size (int): Size of prediction data on which report built.
    """

    st.header(f'Report: {report_name}')
    st.caption(f'Window size: {window_size}')

@st.cache_data
def display_report(report):
    """Display report.

    Args:
        report (Text): Report content.

    Returns:
        Text: Report content.
    """

    components.html(report, width=1000, height=700, scrolling=True)

    return report

