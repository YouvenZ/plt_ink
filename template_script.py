# Example script to plot data from CSV file
# This script is loaded using "Load from File" option

# Read the CSV data (automatically loaded by extension)
# Variables available: x_data, y_data

# Create the plot
plt.plot(x_data, y_data, marker='o', linestyle='-', linewidth=2, markersize=8)
plt.title('Sales Data Over Time')
plt.xlabel('Month')
plt.ylabel('Sales ($)')
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)