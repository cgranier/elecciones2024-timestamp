import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from matplotlib.widgets import Button

# Read the CSV file
df = pd.read_csv('data/resultados-with-timestamps.csv')

# Function to extract hour and minute from the timestamp
def extract_time(timestamp):
    if timestamp == 'NF':
        return pd.NaT
    parts = timestamp.split(':')
    return f"{parts[0]}:{parts[1]}"

# Convert timestamp to datetime and extract hour and minute
df['time'] = pd.to_datetime(df['timestamp'].apply(extract_time), format='%H:%M', errors='coerce')

# Remove rows with NaT values
df = df.dropna(subset=['time'])

# Print some information about the data
print(f"Total number of rows: {len(df)}")
print(f"Earliest timestamp: {df['time'].min()}")
print(f"Latest timestamp: {df['time'].max()}")
print(f"Unique hours in the data: {sorted(df['time'].dt.hour.unique())}")

# Filter timestamps between 6:00 and 12:00
df_filtered = df[(df['time'].dt.hour >= 6) & (df['time'].dt.hour < 12)]

print(f"\nNumber of rows between 6:00 and 12:00: {len(df_filtered)}")

if len(df_filtered) == 0:
    print("No data points found between 6:00 and 12:00. Plotting all data instead.")
    df_filtered = df  # Use all data if no points in the specified range

# Sort the dataframe by time
df_filtered = df_filtered.sort_values('time')

# Create 15-minute intervals
df_filtered['interval'] = df_filtered['time'].dt.floor('15min')

# Group by 15-minute intervals and sum the votes
interval_data = df_filtered.groupby('interval').agg({'EG': 'sum', 'NM': 'sum'})

# Create the plot
fig, ax = plt.subplots(figsize=(12, 6))

# Plot the votes for each candidate
ax.bar(interval_data.index, interval_data['EG'], width=timedelta(minutes=7), align='edge', color='blue', alpha=0.7, label='EG')
ax.bar(interval_data.index + timedelta(minutes=7), interval_data['NM'], width=timedelta(minutes=7), align='edge', color='red', alpha=0.7, label='NM')

# Set the x-axis to show hours and minutes
ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))
ax.xaxis.set_major_locator(plt.matplotlib.dates.HourLocator(interval=1))

# Rotate and align the tick labels so they look better
fig.autofmt_xdate()

# Add labels and title
ax.set_xlabel('Time')
ax.set_ylabel('Number of Votes')
ax.set_title('Votes Received by EG and NM in 15-Minute Intervals')

# Add a legend
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

# Save the plot
plt.savefig('votes_per_15min_interval.png')

# Show the plot
plt.show()
