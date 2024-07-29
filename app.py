import streamlit as st
import pandas as pd
import plotly.express as px 


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
st.title("Dashboard ")

# File uploader
source_file = st.file_uploader("Selectionne le fichier LYON 2024 Répartition classes🚀🎒  .xlsx ", type="xlsx")

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
        
        # # Display the processed data
        # st.write("Données :")
        # st.dataframe(combined_data)
        
# Calculate the total number and percentage of "Placé" students
        total_students = combined_data.shape[0]
        total_place = combined_data[combined_data['Status'] == 'Placé'].shape[0]
        percentage_place = (total_place / total_students) * 100 if total_students > 0 else 0
        
        # Display the KPI
        st.write("### Pourcentage des étudiants Placé")
        st.metric(label="Pourcentage Placé", value=f"{percentage_place:.2f}%", delta=f"{total_place} étudiants")
        
        # Create visualizations
        st.write("Visualisations :")

        # Visualization for Sex Distribution by Class
        sex_chart = px.histogram(
            combined_data, 
            x='SheetName', 
            color='PersonalizedSexe', 
            barmode='group',
            title='Répartition par sexe selon la classe',
            labels={'SPECIALISATION': 'Classe', 'count': 'Nombre', 'PersonalizedSexe': 'Sexe'}
        )
        st.plotly_chart(sex_chart, use_container_width=True)

        # Visualization for Status Distribution by Class
        status_chart = px.histogram(
            combined_data, 
            x='SheetName', 
            color='Status', 
            barmode='group',
            title='Répartition par statut selon la classe',
            labels={'SPECIALISATION': 'Classe', 'count': 'Nombre', 'Status': 'Statut'}
        )
        st.plotly_chart(status_chart, use_container_width=True)



        # # Option to download the processed data
        # @st.cache_data
        # def convert_df(df):
        #     return df.to_csv(index=False).encode('utf-8')

        # csv = convert_df(combined_data)

        # st.download_button(
        #     label="Download Processed Data as CSV",
        #     data=csv,
        #     file_name='processed_data.csv',
        #     mime='text/csv',
        # )
        
    except Exception as e:
        st.error(f"An error occurred: {e}")