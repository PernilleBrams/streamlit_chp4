import pandas as pd
import plotly.express as px
import streamlit as st

# Title of app
st.title("Internationale studerende i Danmark - et OECD-perspektiv")

# Guide for how to use app
st.markdown("""
Denne side viser data fra **Education at a Glance 2024** om internationale studerende i Danmark ift. forskellige OECD-lande på niveau af kandidat- og bacheloruddannelser, samt alle videregående uddannelser samlet. 

- **Nordiske lande**: Sverige, Norge, Finland, Island og Danmark.
- **Vesteuropæiske lande**: Tyskland, Frankrig, Holland, Belgien, Østrig, og Schweiz.
- **OECD-lande**: Storbritannien, Irland, USA, Canada, Australien, New Zealand, Japan, Sydkorea, samt OECD og EU25 totaler.

### Sådan bruger du siden:
1. Vælg de regioner, du vil se på graferne ved at bruge afkrydsningsfelterne i sidebaren til venstre.
2. Fremhæv specifikke lande som **Norge**, **Sverige**, og **OECD/EU25 totaler** ved at aktivere fremhævningsmulighederne i sidebaren.
3. Bemærk, at **Danmark** er vist i **<span style="color:red; font-weight:bold;">rød</span>** på alle grafer.
4. Du kan bruge din mus på hver lands prik for at se baggrundsdata.
""", unsafe_allow_html=True)

# Load data from EAG2024 (Chapter B4 Tables in report)
data = pd.read_excel("masters.xlsx")

# Cleaning and processing data
cols_to_convert = [
    "BA_or_eq_2013", "BA_or_eq_2022",
    "MA_or_eq_2013", "MA_or_eq_2022",
    "DOC_or_eq_2013", "DOC_or_eq_2022",
    "ALL_TER_2013", "ALL_TER_2022"
]

# Converting to numeric
data[cols_to_convert] = data[cols_to_convert].apply(pd.to_numeric, errors='coerce')

# Calculate percentage change for relevant columns
data["Change_MA"] = (data["MA_or_eq_2022"] - data["MA_or_eq_2013"]) / data["MA_or_eq_2013"] * 100
data["Change_BA"] = (data["BA_or_eq_2022"] - data["BA_or_eq_2013"]) / data["BA_or_eq_2013"] * 100
data["Change_ALL_TER"] = (data["ALL_TER_2022"] - data["ALL_TER_2013"]) / data["ALL_TER_2013"] * 100

# Country group lists
nordic_countries = ["Denmark", "Sweden", "Norway", "Finland", "Iceland"]
western_countries = ["Germany", "France", "Netherlands", "Belgium", "Austria", "Switzerland"]
oecd_countries = ["United Kingdom", "Ireland", "United States", "Canada", "Australia", "New Zealand", "Japan", "South Korea", "OECD total", "EU25 total"]

# Prompt user to select at least one region
st.sidebar.markdown("### Vælg mindst én af disse kategorier:")

# Streamlit Sidebar checkboxes for toggling regions (Nordic is checked by default)
show_nordic = st.sidebar.checkbox("Vis Nordiske Lande", value=True, disabled=True)
show_western = st.sidebar.checkbox("Vis Vesteuropæiske Lande", value=False)
show_oecd = st.sidebar.checkbox("Vis OECD Lande", value=False)

# Check if at least one region is selected
if not (show_nordic or show_western or show_oecd):
    st.sidebar.warning("Vælg mindst én kategori")
else:
    # Combining countries based on selected regions
    comparison_countries = []
    if show_nordic:
        comparison_countries += nordic_countries
    if show_western:
        comparison_countries += western_countries
    if show_oecd:
        comparison_countries += oecd_countries

    # Filter to only include selected comparison countries
    filtered_data = data[data['Country'].isin(comparison_countries)]

    # Display highlighting options even if "Vis OECD Lande" is not selected
    st.sidebar.markdown("### Fremhæv specifikke lande:")
    highlight_scandinavia = st.sidebar.checkbox("Fremhæv Norge & Sverige", value=True)  # highlight Scandinavia checked by default
    highlight_oecd_eu = st.sidebar.checkbox("Fremhæv OECD & EU Totals", value=False)

    # Adjust the color mapping based on the toggle
    def color_map_fn(row):
        if row["Country"] == "Denmark":
            return 'red'
        elif highlight_scandinavia and row["Country"] in ["Sweden", "Norway"]:
            return 'orange'
        elif highlight_oecd_eu and row["Country"] in ["OECD total", "EU25 total"]:
            return 'green'
        else:
            return 'gray'

    # Apply color map function
    filtered_data['Color'] = filtered_data.apply(color_map_fn, axis=1)

    # Updated scatter plot function with x and y axis labels as input
    def create_scatter_plot(filtered_data, x_col, y_col, title, hover_2013, hover_2022, x_label, y_label):
    fig = px.scatter(filtered_data, x=x_col, y=y_col, text="Country",
                     color="Color",  # Use the color column as a category
                     color_discrete_map={
                         'red': 'red',
                         'orange': 'orange',
                         'green': 'green',
                         'gray': 'gray'
                     },
                     hover_name="Country",
                     hover_data={
                         hover_2013: ':.1f',  # Round to 2 decimals
                         hover_2022: ':.1f',  # Round to 2 decimals
                         'Color': False,
                         'Country': False},  # Exclude color from hover
                     labels={x_col: x_label, y_col: y_label})

    # Set plot title and subtitle combined
    fig.update_traces(marker=dict(size=12, opacity=0.8), textposition='top center')
    fig.update_layout(
        title={
            'text': title,
            'y': 0.95,  # Adjust the vertical position of the title
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'pad': {'b': 40}  # Add bottom padding to raise the title
        },
        xaxis_title=x_label,
        yaxis_title=y_label,
        width=2000,
        height=600,
        showlegend=False  # Remove the legend
    )

    # Add a vertical line at x = 0
    fig.add_shape(
        dict(
            type="line",
            x0=0, x1=0,  # Start and end x position (vertical at x = 0)
            y0=0, y1=1,  # Full height of the plot
            xref='x', yref='paper',  # Use plot's x-axis and paper's y-axis (normalized from 0 to 1)
            line=dict(color="black", width=2, dash="dash")  # Line style (dashed)
        )
    )

    return fig
    
    # Add descriptions
    st.markdown("""
    **Data stammer fra Chapter B4 Tables i [Education at a Glance 2024](https://www.oecd.org/en/publications/education-at-a-glance-2024_c00cad36-en.html)**.
    """)

    # Plots for each education level
    st.plotly_chart(create_scatter_plot(filtered_data, "Change_MA", "MA_or_eq_2022", 
                                       "Internationale studerende (Kandidatuddannelser): Udvikling (2013-2022) vs Niveau i 2022", 
                                       "MA_or_eq_2013", "MA_or_eq_2022",
                                       "Procentvis ændring (2013-2022)", "Andel af internationale studerende i 2022 (%)"))

    st.plotly_chart(create_scatter_plot(filtered_data, "Change_BA", "BA_or_eq_2022", 
                                       "Internationale studerende (Bacheloruddannelser): Udvikling (2013-2022) vs Niveau i 2022", 
                                       "BA_or_eq_2013", "BA_or_eq_2022",
                                       "Procentvis ændring (2013-2022)", "Andel af internationale studerende i 2022 (%)"))

    st.plotly_chart(create_scatter_plot(filtered_data, "Change_ALL_TER", "ALL_TER_2022", 
                                       "Internationale studerende (Alle videregående udd.): Udvikling (2013-2022) vs Niveau i 2022", 
                                       "ALL_TER_2013", "ALL_TER_2022",
                                       "Procentvis ændring (2013-2022)", "Andel af internationale studerende i 2022 (%)"))

    # Create a new plot for % of Masters (2022) vs % of Bachelors (2022)
    st.plotly_chart(create_scatter_plot(filtered_data, 
                                       x_col="MA_or_eq_2022", 
                                       y_col="BA_or_eq_2022", 
                                       title="Andel af internationale studerende (Kandidat vs Bachelor i 2022)",
                                       hover_2013="MA_or_eq_2022", 
                                       hover_2022="BA_or_eq_2022",
                                       x_label="Andel af internationale studerende i kandidatuddannelser (%)",
                                       y_label="Andel af internationale studerende i bacheloruddannelser (%)"))
