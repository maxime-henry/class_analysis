import streamlit as st
import pandas as pd

# Function to promote headers
def promote_headers(df):
    if pd.notnull(df.iloc[0]).sum() > 2:
        df.columns = df.iloc[0]
        df = df[1:]
    elif pd.notnull(df.iloc[1]).sum() > 2:
        df.columns = df.iloc[1]
        df = df[2:]
    return df

# Function to standardize columns
def standardize_columns(df, columns_to_keep):
    for col in columns_to_keep:
        if col not in df.columns:
            df[col] = None
    return df[columns_to_keep]

# Function to add custom columns
def add_custom_columns(df):
    # Add PersonalizedSexe column
    df['PersonalizedSexe'] = df['Sexe'].apply(lambda x: 'F' if x == 'F' else 'M')
    
    # Add Status column
    def get_status(stat):
        if pd.isnull(stat):
            return None
        stat_lower = stat.lower()
        if stat_lower.startswith('p'):
            return 'Placé'
        elif stat_lower.startswith('s'):
            return 'Selectionné'
        elif stat_lower.startswith('o') or stat_lower.startswith('i'):
            return 'Placé'
        else:
            return None

    df['Status'] = df['Statut'].apply(get_status)
    return df

# Streamlit app
st.title("Dashboard Data Loader")

# File uploader
source_file = st.file_uploader("Choose the LYON 2024 Répartition classes🚀🎒  .xlsx file", type="xlsx")

if source_file:
    try:
        # Load the source file
        source_data = pd.read_excel(source_file, sheet_name=None)
        
        # Process each sheet
        processed_sheets = []
        columns_to_keep = [ "Nom", "Prénom", "Sexe", "Statut"]
        
        for sheet_name, df in source_data.items():
            if df.iloc[0][0] == "Nom" :
                df = promote_headers(df)
            
            df = standardize_columns(df, columns_to_keep)
            
            df = df[df['Nom'].notnull()]
            df = add_custom_columns(df)
            
            df['SheetName'] = sheet_name
            processed_sheets.append(df)
        
        # Combine all sheets
        combined_data = pd.concat(processed_sheets, ignore_index=True)
        
        # Display the processed data
        st.write("Processed Data:")
        st.dataframe(combined_data)
        



        # Option to download the processed data
        @st.cache_data
        def convert_df(df):
            return df.to_csv(index=False).encode('utf-8')

        csv = convert_df(combined_data)

        st.download_button(
            label="Download Processed Data as CSV",
            data=csv,
            file_name='processed_data.csv',
            mime='text/csv',
        )
        
    except Exception as e:
        st.error(f"An error occurred: {e}")