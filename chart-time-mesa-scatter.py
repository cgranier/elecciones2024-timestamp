import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from matplotlib.widgets import Button
import matplotlib.colors as mcolors
import numpy as np
import mplcursors

# Language selector: 'en' for English, 'es' for Spanish
language = 'en'

# Set the style for a cleaner, more modern look
plt.style.use('seaborn-v0_8-whitegrid')

# Read the CSV file
df = pd.read_csv('data/resultados-with-timestamps.csv')

# Function to extract hour and minute from the time_24 column and adjust for next day
def adjust_time(time_str):
    if time_str == '15:05:58':
        time_str = '19:26:00'
    try:
        time = datetime.strptime(time_str, "%H:%M")
    except ValueError:
        try:
            time = datetime.strptime(time_str, "%H:%M:%S")
        except ValueError:
            print(f"Unable to parse time: {time_str}")
            return pd.NaT
    if time.hour < 18:
        time += timedelta(days=1)
    return time

# Convert time_24 to datetime and adjust for next day if necessary
df['adjusted_time'] = df['time_24'].apply(adjust_time)

# Remove rows with NaT values and sort by adjusted time
df = df.dropna(subset=['adjusted_time']).sort_values('adjusted_time')

# Define the interval
# Change interval to 10S, 15S, 1min, 1T, 5min, 15min, 1H, etc.
# to accumulated more voting booths per interval
interval = '1T'
df['interval'] = df['adjusted_time'].dt.floor(interval)

# Function to convert interval to readable format (bilingual)
def interval_to_text(interval):
    if interval.endswith('min'):
        value = int(interval[:-3])
        if language == 'en':
            return f"{value} minute" if value == 1 else f"{value} minutes"
        else:
            return f"{value} minuto" if value == 1 else f"{value} minutos"
    
    value = int(interval[:-1])
    unit = interval[-1]
    
    if language == 'en':
        if unit == 'S':
            return f"{value} second" if value == 1 else f"{value} seconds"
        elif unit == 'T':
            return f"{value} minute" if value == 1 else f"{value} minutes"
        elif unit == 'H':
            return f"{value} hour" if value == 1 else f"{value} hours"
    else:
        if unit == 'S':
            return f"{value} segundo" if value == 1 else f"{value} segundos"
        elif unit == 'T':
            return f"{value} minuto" if value == 1 else f"{value} minutos"
        elif unit == 'H':
            return f"{value} hora" if value == 1 else f"{value} horas"
    
    return interval
    
# Calculate cumulative votes for each 15-minute interval
df['cumulative_EG'] = df.groupby('interval')['EG'].cumsum()
df['cumulative_NM'] = df.groupby('interval')['NM'].cumsum()

# Calculate the number of results (voting booths) per interval
df['tables_in_interval'] = df.groupby('interval')['EG'].transform('count')

# Calculate total votes and winning percentage for each interval
df['total_votes'] = df['cumulative_EG'] + df['cumulative_NM']
df['winning_pct'] = df[['cumulative_EG', 'cumulative_NM']].max(axis=1) / df['total_votes'] * 100
df['winner'] = df[['cumulative_EG', 'cumulative_NM']].idxmax(axis=1)

# Determine the color based on the winner
df['color'] = np.where(df['cumulative_EG'] > df['cumulative_NM'], 'lightblue', 'lightcoral')

# Keep only the last row of each 15-minute interval
df = df.groupby('interval').last().reset_index()

# Create the plot
fig, ax = plt.subplots(figsize=(15, 8))
ax.set_facecolor('#f0f0f0')  # Set a light gray background only for the plot area

# Plot the scatter plot with the new color scheme
scatter = ax.scatter(df['adjusted_time'], df['winning_pct'], 
                     c=df['color'],
                     s=df['tables_in_interval'] * 3, 
                     alpha=0.7,
                     edgecolors='gray',
                     linewidth=0.5)

# Add tooltips
cursor = mplcursors.cursor(scatter, hover=True)

@cursor.connect("add")
def on_add(sel):
    index = sel.target.index
    time = df['adjusted_time'].iloc[index].strftime('%H:%M')
    eg_pct = df['cumulative_EG'].iloc[index] / df['total_votes'].iloc[index] * 100
    nm_pct = df['cumulative_NM'].iloc[index] / df['total_votes'].iloc[index] * 100
    results_count = df['tables_in_interval'].iloc[index]
    
    if language == 'en':
        tooltip_text = (f"Time: {time}\n"
                        f"EG: {eg_pct:.2f}%\n"
                        f"NM: {nm_pct:.2f}%\n"
                        f"Tables: {results_count}")
    else:
        tooltip_text = (f"Hora: {time}\n"
                        f"EG: {eg_pct:.2f}%\n"
                        f"NM: {nm_pct:.2f}%\n"
                        f"Mesas: {results_count}")
    
    sel.annotation.set_text(tooltip_text)
    sel.annotation.get_bbox_patch().set(fc="white", alpha=0.8, ec="black")

# Set the x-axis to show hours and minutes
ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))
ax.xaxis.set_major_locator(plt.matplotlib.dates.HourLocator(interval=1))

# Rotate and align the tick labels so they look better
fig.autofmt_xdate()

# Convert interval to a more readable format for the title
interval_text = interval_to_text(interval)

# Set labels and title based on language
if language == 'en':
    ax.set_xlabel('Reported Closing Time', fontsize=12, fontweight='bold')
    ax.set_ylabel('Winning Percentage', fontsize=12, fontweight='bold')
    ax.set_title(f'Winning Percentage per Voting Booths Over Time (Interval: {interval_text})', 
                 fontsize=16, fontweight='bold')
    legend_labels = ['In favor of NM', 'In favor of EG']
else:
    ax.set_xlabel('Hora de Cierre Reportada', fontsize=12, fontweight='bold')
    ax.set_ylabel('Porcentaje de Ventaja', fontsize=12, fontweight='bold')
    ax.set_title(f'Porcentaje de Ventaja por Centros Reportados (Intervalo: {interval_text})', 
                 fontsize=16, fontweight='bold')
    legend_labels = ['A favor de NM', 'A favor de EG']


# Set y-axis limits to 50-100%
ax.set_ylim(50, 100)

# Update legend
ax.scatter([], [], c='lightcoral', label=legend_labels[0], s=20)
ax.scatter([], [], c='lightblue', label=legend_labels[1], s=20)
ax.legend()

# Add a grid for better readability
ax.grid(True, linestyle='--', alpha=0.7)

# Enable zooming and panning
ax.set_navigate(True)

# Store the original view limits
original_xlim = ax.get_xlim()
original_ylim = ax.get_ylim()

# Function to reset the view
def reset(event):
    ax.set_xlim(original_xlim)
    ax.set_ylim(original_ylim)
    plt.draw()

# Add a reset button
reset_ax = plt.axes([0.8, 0.025, 0.1, 0.04])
reset_button = Button(reset_ax, 'Reset Zoom', color='lightgoldenrodyellow', hovercolor='0.975')
reset_button.on_clicked(reset)

# Print some information about the data
print(f"Total number of booths: {len(df)}")
print(f"Earliest timestamp: {df['adjusted_time'].min()}")
print(f"Latest timestamp: {df['adjusted_time'].max()}")
print(f"Unique hours in the data: {sorted(df['adjusted_time'].dt.hour.unique())}")

# Save the plot
plt.savefig('voting_booth_scatter.png', dpi=300, bbox_inches='tight')

# Show the plot
plt.show()