README

# The zip file contains: 

1. example path file 
	- path_for_one_file_2019_03_04__RIT_to_HOME.kml

2. hazard file 
	- hazard_for_one_file_2019_03_04__RIT_to_Home.kml
	- hazard_for_all_files.kml

3. the project writeup 
	- Garg_Li_Project_Report.pdf

4. python program to run all txt files (Takes 15 minutes to Run)
	- batch_processing_gps_data.py
	- usage: python3 batch_processing_gps_data.py

	- IMPORTANT: folder structure requires to run the program: 
		* batch_processing_gps_data.py
		* gps_data 	(this is where you should keep the txt files)
			* 1.txt
			* 2.txt
			* ...
		* gen_kmls	(auto-generated, this is where the kml path file are)
		* Left Turn.kml 	(auto-generated, contain points only)
		* Right Turn.kml 	(auto-generated, contain points only)
		* Stop Signs.kml 	(auto-generated, contain points only)

5. python program to run 1 txt files 
	- GPS_Data_Project_by_Li_Garg.py
	- usage: python3 GPS_Data_Project_by_Li_Garg.py [filepath/filename]

6. pythpn program containing turn and stop detections
	- costmap.py

# How to test our program: 

* usage: python3 batch_processing_gps_data.py  OR 
* usage: python3 GPS_Data_Project_by_Li_Garg.py [filepath/filename]
