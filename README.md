## Overview

This repository contains two Python scripts:

1. **`create_amber_files.py`**  
   A script that automates the process of generating AMBER topology (`.prmtop`) and coordinate (`.inpcrd`) files from a PDB file. It uses the following AMBER tools:
   - **antechamber**: to generate a MOL2 file with AM1-BCC charges.
   - **parmchk2**: to create a `.frcmod` file containing missing force-field parameters.
   - **tleap**: to load the resulting MOL2/frcmod files and produce the final `.prmtop` and `.inpcrd` files.

2. **`run_create_amber_files.py`**  
   A wrapper script that interactively prompts the user for:
   - The path to **`create_amber_files.py`**.
   - The path (absolute or relative) to the input PDB file.
   - Optional names for the output `.prmtop` and `.inpcrd` files.
   - Select Charge Options: (e.g., RESP, CM1, ESP), with AM1-BCC (-c bcc) as the default.

   After gathering this information, it calls **`create_amber_files.py`** with the appropriate arguments.

## Script 1: create_amber_files.py

### Description

This script uses **AMBER Tools** to:

1. **Convert** a given PDB file into a MOL2 file with AM1-BCC charges (using `antechamber`).
2. **Generate** a `.frcmod` file of missing force-field parameters (using `parmchk2`).
3. **Create** an AMBER parameter (topology) and coordinate file (using `tleap`).

### Usage
1. Make the script executable (optional but recommended on Linux/macOS):
```
chmod +x create_amber_files.py
```
2. Run it:
```bash
python create_amber_files.py <input.pdb> [--prmtop <output.prmtop>] [--inpcrd <output.inpcrd>]
```
- <input.pdb>: Path to the input PDB file.
- prmtop <output.prmtop>: (Optional) Specify the name of the generated topology file.
    - Default: If not provided, the script derives the base name from <input.pdb> and appends .prmtop.
- inpcrd <output.inpcrd>: (Optional) Specify the name of the generated coordinate file.
    - Default: If not provided, the script derives the base name from <input.pdb> and appends .inpcrd.
    - 
### Example

```
python create_amber_files.py my_file.pdb
```
This will produce:

- my_file.mol2
- my_file.frcmod
- my_file.prmtop
- my_file.inpcrd

You can also customize the output names:

```
python create_amber_files.py my_file.pdb --prmtop my_file_top.prmtop --inpcrd my_file_coords.inpcrd
```

## Script 2: run_create_amber_files.py
### Description
This wrapper script interactively guides the user through the process of running **`create_amber_files.py`** by prompting the following:

1. The **location** of **`create_amber_files.py`**.
    - Press **Enter** to default to the **current directory** if **`create_amber_files.py`** is also located there.
2. The **input PDB file** (can be either an absolute path or relative path).
3. (Optional) The desired names for the output `.prmtop` and `.inpcrd` files.
4. Charge Options.
    - An interactive menu displays available charge method options for antechamber. Users can select one or more options:
        1. Use RESP charges: `-c resp`
        2. Use AM1-BCC charges (default): `-c bcc`
        3. Use CM1 charges: `-c cm1`
        4. Use CM2 charges: `-c cm2`
        5. Use ESP (Kollman) charges: `-c esp`
        6. Use Mulliken charges: `-c mul`
        7. Use Gasteiger charges: `-c gas`
        8. Use ABCG2 charges: `-c abcg2`
        9. Read in charge: `-c rc`
        10. Write out charge: `-c wc`
        11. Delete Charge: `-c dc`
    - If no selection is made, the script defaults to AM1-BCC charges (`-c bcc`).

After these prompts, the script constructs the necessary command and calls **`create_amber_files.py`** with the user-supplied arguments.

### Usage
1. Make the script executable (optional but recommended on Linux/macOS):
```
chmod +x run_create_amber_files.py
```
2. Run it:
```
./run_create_amber_files.py
```
3. Follow the on-screen prompts:
    - If `create_amber_files.py` is in your current directory, just press **Enter** when asked for the script path.
    - Provide the path to your PDB file (absolute or relative).
    - Specify custom names for the `.prmtop` and `.inpcrd` files or press **Enter** to accept the defaults (which derive from the PDB filename).

Example session:
```
Enter the full or relative path to create_amber_files.py (press Enter if it's in the current directory):
[User Presses Enter]

Enter the full or relative path to the input PDB file:
my_file.pdb

Enter the desired name for the output topology (prmtop) file (press Enter to use default):
my_file_top.prmtop

Enter the desired name for the output coordinate (inpcrd) file (press Enter to use default):
my_file_coords.inpcrd

Available Charge Method Options:
1. Use RESP charges: -c resp
2. Use AM1-BCC charges (default): -c bcc
3. Use CM1 charges: -c cm1
4. Use CM2 charges: -c cm2
5. Use ESP (Kollman) charges: -c esp
6. Use Mulliken charges: -c mul
7. Use Gasteiger charges: -c gas
8. Use ABCG2 charges: -c abcg2
9. Read in charge: -c rc
10. Write out charge: -c wc
11. Delete Charge: -c dc

Enter the numbers corresponding to the charge options you want or press Enter to use default (-c bcc):
[User Presses Enter]
```

The script will then build and run a command like:
```
python /path/to/create_amber_files.py /path/to/my_file.pdb --prmtop my_file_top.prmtop --inpcrd my_file_coords.inpcrd --ac_opts "-c bcc -s 2"
```