import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import geopandas as gpd
import json
import urllib.request

# Load the dataset from the Excel file
excel_file = pd.ExcelFile('dummydataset.xlsx')
sheet_names = excel_file.sheet_names
dataframes = []

for sheet in sheet_names:
    dataframes.append(excel_file.parse(sheet))

df = pd.concat(dataframes)
df = df.iloc[:, :-1]

# Define the Streamlit app
def main():
    st.title(":sparkles: Dashboard for CRCS Portal")
    st.write("\n")
    st.markdown("Designed and coded with :heart: by Jasween")
    st.write(":cherry_blossom: **Name: Jasween Kaur Brar**")
    st.write(":cherry_blossom: **College Name: Thapar Institute of Engineering and Technology, Patiala**")
    st.write(":cherry_blossom: **Roll No: 102017187**")
    
    st.markdown("---")

    #################### 1) User can select the society name and 2 tables appear: Society Info and States in which the society operates
    
    # Create a sidebar to select the society name
    st.sidebar.header("1) Show the Society Information and the Areas of Operations (States) for the selected society")
    selected_society = st.sidebar.selectbox("Select a Society Name", df['Name of Society'].unique(), index=df['Name of Society'].unique().tolist().index("Travancore Cochin Tourism Cooperative Society Ltd"))
    st.sidebar.markdown("---")

    # Filter the data for the selected society name
    filtered_df = df[df['Name of Society'] == selected_society]

    # Get the additional information for the selected society
    society_name = filtered_df['Name of Society'].iloc[0]
    address = filtered_df['Address'].iloc[0]
    state = filtered_df['State'].iloc[0]
    district = filtered_df['District'].iloc[0] if 'District' in filtered_df.columns else ""
    registration_date = pd.to_datetime(filtered_df['Date of Registration'].iloc[0]).date().strftime("%Y-%m-%d")
    sector_type = filtered_df['Sector Type'].iloc[0]

    # Create a table to display the society information
    st.markdown(f"<h3 style='color: darkblue;'>1) {selected_society}</h3>", unsafe_allow_html=True)

    #st.subheader("Society Information:")
    society_info = pd.DataFrame({'Society Name': [society_name],
                                 'Address': [address],
                                'State': [state],
                                'District': [district],
                                'Date of Registration': [registration_date],
                                'Sector Type': [sector_type]})
    #st.table(society_info.style.set_properties(**{'background-color': '#add8e6', 'color': 'black'}).set_table_styles([{'selector': 'th', 'props': [('background-color', '#3182bd'), ('color', 'white')]}]))

    

    # Get the list of states in the area of operation for the selected society name
    area_states = filtered_df['Area of Operation'].str.split(',').explode().str.strip().unique()

    # Create a table to display the list of states
    st.subheader("Society Information & List of States in Area of Operation:")
    table_df = pd.DataFrame({'Area of Operation': area_states})
    table_df = table_df.reset_index(drop=True).rename_axis('S. No.')
    table_df.index += 1

    # Customize the table's font and colors
    table_styles = [
        dict(selector="th", props=[("font-size", "18px"), ("text-align", "center"), ("color", "white"), ("background-color", "#3182bd")]),
        dict(selector="td", props=[("font-size", "18px"), ("text-align", "center"), ("background-color", "#add8e6"), ("color", "black")]),
    ]

    st.table(society_info.style.set_table_styles(table_styles))
    st.table(table_df.style.set_table_styles(table_styles))
    st.markdown("---")


    ######## 2) Interactive graph to show the number of societies in different sectors
    
    # Add a sidebar option to choose between bar chart and pie chart
    st.sidebar.header("2) Show the Number of Societies in Different Sectors with either Pie Chart or Bar Chart")
    chart_type = st.sidebar.selectbox("Select Chart Type", options=["Bar Chart", "Pie Chart"], index=1)  # Set index=1 for default value as "Pie Chart"
    st.sidebar.markdown("---")

    # Group the data by sector type and count the number of societies
    sector_counts = df['Sector Type'].value_counts()

    # Set a custom color palette
    custom_colors = sns.color_palette("Set3")

    # Create the chart based on the selected chart type
    if chart_type == "Bar Chart":
        # Create a bar chart
        fig, ax = plt.subplots(figsize=(8, 6))
        sector_counts.plot(kind='bar', color=custom_colors)
        ax.set_xlabel('Sector Type', fontsize=10, fontweight='bold')
        ax.set_ylabel('Number of Societies', fontsize=10, fontweight='bold')
        ax.set_title('2) Number of Societies in Different Sectors (Bar Chart)', fontsize=16, fontweight='bold', pad=20)

        # Display the bar chart using Streamlit
        st.pyplot(fig)
        st.markdown("---")

    elif chart_type == "Pie Chart":
        # Create a pie chart
        fig = go.Figure(data=[go.Pie(labels=sector_counts.index, values=sector_counts)])
        fig.update_traces(marker=dict(colors=custom_colors))

        # Customize the layout of the pie chart
        st.subheader("2) Number of Societies in Different Sectors (Pie Chart)")
        #fig.update_layout(title=dict(text='Number of Societies in Different Sectors (Pie Chart)', font=dict(size=16)))

        # Display the pie chart using Streamlit
        st.plotly_chart(fig)
        st.markdown("---")

    ######## 3) Interactive graph to show the top number of states with highest number of societies
    # Add a filter to select the number of top states to display
    st.sidebar.header("3) Show the top number of states with highest number of societies")
    num_top_states = st.sidebar.slider("Select the Number", min_value=1, max_value=15, value=8, key="state_slider")
    st.sidebar.markdown("---")

    # Group the data by state and count the number of societies
    state_counts = df['State'].value_counts().head(num_top_states)  # Display top 'num_top_states' states

    # Define prettier colors
    colors = sns.color_palette('pastel')[:num_top_states]

    # Create a smaller bar chart with prettier colors
    fig, ax = plt.subplots(figsize=(6, 4))
    state_counts.plot(kind='bar', color=colors)
    ax.set_xlabel('State', fontsize=10, fontweight='bold')
    ax.set_ylabel('Number of Societies', fontsize=10, fontweight='bold')
    ax.set_title(f'3) Top {num_top_states} States with Highest Number of Societies', fontsize=16, fontweight='bold', pad=20)

    # Display the chart using Streamlit
    st.pyplot(fig)
    st.markdown("---")


    


    ######## 4) Line chart to show the trend of society registrations over time
    
    # Add a sidebar option to choose the start year and end year
    st.sidebar.header("4) Society Registrations Over Time (Line Chart)")
    
    start_year, end_year = st.sidebar.slider(
        "Select Year Range",
        min_value=int(df['Date of Registration'].dt.year.min()),
        max_value=int(df['Date of Registration'].dt.year.max()),
        value=(int(df['Date of Registration'].dt.year.min()), int(df['Date of Registration'].dt.year.max()))
    )
    st.sidebar.markdown("---")

    # Filter the data based on the selected range of years
    filtered_df = df[
        (df['Date of Registration'].dt.year >= start_year)
        & (df['Date of Registration'].dt.year <= end_year)
    ]

    # Group the data by registration date and count the number of societies
    registrations_over_time = (
        filtered_df['Date of Registration']
        .value_counts()
        .sort_index()
        .reset_index()
    )
    registrations_over_time.columns = ['Date', 'Number of Registrations']

    # Resample the data by month to get monthly counts
    registrations_over_time = registrations_over_time.resample('M', on='Date').sum().reset_index()

    # Create a line chart using Plotly Express
    fig = px.line(registrations_over_time, x='Date', y='Number of Registrations')

    # Customize the layout of the line chart
    fig.update_layout(
        xaxis=dict(title='Date'),
        yaxis=dict(title='Number of Registrations', range=[0, registrations_over_time['Number of Registrations'].max()]),
        showlegend=False,
        font=dict(
            family="Arial",
            size=12,
            color="black",
        )
    )

    # Display the line chart using Streamlit
    st.subheader("4) Society Registrations Over Time (Line Chart)")
    st.plotly_chart(fig)
    st.markdown("---")


    ######## 5) Pie chart to display the sector types of societies for a selected state
    # Get the unique states in the dataset
    states = df['State'].unique()

    st.sidebar.header("5) Sector Types of Societies for the Selected State")
    # Add a dropdown menu to select a state
    selected_state = st.sidebar.selectbox("Select a state", states, index=states.tolist().index("MAHARASHTRA"))
    st.sidebar.markdown("---")

    # Filter the data for the selected state
    selected_state_data = df[df['State'] == selected_state]

    # Group the data by sector type and count the number of societies
    sector_counts = selected_state_data['Sector Type'].value_counts()

    # Define a custom color palette
    custom_colors = px.colors.qualitative.Set3

    # Create a pie chart with custom colors
    fig = go.Figure(data=[go.Pie(labels=sector_counts.index, values=sector_counts)])

    # Apply the custom colors to the pie chart
    fig.update_traces(marker=dict(colors=custom_colors))

    st.subheader(f"5) Sector Types of Societies for {selected_state}")
    # Customize the layout of the pie chart
    fig.update_layout(
        
        font=dict(
            family="Arial",
            size=12,
            color="black"
        ),
        height=500,  # Set the height of the figure
        width=800    # Set the width of the figure
    )

    # Add bold text inside the pie chart
    fig.update_traces(textposition='inside', textinfo='percent+label')

    # Display the pie chart using Streamlit
    st.plotly_chart(fig)
    st.markdown("---")

    ###########  6)
    st.sidebar.header("6) Number of Society Registrations Over Time for the Selected State")
    # Create a sidebar to select the state
    selected_state = st.sidebar.selectbox("Select a state", df['State'].unique(), index=df['State'].unique().tolist().index("KERALA"))
    st.sidebar.markdown("---")

    # Filter the data for the selected state
    filtered_df = df[df['State'] == selected_state]

    # Convert the registration date column to datetime format
    filtered_df['Date of Registration'] = pd.to_datetime(filtered_df['Date of Registration'], format='%Y-%m-%d')

    # Group the data by registration date and count the number of registrations
    registrations_over_time = filtered_df['Date of Registration'].value_counts().sort_index().reset_index()
    registrations_over_time.columns = ['Date', 'Number of Registrations']

    # Resample the data by month to get monthly counts
    registrations_over_time = registrations_over_time.resample('M', on='Date').sum().reset_index()

    # Create a stacked bar chart using Plotly
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=registrations_over_time['Date'],
        y=registrations_over_time['Number of Registrations'],
        name='Number of Registrations',
        marker_color='rgb(26, 118, 255)'
    ))

    st.subheader(f'6) Number of Society Registrations Over Time in {selected_state}')
    # Customize the layout of the stacked bar chart
    fig.update_layout(
        xaxis=dict(title='Date'),
        yaxis=dict(title='Number of Registrations'),
        showlegend=False,
        barmode='stack',
        font=dict(
            family="Arial",
            size=12,
            color="black"
        )
    )

    # Display the stacked bar chart using Streamlit
    st.plotly_chart(fig)
    st.markdown("---")

    

    ### 7)
    # Add a filter to select the number of top districts to display
    st.sidebar.header("7) Show the top number of districts with the highest number of societies")
    num_top_districts = st.sidebar.slider("Select the Number", min_value=1, max_value=20, value=10, key="district_slider")
    st.sidebar.markdown("---")

    # Group the data by district and count the number of societies
    district_counts = df['District'].value_counts().head(num_top_districts)  # Display top 'num_top_districts' districts

    # Define prettier colors
    colors = sns.color_palette('pastel')[:num_top_districts]

    # Create a smaller bar chart with prettier colors
    fig, ax = plt.subplots(figsize=(6, 4))
    district_counts.plot(kind='barh', color=colors)
    ax.set_xlabel('District', fontsize=10, fontweight='bold')
    ax.set_ylabel('Number of Societies', fontsize=10, fontweight='bold')
    ax.set_title(f'7) Top {num_top_districts} Districts with Highest Number of Societies', fontsize=16, fontweight='bold', pad=20)

    # Display the chart using Streamlit
    st.pyplot(fig)
    st.markdown("---")


    ######## 8) Stacked bar chart to compare count of societies in each state by sector type
    st.sidebar.header("8) Count of Societies by State and Sector Type (Stacked Bar Chart)")
    st.sidebar.markdown("---")

    ## Compare the count of societies in each state by sector type.
    st.subheader("8) Count of Societies by State and Sector Type (Stacked Bar Chart)")

    # Group the data by state and sector type, and count the number of societies
    state_sector_counts = df.groupby(['State', 'Sector Type']).size().unstack(fill_value=0)

    # Create a stacked bar chart
    fig = go.Figure(data=[
        go.Bar(name=sector_type, x=state_sector_counts.index, y=state_sector_counts[sector_type])
        for sector_type in state_sector_counts.columns
    ])

    # Customize the layout of the bar chart
    fig.update_layout(
        barmode='stack',
        xaxis=dict(title='State', title_font=dict(size=12)),
        yaxis=dict(title='Number of Societies', title_font=dict(size=12)),
        showlegend=True,
        font=dict(
            family="Arial",
            size=12,
            color="black"
        )
    )

    # Display the stacked bar chart using Streamlit
    st.plotly_chart(fig)
    st.markdown("---")



    ######## 9) Word cloud to showcase popular themes in society names
    # Add a sidebar header and divider
    st.sidebar.header("9) Word Cloud: Popular Themes in Society Names")

    # Get the selected state from the sidebar
    selected_state = st.sidebar.selectbox("Select a state", states, index=states.tolist().index("KERALA"), key="word_cloud")
    st.sidebar.markdown("---")

    # Filter the data based on the selected state
    filtered_df = df[df['State'] == selected_state]

    # Convert society names to strings for the selected state
    society_names = filtered_df['Name of Society'].apply(str)

    # Combine all society names into a single string
    text = ' '.join(society_names)

    # Create word cloud
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

    # Plot the word cloud
    fig = plt.figure(figsize=(10, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')

    # Set the title of the word cloud to match the title of the bar chart
    plt.title(f"9) Word Cloud: Popular Themes in Society Names ({selected_state})", fontsize=24, fontweight='bold', pad=30)

    # Display the word cloud using Streamlit
    st.pyplot(fig)
    st.markdown("---")


    

    

    

    


    

    


    
    #####  Choropleth map showing the count of societies in each state of India
    








    



# Run the Streamlit app
if __name__ == "__main__":
    main()
