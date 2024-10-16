#=======================================================================
## 0. Importing libraries and setting up Streamlit web app

# Importing the necessary packages
import streamlit as st
import openpyxl
import pygwalker as pyg
import pandas as pd

# Setting up web app page
st.set_page_config(page_title='Exploratory Data Analysis App', page_icon=None, layout="wide")

# Creating section in sidebar
st.sidebar.write("****A) File upload****")

# User prompt to select file type
ft = st.sidebar.selectbox("*What is the file type?*", ["Excel", "csv"])

# Creating dynamic file upload option in sidebar
uploaded_file = st.sidebar.file_uploader("*Upload file here*")

if uploaded_file is not None:

    if ft == 'Excel':
        try:
            # User prompt to select sheet name in uploaded Excel
            excel_file = pd.ExcelFile(uploaded_file)
            sh = st.sidebar.selectbox("*Which sheet name in the file should be read?*", excel_file.sheet_names)
            # User prompt to define row with column names if they aren't in the header row in the uploaded Excel
            h = st.sidebar.number_input("*Which row contains the column names?*", 0, 100, value=0)
        except Exception as e:
            st.error(f"Error reading the Excel file: {e}")
            st.stop()
    
    elif ft == 'csv':
        # No need for sheet name and header row for CSV, set them to None
        sh = None
        h = None

    # Caching function to load data
    @st.cache_data
    def load_data(file, file_type, sheet=None, header_row=None):
        if file_type == 'Excel':
            try:
                # Reading the excel file
                data = pd.read_excel(file, header=header_row, sheet_name=sheet, engine='openpyxl')
            except Exception as e:
                st.error(f"Error reading the Excel file: {e}")
                st.stop()
    
        elif file_type == 'csv':
            try:
                # Reading the csv file
                data = pd.read_csv(file)
            except Exception as e:
                st.error(f"Error reading the CSV file: {e}")
                st.stop()
        
        return data

    data = load_data(uploaded_file, ft, sh, h)

#=====================================================================================================
## 1. Overview of the data
    st.write('### 1. Dataset Preview')

    try:
        # View the dataframe in Streamlit
        st.dataframe(data, use_container_width=True)

    except Exception as e:
        st.error(f"Error displaying the data: {e}")
        st.stop()

#=====================================================================================================
## 2. Understanding the data
    st.write('### 2. High-Level Overview')

    # Creating radio button and sidebar simultaneously
    selected = st.sidebar.radio("**B) What would you like to know about the data?**", 
                                ["Data Dimensions",
                                 "Field Descriptions",
                                 "Summary Statistics", 
                                 "Value Counts of Fields"])

    # Showing field types
    if selected == 'Field Descriptions':
        fd = data.dtypes.reset_index().rename(columns={'index': 'Field Name', 0: 'Field Type'}).sort_values(by='Field Type', ascending=False).reset_index(drop=True)
        st.dataframe(fd, use_container_width=True)

    # Showing summary statistics
    elif selected == 'Summary Statistics':
        ss = pd.DataFrame(data.describe(include='all').round(2).fillna(''))
        st.dataframe(ss, use_container_width=True)

    # Showing value counts of object fields
    elif selected == 'Value Counts of Fields':
        # Creating radio button and sidebar simultaneously if this main selection is made
        sub_selected = st.sidebar.radio("*Which field should be investigated?*", data.select_dtypes('object').columns)
        vc = data[sub_selected].value_counts(dropna=False).reset_index().rename(columns={sub_selected: 'Value', 'index': 'Count'}).reset_index(drop=True)
        st.dataframe(vc, use_container_width=True)

    # Showing the shape of the dataframe
    else:
        st.write('###### The data has the dimensions :', data.shape)

#=====================================================================================================
## 3. Visualisation

    # Selecting whether visualisation is required
    vis_select = st.sidebar.checkbox("**C) Is visualisation required for this dataset?**")

    if vis_select:
        st.write('### 3. Visual Insights')

        # Creating a PyGWalker Dashboard
        walker = pyg.walk(data, return_html=True)
        st.components.v1.html(walker, width=1100, height=800)  # Adjust width and height as needed
