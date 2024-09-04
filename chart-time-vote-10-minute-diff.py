import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from matplotlib.widgets import Button

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

# Print some information about the data
print(f"Total number of rows: {len(df)}")
print(f"Earliest timestamp: {df['adjusted_time'].min()}")
print(f"Latest timestamp: {df['adjusted_time'].max()}")
print(f"Unique hours in the data: {sorted(df['adjusted_time'].dt.hour.unique())}")

# Create 10-minute intervals
df['interval'] = df['adjusted_time'].dt.floor('10min')

# Group by 10-minute intervals and sum the votes
interval_data = df.groupby('interval').agg({'EG': 'sum', 'NM': 'sum'})

# Calculate vote difference (EG - NM)
interval_data['vote_diff'] = interval_data['EG'] - interval_data['NM']

# Create the plot
fig, ax = plt.subplots(figsize=(12, 6))

# Plot the vote difference
bars = ax.bar(interval_data.index, interval_data['vote_diff'], width=timedelta(minutes=9), align='edge', alpha=0.7)

# Color the bars based on which candidate is favored
for bar, diff in zip(bars, interval_data['vote_diff']):
    if diff > 0:
        bar.set_color('blue')
    else:
        bar.set_color('red')

# Set the x-axis to show hours and minutes
ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))
ax.xaxis.set_major_locator(plt.matplotlib.dates.HourLocator(interval=1))

# Rotate and align the tick labels so they look better
fig.autofmt_xdate()

# Add labels and title
ax.set_xlabel('Time')
ax.set_ylabel('Vote Difference (EG - NM)')
ax.set_title('Vote Difference (EG - NM) in 10-Minute Intervals')

# Add a horizontal line at y=0
ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

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
plt.savefig('vote_difference_per_10min_interval.png')

# Show the plot
plt.show()
