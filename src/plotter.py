import os
import glob
import pandas as pd
import matplotlib.pyplot as plt


list_of_files = glob.glob('../output_csvs/*.csv')
latest_file = max(list_of_files, key=os.path.getctime)


df = pd.read_csv(latest_file)


df = df[df['Y'] != 0]


plt.figure(figsize=(15, 10))

unique_ids = df['ID'].unique()


for unique_id in unique_ids:
    subset = df[df['ID'] == unique_id]
    plt.plot(subset['Frame'], subset['Y'], label=f'ID {unique_id}')


plt.xlabel('Frame')
plt.ylabel('Y')
plt.title('Frame vs Y for each ID')
plt.legend()

from datetime import datetime

current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')

csv_filename = os.path.splitext(os.path.basename(latest_file))[0]

output_dir = '../plots'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

filename = f'plot_{csv_filename}.png'
plt.savefig(os.path.join(output_dir, filename))
print(f"Plot saved to {output_dir}/{filename}")