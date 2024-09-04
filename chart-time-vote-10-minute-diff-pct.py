import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from matplotlib.widgets import Button
import matplotlib.dates as mdates

# Set the style for a cleaner, more modern look
plt.style.use('seaborn-v0_8')

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

# Remove rows with NaT values
df = df.dropna(subset=['adjusted_time'])

# Sort the dataframe by adjusted time
df = df.sort_values('adjusted_time')

# Create 10-minute intervals
df['interval'] = df['adjusted_time'].dt.floor('10min')

# Group by 10-minute intervals and sum the votes
interval_data = df.groupby('interval').agg({'EG': 'sum', 'NM': 'sum'})

# Calculate vote percentages
interval_data['total_votes'] = interval_data['EG'] + interval_data['NM']
interval_data['EG_pct'] = interval_data['EG'] / interval_data['total_votes'] * 100
interval_data['NM_pct'] = interval_data['NM'] / interval_data['total_votes'] * 100

# Count the number of tables in each interval
interval_data['tables_count'] = df.groupby('interval').size()

# Calculate cumulative sum of tables
interval_data['cumulative_tables'] = interval_data['tables_count'].cumsum()

# Create the plot
fig, ax1 = plt.subplots(figsize=(16, 9))

# Plot the stacked bar chart
ax1.bar(interval_data.index, interval_data['EG_pct'], width=timedelta(minutes=9), align='edge', color='#3498db', alpha=0.8, label='EG')
ax1.bar(interval_data.index, interval_data['NM_pct'], width=timedelta(minutes=9), align='edge', color='#e74c3c', alpha=0.8, label='NM', bottom=interval_data['EG_pct'])

# Set up the secondary y-axis for tables count and cumulative tables
ax2 = ax1.twinx()
ax2.plot(interval_data.index, interval_data['cumulative_tables'], color='#2ecc71', linewidth=2, label='Cumulative Tables')
ax2.plot(interval_data.index, interval_data['tables_count'], color='#f39c12', linewidth=2, label='Tables per Interval')

# Set the x-axis to show hours and minutes
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax1.xaxis.set_major_locator(mdates.HourLocator(interval=1))
ax1.xaxis.set_minor_locator(mdates.MinuteLocator(byminute=[0,30]))

# Rotate and align the tick labels so they look better
fig.autofmt_xdate()

# Add labels and title
ax1.set_xlabel('Time', fontsize=12, fontweight='bold')
ax1.set_ylabel('Percentage of Votes', fontsize=12, fontweight='bold')
ax2.set_ylabel('Number of Tables', fontsize=12, fontweight='bold')
plt.title('Vote Distribution and Table Reporting Over Time', fontsize=16, fontweight='bold')

# Add legends
ax1.legend(loc='upper left', frameon=True, framealpha=0.9)
ax2.legend(loc='upper right', frameon=True, framealpha=0.9)

# Set y-axis limits
ax1.set_ylim(0, 100)
ax2.set_ylim(0, max(interval_data['cumulative_tables'].max(), interval_data['tables_count'].max()) * 1.1)

# Add a grid for better readability
ax1.grid(True, linestyle='--', alpha=0.7)

# Remove top and right spines
ax1.spines['top'].set_visible(False)
ax2.spines['top'].set_visible(False)

# Enable zooming and panning
ax1.set_navigate(True)

# Store the original view limits
original_xlim = ax1.get_xlim()
original_ylim = ax1.get_ylim()

# Function to reset the view
def reset(event):
    ax1.set_xlim(original_xlim)
    ax1.set_ylim(original_ylim)
    plt.draw()

# Add a reset button
reset_ax = plt.axes([0.85, 0.02, 0.1, 0.04])
reset_button = Button(reset_ax, 'Reset Zoom', color='#ecf0f1', hovercolor='#bdc3c7')
reset_button.on_clicked(reset)

# Adjust layout
plt.tight_layout()

# Save the plot
plt.savefig('vote_distribution_and_table_reporting.png', dpi=300, bbox_inches='tight')

# Show the plot
plt.show()