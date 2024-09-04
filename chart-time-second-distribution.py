import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Set the style for a cleaner, more modern look
plt.style.use('seaborn-v0_8')

# Read the CSV file
df = pd.read_csv('data/resultados-with-timestamps.csv')

# Function to extract seconds, minutes, and hours from the time_24 column
def extract_time_parts(time_str):
    try:
        time = datetime.strptime(time_str, "%H:%M:%S")
        return time.second, time.minute, time.hour
    except ValueError:
        print(f"Unable to parse time: {time_str}")
        return None, None, None

# Extract seconds, minutes, and hours from time_24
df['seconds'], df['minutes'], df['hours'] = zip(*df['time_24'].apply(extract_time_parts))

# Remove rows with None values
df = df.dropna(subset=['seconds', 'minutes', 'hours'])

# Count the number of tables reporting at each second, minute, and hour
second_counts = df['seconds'].value_counts().sort_index()
minute_counts = df['minutes'].value_counts().sort_index()
hour_counts = df['hours'].value_counts().sort_index()

# Count for specific hours (18 and 19)
hour_18_df = df[df['hours'] == 18]
hour_19_df = df[df['hours'] == 19]

second_counts_18 = hour_18_df['seconds'].value_counts().sort_index()
minute_counts_18 = hour_18_df['minutes'].value_counts().sort_index()
second_counts_19 = hour_19_df['seconds'].value_counts().sort_index()
minute_counts_19 = hour_19_df['minutes'].value_counts().sort_index()

# Function to create a bar chart
def create_bar_chart(counts, title, xlabel):
    if counts.empty:
        print(f"No data available for: {title}")
        return None
    
    fig, ax = plt.subplots(figsize=(16, 9))
    bars = ax.bar(counts.index, counts.values, width=0.8, align='center', color='#3498db', alpha=0.8)
    
    ax.set_xlabel(xlabel, fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Tables Reporting', fontsize=12, fontweight='bold')
    plt.title(title, fontsize=16, fontweight='bold')
    
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height}',
                ha='center', va='bottom')
    
    plt.tight_layout()
    return fig

# Create and save charts
charts = [
    (second_counts, 'Distribution of Table Reporting Times by Second', 'Second', 'tables_reporting_by_second.png'),
    (minute_counts, 'Distribution of Table Reporting Times by Minute', 'Minute', 'tables_reporting_by_minute.png'),
    (hour_counts, 'Distribution of Table Reporting Times by Hour', 'Hour', 'tables_reporting_by_hour.png'),
    (second_counts_18, 'Distribution of Table Reporting Times by Second (Hour 18)', 'Second', 'tables_reporting_by_second_hour_18.png'),
    (minute_counts_18, 'Distribution of Table Reporting Times by Minute (Hour 18)', 'Minute', 'tables_reporting_by_minute_hour_18.png'),
    (second_counts_19, 'Distribution of Table Reporting Times by Second (Hour 19)', 'Second', 'tables_reporting_by_second_hour_19.png'),
    (minute_counts_19, 'Distribution of Table Reporting Times by Minute (Hour 19)', 'Minute', 'tables_reporting_by_minute_hour_19.png'),
]

for counts, title, xlabel, filename in charts:
    fig = create_bar_chart(counts, title, xlabel)
    if fig:
        fig.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close(fig)  # Close the figure to free up memory

# Print statistics
def print_stats(name, counts):
    if counts.empty:
        print(f"\nNo data available for {name}")
        return
    
    total = counts.sum()
    print(f"\nStatistics for {name}:")
    print(f"Total number of tables: {total}")
    print(f"{name} with most tables reporting: {counts.idxmax()} ({counts.max()} tables)")
    print(f"{name} with least tables reporting: {counts.idxmin()} ({counts.min()} tables)")
    print(f"Average number of tables per {name.lower()}: {total / len(counts):.2f}")

print_stats("Seconds", second_counts)
print_stats("Minutes", minute_counts)
print_stats("Hours", hour_counts)
print_stats("Seconds (Hour 18)", second_counts_18)
print_stats("Minutes (Hour 18)", minute_counts_18)
print_stats("Seconds (Hour 19)", second_counts_19)
print_stats("Minutes (Hour 19)", minute_counts_19)

print("\nCharts have been saved for non-empty datasets. Run 'plt.show()' to display them.")