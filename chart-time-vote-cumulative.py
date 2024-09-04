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

# Calculate cumulative votes and row count
df_filtered['Cumulative_EG'] = df_filtered['EG'].cumsum()
df_filtered['Cumulative_NM'] = -df_filtered['NM'].cumsum()  # Negative for NM
df_filtered['Cumulative_Rows'] = range(1, len(df_filtered) + 1)

# Create the plot with two y-axes
fig, ax1 = plt.subplots(figsize=(12, 6))
ax2 = ax1.twinx()

# Plot cumulative EG votes (positive)
ax1.plot(df_filtered['time'], df_filtered['Cumulative_EG'], color='blue', label='EG (Cumulative)')

# Plot cumulative NM votes (negative)
ax1.plot(df_filtered['time'], df_filtered['Cumulative_NM'], color='red', label='NM (Cumulative)')

# Plot cumulative row count
ax2.plot(df_filtered['time'], df_filtered['Cumulative_Rows'], color='green', label='Voting Centers Reported')

# Fill areas
ax1.fill_between(df_filtered['time'], df_filtered['Cumulative_EG'], 0, color='blue', alpha=0.3)
ax1.fill_between(df_filtered['time'], df_filtered['Cumulative_NM'], 0, color='red', alpha=0.3)

# Set the x-axis to show hours and minutes
ax1.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))
ax1.xaxis.set_major_locator(plt.matplotlib.dates.HourLocator(interval=1))

# Rotate and align the tick labels so they look better
fig.autofmt_xdate()

# Add labels and title
ax1.set_xlabel('Time')
ax1.set_ylabel('Cumulative Votes')
ax2.set_ylabel('Cumulative Voting Centers Reported')
plt.title('Cumulative Votes and Reporting Centers Over Time')

# Add legends
ax1.legend(loc='upper left')
ax2.legend(loc='lower right')

# Add a grid for better readability
ax1.grid(True, linestyle='--', alpha=0.7)

# Add a horizontal line at y=0
ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

# Enable zooming and panning
ax1.set_navigate(True)
ax2.set_navigate(True)

# Store the original view limits
original_xlim = ax1.get_xlim()
original_y1lim = ax1.get_ylim()
original_y2lim = ax2.get_ylim()

# Function to reset the view
def reset(event):
    ax1.set_xlim(original_xlim)
    ax1.set_ylim(original_y1lim)
    ax2.set_ylim(original_y2lim)
    plt.draw()

# Add a reset button
reset_ax = plt.axes([0.8, 0.025, 0.1, 0.04])
reset_button = Button(reset_ax, 'Reset Zoom', color='lightgoldenrodyellow', hovercolor='0.975')
reset_button.on_clicked(reset)

# Save the plot
plt.savefig('cumulative_votes_and_centers_reported.png')

# Show the plot
plt.show()
