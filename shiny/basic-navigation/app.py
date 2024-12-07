# shiny run --reload basic-navigation/app.py
from shiny import App, render, ui, reactive
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import to_rgba
import geopandas as gpd
import os

# Loading data
current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.abspath(os.path.join(current_dir, "../../data"))

df = pd.read_csv(os.path.join(data_dir, "processed_data.csv"))
df2 = pd.read_csv(os.path.join(data_dir, "aggregated_data.csv"))
df_geo = gpd.read_file(os.path.join(data_dir, "world-administrative-boundaries/world-administrative-boundaries.shp"))

# Define UI
app_ui = ui.page_navbar(
    ui.nav_panel(
        "Geo Plot",
        ui.page_fluid(
            ui.h3("Geospatial Plot: Total CO2 Emissions"),
            ui.input_slider("geo_year", "Choose Year:", min=2000, max=2014, value=2000, step=1),
            ui.output_plot("geo_plot"),
            ui.h4("Top 5 Countries by CO2 Emissions"),
            ui.output_table("top5_table"),
            ui.h4("Bottom 5 Countries by CO2 Emissions"),
            ui.output_table("bottom5_table"),
        ),
    ),
    ui.nav_panel(
        "Nation Level",
        ui.page_fluid(
            ui.h3("Nation Level: GVC Participation vs CO2 Emissions"),
            ui.row(
                ui.column(
                    6,
                    ui.input_select("country1", "Choose the first country:", list(df['country'].unique()), selected=df['country'].iloc[0]),
                    ui.input_select("country3", "Choose the third country:", list(df['country'].unique()), selected=df['country'].iloc[2]),
                ),
                ui.column(
                    6,
                    ui.input_select("country2", "Choose the second country:", list(df['country'].unique()), selected=df['country'].iloc[1]),
                    ui.input_select("country4", "Choose the fourth country:", list(df['country'].unique()), selected=df['country'].iloc[3]),
                ),
            ),
            ui.input_radio_buttons(
                "participation",
                "Choose forward or backward:",
                {
                    "average_f": "Forward Participation",
                    "average_b": "Backward Participation",
                    "average_gvcs": "Simple GVC Participation",
                    "average_gvcc": "Complex GVC Participation",
                },
                selected="average_f",
            ),
            ui.output_plot("scatter_plot"),
        ),
    ),
    ui.nav_panel(
        "Industry Level",
        ui.page_fluid(
            ui.h3("Industry Level: GVC Participation vs CO2 Emissions"),
            ui.input_slider("year", "Choose Year:", min=2000, max=2014, value=2000, step=1),
            ui.input_radio_buttons(
                "participation_type",
                "Choose Participation Type:",
                {"f": "Forward Participation", "b": "Backward Participation", "gvcs": "Simple GVC Participation", "gvcc": "Complex GVC Participation"},
                selected="f",
            ),
            ui.row(
                ui.column(6, ui.output_plot("agriculture_plot")),
                ui.column(6, ui.output_plot("manufacturing_plot")),
            ),
            ui.row(
                ui.column(6, ui.output_plot("service_plot")),
                ui.column(6, ui.output_plot("mining_plot")),
            ),
        ),
    ),
)

# Server Logic
def server(input, output, session):
    # Filter geoc data based on Member State status and merge
    @reactive.calc
    def filtered_geo_data():
        geo_filtered = df_geo[df_geo['status'] == "Member State"]
        
        df_filtered = df[df['year'] == input.geo_year()]
        
        merged_data = geo_filtered.merge(
            df_filtered,
            left_on="iso3",
            right_on="country",
            how="left"
        )
        return merged_data
    
    # Get top 5 countries by total CO2 emissions
    @reactive.calc
    def top5_countries_data():
        df_filtered = df[df['year'] == input.geo_year()]
        top5 = df_filtered.sort_values(by="CE", ascending=False).head(5)
        return top5[["country", "CE", "average_gvc", "average_gvcs", "average_gvcc", "average_f", "average_b"]]
    
    # Get bottom 5 countries by total CO2 emissions
    @reactive.calc
    def bottom5_countries_data():
        df_filtered = df[df['year'] == input.geo_year()]
        bottom5 = df_filtered.sort_values(by="CE", ascending=True).head(5)
        return bottom5[["country", "CE", "average_gvc", "average_gvcs", "average_gvcc", "average_f", "average_b"]]
    
    # Render a table
    @output
    @render.table
    def top5_table():
        return top5_countries_data()
    
    @output
    @render.table
    def bottom5_table():
        return bottom5_countries_data()
    
    # Plot
    @render.plot
    def geo_plot():
        data = filtered_geo_data()
        
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        data.boundary.plot(ax=ax, linewidth=0.5, color="gray")
        data.plot(
            column="CE", 
            ax=ax,
            cmap="Blues",
            legend=True,
            legend_kwds={'label': "Total CO2 Emissions"},
            missing_kwds={
                "color": "lightgrey",
                "label": "No Data"
            },
        )
        ax.set_title(f"Total CO2 Emissions - {input.geo_year()}", fontsize=16)
        ax.set_axis_off()
        return fig

    # Filter data for selected nations
    @reactive.calc
    def filtered_nation_data():
        return pd.concat([
            df[df['country'] == input.country1()],
            df[df['country'] == input.country2()],
            df[df['country'] == input.country3()],
            df[df['country'] == input.country4()],
        ])
    
    # Filter industry data for selected year
    @reactive.calc
    def filtered_industry_data():
        return df2[(df2['year'] == input.year())]

    # Plot
    @render.plot
    def scatter_plot():
        data = filtered_nation_data()
        fig, ax = plt.subplots(figsize=(6, 4))
        for country, group_data in data.groupby('country'):
            ax.scatter(
                group_data[input.participation()],
                group_data['CE'],
                label=country,
                s=60,
                alpha=0.7,
            )
            if len(group_data) > 1:
                z = np.polyfit(group_data[input.participation()], group_data['CE'], 1)
                p = np.poly1d(z)
                ax.plot(group_data[input.participation()], p(group_data[input.participation()]), label=f"{country} Trend")
        ax.set_title("GVC Participation vs CO2 Emissions")
        ax.set_xlabel("GVC Participation")
        ax.set_ylabel("Total CO2 Emissions")
        ax.legend()
        ax.grid(True)
        return fig

    # Scatter plots for specific industries
    def industry_scatter_plot(classification, color):
        data = filtered_industry_data()
        class_data = data[data['classification'] == classification]

        highlight_countries = get_highlight_countries(input.participation_type(), classification)

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.scatter(
            class_data[input.participation_type()],
            class_data['CE'],
            s=50,
            color=to_rgba(color),
        )

        for _, row in class_data[class_data['country'].isin(highlight_countries)].iterrows():
            if not np.isnan(row[input.participation_type()]) and not np.isnan(row['CE']):
                ax.text(
                    row[input.participation_type()],
                    row['CE'],
                    row['country'],  # Country name as label
                    fontsize=6,
                    ha='right',
                    color='black'
                )

        ax.set_title(f"{classification}")
        ax.set_xlabel("Participation")
        ax.set_ylabel("Total CO2 Emission")
        ax.set_xlim(0.0, 1.0)
        ax.grid(True)
        return fig
    
    # Plot 4 industries
    @render.plot
    def agriculture_plot():
        return industry_scatter_plot("Agriculture", color="#FF9999")

    @render.plot
    def manufacturing_plot():
        return industry_scatter_plot("Manufacturing", color="#99CCFF")

    @render.plot
    def service_plot():
        return industry_scatter_plot("Service", color="#FFCC99")

    @render.plot
    def mining_plot():
        return industry_scatter_plot("Mining", color="#CC99FF")
    
    # Get highlighted countries' details
    def get_highlight_countries(participation_type, classification):
        highlight_mapping = {
            "f": {
                "Agriculture": ["CHN", "USA", "IND"],
                "Service": ["USA", "CHN", "LUX"],
                "Manufacturing": ["CHN", "USA", "JPN"],
                "Mining": ["USA", "CHN", "RUS"],
            },
            "b": {
                "Agriculture": ["CHN", "USA", "IND"],
                "Service": ["USA", "CHN", "RUS"],
                "Manufacturing": ["CHN", "USA", "JPN"],
                "Mining": ["USA", "CHN", "RUS"],
            },
            "gvcs": {
                "Agriculture": ["CHN", "USA", "IND"],
                "Service": ["USA", "CHN", "RUS", "JPN"],
                "Manufacturing": ["CHN", "USA", "JPN"],
                "Mining": ["USA", "CHN", "RUS"],
            },
            "gvcc": {
                "Agriculture": ["CHN", "USA", "IND"],
                "Service": ["USA", "CHN", "RUS", "JPN"],
                "Manufacturing": ["CHN", "USA", "JPN"],
                "Mining": ["USA", "CHN", "RUS"],
            },
        }
        return highlight_mapping.get(participation_type, {}).get(classification, [])

app = App(app_ui, server)

