import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from matplotlib.widgets import Button

# Set the style for a cleaner, more modern look
plt.style.use('seaborn-v0_8-whitegrid')

# Read the CSV file
df = pd.read_csv('data/resultados-with-timestamps.csv')

# Convert time_24 to datetime and adjust for crossing midnight
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

df['adjusted_time'] = df['time_24'].apply(adjust_time)

# Remove rows with NaT values
df = df.dropna(subset=['adjusted_time'])

# Sort the dataframe by adjusted time
df = df.sort_values('adjusted_time')

# Calculate cumulative votes
df['EG_cumulative'] = df['EG'].cumsum()
df['NM_cumulative'] = df['NM'].cumsum()

# Create the plot
fig, ax = plt.subplots(figsize=(12, 6))
ax.set_facecolor('#f0f0f0')  # Set a light gray background only for the plot area

# Plot cumulative votes
ax.plot(df['adjusted_time'], df['EG_cumulative'] / 1e6, label='EG', color='#3498db', alpha=0.8, linewidth=2.5)
ax.plot(df['adjusted_time'], df['NM_cumulative'] / 1e6, label='NM', color='#e74c3c', alpha=0.8, linewidth=2.5)

# Set the x-axis to show hours and minutes
ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))
ax.xaxis.set_major_locator(plt.matplotlib.dates.HourLocator(interval=1))

# Rotate and align the tick labels so they look better
fig.autofmt_xdate()

# Add labels and title
ax.set_xlabel('Reported Closing Time', fontsize=12, fontweight='bold')
ax.set_ylabel('Cumulative Votes (Millions)', fontsize=12, fontweight='bold')
ax.set_title('Cumulative Votes for EG and NM Over Time', fontsize=16, fontweight='bold')

# En español
# ax.set_xlabel('Hora de cierre reportada', fontsize=12, fontweight='bold')
# ax.set_ylabel('Votos Acumulados (Millones)', fontsize=12, fontweight='bold')
# ax.set_title('Votos Acumulados para EG y NM por Hora', fontsize=16, fontweight='bold')


# Format y-axis ticks to show millions
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.1f}M'))

# Add a legend
ax.legend(loc='upper right', bbox_to_anchor=(1, 0.9), frameon=True, framealpha=0.9)

# Add a grid for better readability
ax.grid(True, linestyle='--', alpha=0.7)

# Remove top and right spines
ax.spines['top'].set_visible(False)

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
plt.savefig('cumulative_votes_over_time.png')

# Show the plot
plt.show()
