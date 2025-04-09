import os
import subprocess

def main():
    # 1
    create_script_input = input("Enter the full or relative path to create_amber_files.py (press Enter if it's in the current directory): ").strip()
    if not create_script_input:
        create_script = os.path.join(os.getcwd(), "create_amber_files.py")
    else:
        create_script = os.path.abspath(create_script_input)
    if not os.path.isfile(create_script):
        print("Error: The specified create_amber_files.py file does not exist at", create_script)
        return

    # 2
    pdb_file_input = input("Enter the full or relative path to the input PDB file: ").strip()
    pdb_file = os.path.abspath(pdb_file_input)
    if not os.path.isfile(pdb_file):
        print("Error: The specified PDB file does not exist at", pdb_file)
        return

    # 3
    prmtop_file = input("Enter the desired name for the output topology (prmtop) file (press Enter to use default): ").strip()
    inpcrd_file = input("Enter the desired name for the output coordinate (inpcrd) file (press Enter to use default): ").strip()

    # 4
    print("\nAvailable Charge Method Options:")
    charge_options = {
        "1": "-c resp",
        "2": "-c bcc",
        "3": "-c cm1",
        "4": "-c cm2",
        "5": "-c esp",
        "6": "-c mul",
        "7": "-c gas",
        "8": "-c abcg2",
        "9": "-c rc",
        "10": "-c wc",
        "11": "-c dc"
    }
    descriptions = {
        "1": "Use RESP charges",
        "2": "Use AM1-BCC charges (default)",
        "3": "Use CM1 charges",
        "4": "Use CM2 charges",
        "5": "Use ESP (Kollman) charges",
        "6": "Use Mulliken charges",
        "7": "Use Gasteiger charges",
        "8": "Use ABCG2 charges",
        "9": "Read in charge",
        "10": "Write out charge",
        "11": "Delete Charge"
    }

    for num in sorted(charge_options, key=lambda x: int(x)):
        print(f"{num}. {descriptions[num]}: {charge_options[num]}")
    user_charge_selection = input("Enter the numbers corresponding to the charge options you want or press Enter to use default (-c bcc): ").strip()

    if user_charge_selection:
        selected_numbers = user_charge_selection.split()
        selected_options = [charge_options[num] for num in selected_numbers if num in charge_options]
        ac_opts = " ".join(selected_options)
    else:
        ac_opts = "-c bcc"
    # Automatically append default verbosity option.
    ac_opts += " -s 2"

    # Build argument list for create_amber_files.py.
    base_command = [create_script, pdb_file]
    if prmtop_file:
        base_command.extend(["--prmtop", prmtop_file])
    if inpcrd_file:
        base_command.extend(["--inpcrd", inpcrd_file])
    if ac_opts:
        base_command.extend(["--ac_opts", ac_opts])
    
    # List of python interpreter candidates to try.
    python_candidates = ["python", "python3", "python3.8"]

    success = False
    for candidate in python_candidates:
        command = [candidate] + base_command
        print("\nTrying command:")
        print(" ".join(command))
        try:
            result = subprocess.run(command)
            if result.returncode == 0:
                print("\nScript executed successfully using ", candidate)
                success = True
                break
            else:
                print(f"\n{candidate} ran the script but it exited with non-zero exit code ({result.returncode}). Trying next candidate...")
        except FileNotFoundError:
            print(f"\n{candidate} not found, trying next candidate...")
        except Exception as e:
            print(f"\nAn error occurred when trying {candidate}: {e}")
    
    if not success:
        print("\nNone of the Python interpreter candidates succeeded in running create_amber_files.py.")

if __name__ == '__main__':
    main()

