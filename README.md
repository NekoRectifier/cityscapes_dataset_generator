# Cityscape Dataset Generating Tool

----

## Usage

1. Split your annotation json and original pictures into 2 groups.  
    Like one for `training` and one for `validating`


2. Copy the corresponding group of files into `raw_train` and `raw_val` folder.  
    

3. For each type of files in every folder, rename them from number `1`.  
    After renaming, the structure of the folder should be like:  
    
   ```plaintext
   
    proj_root/
      |--- gen_dataset.py
      |--- raw_train
      |      |--- 1.json
      |      |--- 1.png
      |      |--- 2.json
      |      |--- 2.png
      |      |--- ...
      |
      |--- raw_val
      |      |--- 1.json
      |      |--- 1.png
      |      |--- 2.json
      |      |--- 2.png
      |      |--- ...
      |
      |--- requirements.txt
      |--- ...
      
    ```

4. run `gen_dataset.py`

