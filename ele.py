import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter  # Import DateFormatter for date formatting

# Load the two CSV files
cons = 'https://raw.githubusercontent.com/mirwaissian/electricity-analysis-pro/main/Electricity_20-09-2024.csv'
price = 'https://raw.githubusercontent.com/mirwaissian/electricity-analysis-pro/main/sahkon-hinta-010121-240924.csv'


# Remove leading/trailing spaces in the 'Time' column and convert to datetime
cons['Time'] = pd.to_datetime(cons['Time'].str.strip(), format='%d.%m.%Y %H:%M', dayfirst=True)
price['Time'] = pd.to_datetime(price['Time'], format='%d-%m-%Y %H:%M:%S')

# Merge the two datasets on the 'Time' column
merged_df = pd.merge(cons, price, on='Time', how='inner')

# Ensure 'Time' is in datetime format and set it as the index for resampling
merged_df['Time'] = pd.to_datetime(merged_df['Time'])
merged_df.set_index('Time', inplace=True)

# Convert 'Energy (kWh)' and 'Price (cent/kWh)' to numeric, removing commas
merged_df['Energy (kWh)'] = pd.to_numeric(merged_df['Energy (kWh)'].str.replace(',', '.'))
merged_df['Price (cent/kWh)'] = pd.to_numeric(merged_df['Price (cent/kWh)'])

# Calculate the hourly bill (price in euros)
merged_df['Hourly Bill (€)'] = (merged_df['Energy (kWh)'] * (merged_df['Price (cent/kWh)'] / 100))

# Convert 'Temperature' to numeric, replacing commas
merged_df['Temperature'] = pd.to_numeric(merged_df['Temperature'].str.replace(',', '.'), errors='coerce')

# Add Streamlit elements
st.title('Electricity Consumption Analysis')

# Date selector
start_date = st.date_input('Start date', value=pd.to_datetime('2021-01-01'))
end_date = st.date_input('End date', value=pd.to_datetime('2024-09-24'))

# Filter data based on date
filtered_data = merged_df.loc[(merged_df.index >= pd.to_datetime(start_date)) & 
                              (merged_df.index <= pd.to_datetime(end_date))]

# Calculate summary stats
total_consumption = filtered_data['Energy (kWh)'].sum()
total_bill = filtered_data['Hourly Bill (€)'].sum()
avg_price = filtered_data['Price (cent/kWh)'].mean()
avg_paid_price = (total_bill / total_consumption) * 100 if total_consumption != 0 else 0

# Display summary stats
st.write(f"Showing range: {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}")
st.write(f"Total consumption over the period: {total_consumption:.1f} kWh")
st.write(f"Total bill over the period: {total_bill:.2f} €")
st.write(f"Average hourly price: {avg_price:.2f} cents")
st.write(f"Average paid price: {avg_paid_price:.2f} cents")

# Grouping selector
group_interval = st.selectbox('Averaging period:', ['Daily', 'Weekly', 'Monthly'])

if group_interval == 'Daily':
    grouped_data = filtered_data.resample('D').sum()
elif group_interval == 'Weekly':
    grouped_data = filtered_data.resample('W').sum()
else:
    grouped_data = filtered_data.resample('M').sum()

# Define month name format for the x-axis
date_format = DateFormatter("%B")  # This will show month names like January, February

# Plot Energy
st.write('Electricity consumption (kWh)')
fig, ax = plt.subplots(figsize=(15, 6))
ax.plot(grouped_data.index, grouped_data['Energy (kWh)'], color='blue')
ax.set_title('Electricity consumption (kWh)')
ax.set_xlabel('Month')
ax.set_ylabel('Electricity consumption [kWh]')
ax.xaxis.set_major_formatter(date_format)  # Apply month name format
fig.autofmt_xdate()  # Auto format x-axis labels
st.pyplot(fig)

# Plot Price (cent/kWh)
st.write('Electricity price (cent/kWh)')
fig, ax = plt.subplots(figsize=(15, 6))
ax.plot(grouped_data.index, grouped_data['Price (cent/kWh)'], color='red')
ax.set_title('Electricity price (cent/kWh)')
ax.set_xlabel('Month')
ax.set_ylabel('Electricity price [cents]')
ax.xaxis.set_major_formatter(date_format)  # Apply month name format
fig.autofmt_xdate()  # Auto format x-axis labels
st.pyplot(fig)

# Plot Hourly Bill (€)
st.write('Electricity bill (€)')
fig, ax = plt.subplots(figsize=(15, 6))
ax.plot(grouped_data.index, grouped_data['Hourly Bill (€)'], color='green')
ax.set_title('Electricity bill (€)')
ax.set_xlabel('Month')
ax.set_ylabel('Electricity bill [€]')
ax.xaxis.set_major_formatter(date_format)  # Apply month name format
fig.autofmt_xdate()  # Auto format x-axis labels
st.pyplot(fig)

# Plot Temperature
st.write('Temperature')
fig, ax = plt.subplots(figsize=(15, 6))
ax.plot(grouped_data.index, grouped_data['Temperature'], color='orange')
ax.set_title('Temperature')
ax.set_xlabel('Month')
ax.set_ylabel('Temperature')
ax.xaxis.set_major_formatter(date_format)  # Apply month name format
fig.autofmt_xdate()  # Auto format x-axis labels
st.pyplot(fig)
