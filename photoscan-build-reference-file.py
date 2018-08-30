import argparse
import pandas as pd
import numpy as np
import os
from math import degrees


parser = argparse.ArgumentParser( description='This script generates a reference file from LCM logs to be used with PhotoScan.')
parser.add_argument("log_dir", type=str,  help="Path to the folder with LCM logs.")
args = parser.parse_args()

log_directory = args.log_dir

def find_lcm_logs(log_directory):
	file_list = os.listdir(log_directory)
	csv_list = []

	for file in file_list:
		if '.csv' in file:
			csv_list.append(file)
			print('Found a csv')
		elif '.CSV' in file:
			csv_list.append(file)
			print('Found a CSV')
		else:
			print('Not a csv')

	for file in csv_list:
		if 'GPSD_CLIENT' in file:
			gps_df_filename = file
		elif 'AUV_VIS_RAWLOG' in file:
			vis_df_filename = file
		elif 'UVC_RPH' in file:
			rph_df_filename = file
		elif 'UVC_OSI' in file:
			osi_df_filename = file
	return gps_df_filename, vis_df_filename, rph_df_filename, osi_df_filename

def create_master_log(gps_df, vis_df, rph_df, osi_df):
	# Concatenate dataframes, sort by time and reset index.
	combined_df = pd.concat([gps_df, vis_df, rph_df, osi_df])
	combined_df = combined_df.sort_values(by=['utime']).reset_index(drop=True)

	# Subtract start utime from rest.
	start_time = combined_df.loc[0, 'utime']
	combined_df['utime'] = (combined_df['utime'] - start_time)
	return combined_df


def interpolate_missing_data():
	# Find first missing value.
	column_list = ['latitude', 'longitude', 'heading', 'altimeter']
	for column in column_list:
		for i in range(10, len(combined_df)-10):
			print(' ', int((i/(len(combined_df)-10)*100)), '%', column, end='\r')
			if np.isnan(combined_df.loc[i, column]) == True:
				#print('missing value at:', i)
				missing_val_index = i

				prev_val_index = i - 1
				while(True):
					if np.isnan(combined_df.loc[prev_val_index, column]) == False:
						#print('value found before:', i, 'at', prev_val_index)
						break
					else:
						prev_val_index = prev_val_index - 1

				post_val_index = i + 1
				while(True):
					if np.isnan(combined_df.loc[post_val_index, column]) == False:
						#print('value found after:', i, 'at', post_val_index)
						break
					else:
						post_val_index = post_val_index + 1

				prev_val = combined_df.loc[prev_val_index, column]
				post_val = combined_df.loc[post_val_index, column]

				prev_time = combined_df.loc[prev_val_index, 'utime']
				post_time = combined_df.loc[post_val_index, 'utime']

				missing_value_time = combined_df.loc[missing_val_index, 'utime']

				time_portion = (missing_value_time - prev_time) / (post_time - prev_time)

				val_seperation = (post_val - prev_val)

				new_val = (val_seperation * time_portion) + prev_val
				#print(new_val)

				combined_df.loc[i, column] = new_val
		print('\n')
	new_df = combined_df.dropna(axis=0, how='any')
	return new_df




gps_filename, vis_filename, rph_filename, osi_filename = find_lcm_logs(log_directory)

gps_df = pd.read_csv(log_directory + gps_filename, sep=';', header=1, usecols=['utime', 'latitude', 'longitude'])
vis_df = pd.read_csv(log_directory + vis_filename, sep=';', header=1, usecols=['utime', 'image_name'])
rph_df = pd.read_csv(log_directory + rph_filename, sep=';', header=1, usecols=['utime', 'heading'])
osi_df = pd.read_csv(log_directory + osi_filename, sep=';', header=1, usecols=['utime', 'latitude', 'longitude', 'altimeter'])

combined_df = create_master_log(gps_df, vis_df, rph_df, osi_df)
combined_df = interpolate_missing_data()

# Convert lat, lon and heading angles from rad to degrees.
combined_df['latitude']  = combined_df['latitude'].apply(degrees)
combined_df['longitude'] = combined_df['longitude'].apply(degrees)
combined_df['heading']   = combined_df['heading'].apply(degrees)

#print(combined_df)

combined_df.rename(columns={'heading':'<heading>',
							'longitude':'<longitude>',
							'latitude':'<latitude>',
							'image_name':'<label>',
							'altimeter':'<altitude>'}, inplace=True)

combined_df = combined_df.drop(labels='utime', axis=1)

combined_df.to_csv(log_directory + 'combined_df.csv', index=False)

