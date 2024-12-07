# %%
import pandas as pd
import numpy as np
import altair as alt
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

OUTPUT_DIR = '../../data'
df_gvc_original = pd.read_csv("../../data/GVCpt_WIOD2016.All.2024-12-01 22-49-43.csv")
excel_data = pd.ExcelFile("../../data/CO2 emissions.xlsx")

# In case your relative path is not working, use the following
# df_gvc_original = pd.read_csv("/Users/yukireflection/Desktop/final project😠/data/GVCpt_WIOD2016.All.2024-12-01 22-49-43.csv")
# excel_data = pd.ExcelFile("/Users/yukireflection/Desktop/final project😠/data/CO2 emissions.xlsx")




# %% Data Processing: CO2 Emissions Data

# Set country list
countries = ['AUS', 'AUT', 'BEL', 'BGR', 'BRA', 'CAN', 'CHE', 'CHN', 'CYP',
       'CZE', 'DEU', 'DNK', 'ESP', 'EST', 'FIN', 'FRA', 'GBR', 'GRC',
       'HRV', 'HUN', 'IDN', 'IND', 'IRL', 'ITA', 'JPN', 'KOR', 'LTU',
       'LUX', 'LVA', 'MEX', 'MLT', 'NOR', 'POL', 'PRT', 'ROU', 'RUS',
       'SVK', 'SVN', 'SWE', 'TUR', 'TWN', 'USA']

CO2 = pd.DataFrame()

# Loop through countries in different sheet
for country in countries:
    if country in excel_data.sheet_names:
        df = excel_data.parse(sheet_name=country)

        industries_data = df.iloc[:56, :]
        
        # Inverse
        value_vars = [col for col in industries_data.columns if col.isdigit()]
        industries_data = industries_data.melt(
            id_vars=None, value_vars=value_vars, var_name="Year", value_name="CO2_Emissions"
        )
        
        industries_data["Country"] = country
        industries_data["Industry"] = np.tile([f"C{str(i+1).zfill(2)}" for i in range(56)], len(industries_data) // 56)
        industries_data["Year"] = industries_data["Year"].astype(int)
        industries_data = industries_data[industries_data["Year"].between(2000, 2014)]
        
        industries_data.columns = industries_data.columns.str.lower()
        CO2 = pd.concat([CO2, industries_data], ignore_index=True)

# Reset index and sorted
CO2 = CO2.sort_values(by=["year", "country", "industry"]).reset_index(drop=True)
CO2 = CO2[["country", "year", "industry", "co2_emissions"]]





# %% Data processing: GVC Data

# Replicate dataset
df_gvc = df_gvc_original

# Revise country and industry columns
df_gvc['country'] = df_gvc['region'].str[:3]
df_gvc = df_gvc.drop(columns=['region'])
df_gvc = df_gvc[~df_gvc['country'].isin(['NLD', 'ROW'])]  # Lack of 'NLD', and exclude 'Rest of the world'

# Keep the sorted industry
keep_sectors = ['Total', 'goods', 'manufacture', 'all service', 'services related to production']
df_gvc['industry'] = df_gvc['sector'].apply(lambda x: x[:3] if x not in keep_sectors else x)

# Drop the 'sector' column
df_gvc = df_gvc.drop(columns=['sector'])

# Reset index
df_gvc = df_gvc.set_index(['year', 'country', 'industry']).sort_index()
df_gvc = df_gvc.drop(columns=['Unnamed: 0'])
df_gvc = df_gvc.reset_index()

# Rename the columns
df_gvc = df_gvc.rename(columns={
    'GVCpt_f': 'f',
    'GVCpt_f_s': 'fs',
    'GVCpt_f_c': 'fc',
    'GVCpt_b': 'b',
    'GVCpt_b_s': 'bs',
    'GVCpt_b_c': 'bc'
})

# Create new columns
df_gvc['gvc'] = df_gvc['f'] + df_gvc['b']
df_gvc['gvcc'] = df_gvc['fc'] + df_gvc['bc']
df_gvc['gvcs'] = df_gvc['fs'] + df_gvc['bs']





# %% Create dataset (df_gvc) and save file

# Merge CO2 to GVC dataset
df_gvc = pd.merge(df_gvc, CO2[['year', 'country', 'industry', 'co2_emissions']], 
                  on=['year', 'country', 'industry'], how='left')
df_gvc.rename(columns={'co2_emissions': 'CE'}, inplace=True)

# Store the result file
output_file = "df.xlsx"
df_gvc.to_excel(f"{OUTPUT_DIR}/{output_file}", index=False)



# Exclude sorted industry (only keep C01 to 56)
# df_gvc = df_gvc[~df_gvc['sector'].isin(['Total',
#                                         'goods', 'manufacture', 'all service',
#                                         'services related to production'])]





# %% Figure 1. Forward/Backward Participation Indexes, 2000 to 2014

# Calculate the average f and b by country and year, grouped by industry
averaged_df = df_gvc[
    df_gvc['country'].isin(['USA', 'CHN', 'JPN', 'RUS']) & 
    df_gvc['year'].between(2000, 2014)
].groupby(['country', 'year'])[['f', 'b']].mean().reset_index()

# Define a common y-axis scale (assuming range 0 to 100)
y_axis_scale = alt.Scale(domain=[0, 0.35])

# Create Forward Participation Index (f) line plot with scatter points
line_plot_f = alt.Chart(averaged_df).mark_line().encode(
    x=alt.X(
        'year:O', 
        title='Year', 
        axis=alt.Axis(labelAngle=45)  # Rotate x-axis labels by 45 degrees
    ),
    y=alt.Y(
        'f:Q', 
        title='Forward Participation Index (%)', 
        scale=y_axis_scale, 
        axis=alt.Axis(format='%')
    ),
    color='country:N',  # Different color for each country
    tooltip=['year', 'country', 'f']  # Tooltip showing year, country, and f value
).properties(
    title='Forward Participation Index Over Time',
    width=600,
    height=300
) + alt.Chart(averaged_df).mark_point().encode(
    x=alt.X('year:O', axis=alt.Axis(labelAngle=45)),  # Ensure scatter points also have rotated labels
    y='f:Q',
    color='country:N',
    tooltip=['year', 'country', 'f']
)

# Create Backward Participation Index (b) line plot with scatter points
line_plot_b = alt.Chart(averaged_df).mark_line().encode(
    x=alt.X(
        'year:O', 
        title='Year', 
        axis=alt.Axis(labelAngle=45)  # Rotate x-axis labels by 45 degrees
    ),
    y=alt.Y(
        'b:Q', 
        title='Backward Participation Index (%)', 
        scale=y_axis_scale, 
        axis=alt.Axis(format='%')
    ),
    color='country:N',  # Different color for each country
    tooltip=['year', 'country', 'b']  # Tooltip showing year, country, and b value
).properties(
    title='Backward Participation Index Over Time',
    width=600,
    height=300
) + alt.Chart(averaged_df).mark_point().encode(
    x=alt.X('year:O', axis=alt.Axis(labelAngle=45)),  # Ensure scatter points also have rotated labels
    y='b:Q',
    color='country:N',
    tooltip=['year', 'country', 'b']
)

# Display the two plots side by side
alt.hconcat(line_plot_f, line_plot_b)






# %% Figure 2. GVC participation Indexes, Sector Level, 2014

# Sector Categories
industry_classification = {
    'C01': 'Agriculture', 'C02': 'Agriculture', 'C03': 'Agriculture',
    'C04': 'Mining',
    'C05': 'Manufacturing', 'C06': 'Manufacturing', 'C07': 'Manufacturing',
    'C08': 'Manufacturing', 'C09': 'Manufacturing', 'C10': 'Manufacturing',
    'C11': 'Manufacturing', 'C12': 'Manufacturing', 'C13': 'Manufacturing',
    'C14': 'Manufacturing', 'C15': 'Manufacturing', 'C16': 'Manufacturing',
    'C17': 'Manufacturing', 'C18': 'Manufacturing', 'C19': 'Manufacturing',
    'C20': 'Manufacturing', 'C21': 'Manufacturing', 'C22': 'Manufacturing',
    'C23': 'Manufacturing',
    'C24': 'Service', 'C25': 'Service', 'C26': 'Service', 'C27': 'Service',
    'C28': 'Service', 'C29': 'Service', 'C30': 'Service', 'C31': 'Service',
    'C32': 'Service', 'C33': 'Service', 'C34': 'Service', 'C35': 'Service',
    'C36': 'Service', 'C37': 'Service', 'C38': 'Service', 'C39': 'Service',
    'C40': 'Service', 'C41': 'Service', 'C42': 'Service', 'C43': 'Service',
    'C44': 'Service', 'C45': 'Service', 'C46': 'Service', 'C47': 'Service',
    'C48': 'Service', 'C49': 'Service', 'C50': 'Service', 'C51': 'Service',
    'C52': 'Service', 'C53': 'Service', 'C54': 'Service', 'C55': 'Service',
    'C56': 'Service'
}

def plot_gvc_participation_colored(df, year):
    """
    Generate a scatter plot of GVC Participation Indexes with industries grouped into 4 categories,
    differentiated by color.

    Parameters:
    - df (pd.DataFrame): The dataset containing GVC data.
    - year (int): The year to filter the dataset on.

    Returns:
    - alt.Chart: A scatter plot chart showing sectoral GVC participation indexes with categories.
    """
    # Filter the data for the specified year and only keep types
    df = df[~df['industry'].isin(['Total','goods', 'manufacture', 'all service', 'services related to production'])]
    df_filtered = df[df['year'] == year]

    # Compute sectoral averages across all countries
    df_mean = df_filtered.groupby('industry', as_index=False).agg({
        'f': 'mean',  # Mean forward-linkage
        'b': 'mean'   # Mean backward-linkage
    })

    # Add classification based on industry
    df_mean['category'] = df_mean['industry'].map(industry_classification)

    # Trim the data to ensure points are within the [0, 1] range for both axes
    df_mean_trimmed = df_mean[(df_mean['f'] <= 1) & (df_mean['f'] >= 0) &
                              (df_mean['b'] <= 1) & (df_mean['b'] >= 0)]

    # Scatter plot
    scatter_plot = alt.Chart(df_mean_trimmed).mark_point(filled=True, size=80).encode(
        x=alt.X('b:Q', title='Average Backward-Linkage', scale=alt.Scale(domain=[0, 1])),
        y=alt.Y('f:Q', title='Average Forward-Linkage', scale=alt.Scale(domain=[0, 1])),
        color=alt.Color('category:N', title='Industry Category', legend=alt.Legend(orient='right')),
        tooltip=['industry:N', 'category:N', 'f:Q', 'b:Q']
    )

    # Add diagonal reference line (b=f)
    diagonal_line = alt.Chart(pd.DataFrame({'value': [0, 1]})).mark_line(color='gray', strokeDash=[5, 5]).encode(
        x='value:Q',
        y='value:Q'
    )

    # Combine scatter plot with diagonal line
    final_plot = (scatter_plot + diagonal_line).properties(
        title=f"GVC Participation Indexes, Sectoral Level, {year}",
        width=400,
        height=400
    ).configure_title(fontSize=16)

    return final_plot


# Example usage:
# Call the function to create the plot for 2014
gvc_plot_colored = plot_gvc_participation_colored(df_gvc, 2014)

# Render the plot
gvc_plot_colored





# %% Figure 3. Forward/Backward GVC-participation Indexes, Country-Sector Level, 2014

def generate_industry_plots_with_means_and_diag(df, industries, year):
    """
    Generate scatter plots for specified industries, with country labels and a diagonal line (b=f).
    
    Parameters:
    - df (pd.DataFrame): The dataset containing the industry data.
    - industries (dict): A dictionary where keys are industry names and values are tuples:
        (sector(s), list of countries to label).
    - year (int): The year to filter the dataset on.

    Returns:
    - alt.VConcatChart: A vertically concatenated Altair chart containing all industry plots.
    """
    # Filter the data for the specified year
    df_filtered_year = df[df['year'] == year]

    # List to store individual plots
    plots = []

    for industry, (sector, countries_to_label) in industries.items():
        # Filter by sector(s)
        if isinstance(sector, list):  # If the sector is a list, filter by the industries
            df_filtered = df_filtered_year[df_filtered_year['industry'].isin(sector)]
        else:  # Otherwise, filter for the specific sector
            df_filtered = df_filtered_year[df_filtered_year['industry'] == sector]

        # Compute mean values for each country within the filtered data
        df_mean = df_filtered.groupby('country', as_index=False).agg({
            'f': 'mean',  # Forward linkage mean
            'b': 'mean'   # Backward linkage mean
        })

        # Scatter plot with black points
        scatter_plot = alt.Chart(df_mean).mark_point(color='black', clip=True).encode(
            x=alt.X('b:Q', title='Backward-Linkage', scale=alt.Scale(domain=[0, 1])),  # Backward linkage on the x-axis
            y=alt.Y('f:Q', title='Forward-Linkage', scale=alt.Scale(domain=[0, 1])),  # Forward linkage on the y-axis
            tooltip=['country:N', 'f:Q', 'b:Q']  # Show country name on hover
        )

        # Adding country labels for specified countries
        country_labels = alt.Chart(df_mean[df_mean['country'].isin(countries_to_label)]).mark_text(
            align='left', fontSize=12, dx=5, dy=-5, color='green').encode(
            x='b:Q',
            y='f:Q',
            text='country:N'
        )

        # Adding the diagonal line (b=f)
        diagonal_line = alt.Chart(pd.DataFrame({'b': [0, 1], 'f': [0, 1]})).mark_line(color='orange', strokeDash=[4, 4]).encode(
            x='b:Q',
            y='f:Q'
        )

        # Combine scatter plot, country labels, and diagonal line
        combined_plot = scatter_plot + country_labels + diagonal_line

        # Set the title for the plot
        combined_plot = combined_plot.properties(
            title=f"{industry.capitalize()}, {year}"
        )

        plots.append(combined_plot)

    # Combine all plots vertically
    final_plot = alt.vconcat(*plots)

    return final_plot


# Example usage:
industries_config = {
    'manufacture': ('manufacture', ['IND', 'DEU', 'JPN']),
    'agriculture': (['C01', 'C02', 'C03'], []),
    'all_service': ('all service', []),
    'mining': ('C04', ['JPN', 'RUS'])
}

# Call the function to generate the plots
final_chart = generate_industry_plots_with_means_and_diag(df_gvc, industries_config, 2014)

# Render the chart
final_chart





# %%
# Figure 4. Simple/Complex GVC-participation Indexes, Country-Sector Level, 2014

def generate_industry_plots_with_means_and_diag(df, industries, year):
    """
    Generate scatter plots for specified industries, with country labels and a diagonal line (b=f).
    
    Parameters:
    - df (pd.DataFrame): The dataset containing the industry data.
    - industries (dict): A dictionary where keys are industry names and values are tuples:
        (sector(s), list of countries to label).
    - year (int): The year to filter the dataset on.

    Returns:
    - alt.VConcatChart: A vertically concatenated Altair chart containing all industry plots.
    """
    # Filter the data for the specified year
    df_filtered_year = df[df['year'] == year]

    # List to store individual plots
    plots = []

    for industry, (sector, countries_to_label) in industries.items():
        # Filter by sector(s)
        if isinstance(sector, list):  # If the sector is a list, filter by the industries
            df_filtered = df_filtered_year[df_filtered_year['industry'].isin(sector)]
        else:  # Otherwise, filter for the specific sector
            df_filtered = df_filtered_year[df_filtered_year['industry'] == sector]

        # Compute mean values for each country within the filtered data
        df_mean = df_filtered.groupby('country', as_index=False).agg({
            'gvcc': 'mean',  # Forward linkage mean
            'gvcs': 'mean'   # Backward linkage mean
        })

        # Scatter plot with black points
        scatter_plot = alt.Chart(df_mean).mark_point(color='black', clip=True).encode(
            x=alt.X('gvcc:Q', title='Complicated-Linkage', scale=alt.Scale(domain=[0, 1])),  # Backward linkage on the x-axis
            y=alt.Y('gvcs:Q', title='Simple-Linkage', scale=alt.Scale(domain=[0, 1])),  # Forward linkage on the y-axis
            tooltip=['country:N', 'gvcc:Q', 'gvcs:Q']  # Show country name on hover
        )

        # Adding country labels for specified countries
        country_labels = alt.Chart(df_mean[df_mean['country'].isin(countries_to_label)]).mark_text(
            align='left', fontSize=12, dx=5, dy=-5, color='grey').encode(
            x='gvcc:Q',
            y='gvcs:Q',
            text='country:N'
        )

        # Adding the diagonal line (b=f)
        diagonal_line = alt.Chart(pd.DataFrame({'gvcc': [0, 1], 'gvcs': [0, 1]})).mark_line(color='orange', strokeDash=[4, 4]).encode(
            x='gvcc:Q',
            y='gvcs:Q'
        )

        # Combine scatter plot, country labels, and diagonal line
        combined_plot = scatter_plot + country_labels + diagonal_line

        # Set the title for the plot
        combined_plot = combined_plot.properties(
            title=f"{industry.capitalize()}, {year}"
        )

        plots.append(combined_plot)

    # Combine all plots vertically
    final_plot = alt.vconcat(*plots)

    return final_plot


# Example usage:
industries_config = {
    'manufacture': ('manufacture', ['CNH', 'USA', 'RUS', 'BEL']),
    'agriculture': (['C01', 'C02', 'C03'], ['IND', 'CAN']),
    'all_service': ('all service', []),
    'mining': ('C04', ['USA'])
}

# Call the function to generate the plots
final_chart = generate_industry_plots_with_means_and_diag(df_gvc, industries_config, 2014)

# Render the chart
final_chart





# %% Figure 5. Global Map Plot

# Load the shapefile containing global administrative boundaries
shapefile_path = "/Users/yukireflection/Desktop/final project😠/world-administrative-boundaries/world-administrative-boundaries.shp"
world = gpd.read_file(shapefile_path)

# Filter for countries with 'Member State' status
world = world[world['status'] == 'Member State']

# Prepare the data for visualization
# Filter for the year 2014, group by country, and calculate the mean for all numeric columns
df_geo = (
    df_gvc[df_gvc['year'] == 2014].groupby('country', as_index=False)
    .mean(numeric_only=True)  # Compute the mean of numeric columns
)

# Rename the 'country' column to 'iso3' for consistent merging
df_geo = df_geo.rename(columns={'country': 'iso3'})

# Merge the shapefile data with the GVC data based on the 'iso3' column
world = world.merge(df_geo, on="iso3", how="left")

# Plot the global map with GVC participation
fig, ax = plt.subplots(1, 1, figsize=(15, 10))
world.boundary.plot(ax=ax, linewidth=1, color="grey")  # Draw country boundaries in grey
world.plot(column="gvc", ax=ax, legend=True,          # Visualize GVC participation using a color scale
           cmap="Blues", edgecolor="black",           # Use blue shades for the color map
           missing_kwds={"color": "lightgrey"})       # Use light grey for missing data

# Add a title and hide axes
ax.set_title("GVC Participation by Country, 2014", fontsize=16)
ax.axis("off")

# Display the plot
plt.show()





# %% Figure 6. Europe Map Plot

# Limit to Europe Region (approximately defined by latitude and longitude bounds)
europe_bounds = (-10, 42, 15, 60)  # (min_lon, min_lat, max_lon, max_lat)

# Subset the data for countries within the specified geographic bounds
europe = world.cx[europe_bounds[0]:europe_bounds[2], europe_bounds[1]:europe_bounds[3]]

# Plot the map for Europe with GVC participation
fig, ax = plt.subplots(1, 1, figsize=(15, 10))
europe.boundary.plot(ax=ax, linewidth=1, color="grey")  # Draw country boundaries in grey
europe.plot(column="gvc", ax=ax, legend=True,           # Visualize GVC participation using a color scale
            cmap="Blues", edgecolor="black",            # Use blue shades for the color map
            missing_kwds={"color": "lightgrey"})        # Use light grey for missing data

# Add a title and hide axes
ax.set_title("GVC Participation by Country (Europe), 2014", fontsize=16)
ax.axis("off")

# Display the plot
plt.show()
# %%
