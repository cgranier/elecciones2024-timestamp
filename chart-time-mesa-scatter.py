import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from matplotlib.widgets import Button
import matplotlib.colors as mcolors

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

# Calculate total votes and winning percentage for each booth
df['total_votes'] = df['EG'] + df['NM']
df['winning_pct'] = df[['EG', 'NM']].max(axis=1) / df['total_votes'] * 100
df['winner'] = df[['EG', 'NM']].idxmax(axis=1)

# Create a color map
cmap = mcolors.LinearSegmentedColormap.from_list("", ["red", "white", "blue"])

# Calculate color values (-1 for full NM, 1 for full EG)
df['color_value'] = (df['EG'] - df['NM']) / df['total_votes']

# Create the plot
fig, ax = plt.subplots(figsize=(15, 8))

# Plot the scatter plot
scatter = ax.scatter(df['adjusted_time'], df['winning_pct'], 
                     c=df['color_value'], cmap=cmap, 
                     s=20, alpha=0.7)

# Set the x-axis to show hours and minutes
ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))
ax.xaxis.set_major_locator(plt.matplotlib.dates.HourLocator(interval=1))

# Rotate and align the tick labels so they look better
fig.autofmt_xdate()

# Add labels and title
ax.set_xlabel('Time')
ax.set_ylabel('Winning Percentage')
ax.set_title('Winning Percentage for Each Voting Booth Over Time')

# Set y-axis limits to 50-100%
ax.set_ylim(50, 100)

# Add a color bar
cbar = plt.colorbar(scatter)
cbar.set_label('Favor towards NM (red) vs EG (blue)')

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