# Cityscape Dataset Generating Tool

----

## Before Using...

- This tool can only create a cityscapes-like dataset which consists two citys (`fsacI` for train and `fsacII` for validate), you can change these names in `gen_data.py`

- All output files are named in the format like:  
	`{city_name}_{num}_000019_{other_indictors}.{suffix}`

## Usage

1. Prepare your data and split them into two groups by type "json file" and "image file"
    > `png`/`jpg` formats are supported

2. Copy the corresponding group of files into `raw/json` and `raw/img` folder. 

3. For each type of files in every folder, rename them from number `1`.  
    After renaming, the structure of the folder should be like:  
    
   ```plain
    proj_root/
      |--- gen_dataset.py
      |--- raw/
      |      |--- json/
      |      |	    |--- 1.json
      |      |		|--- 2.json
      |      |      |--- 3.json
      |      |      |--- ...
      |      |--- img/
      |             |--- 1.png
      |             |--- 2.png
      |             |--- 3.png
      |             |--- ...
      |
      |--- requirements.txt
      |--- ...
    ```

4. run `gen_dataset.py`

