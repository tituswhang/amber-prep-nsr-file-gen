#!/usr/bin/env python3
import argparse
import subprocess
import sys
import os
import tempfile

def run_command(command, shell=False):
    """Run a command and exit if it fails."""
    print("Running command:", " ".join(command) if not shell else command)
    try:
        subprocess.check_call(command, shell=shell)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description=("Generate AMBER parameter (prmtop) and coordinate (inpcrd) files "
                     "from a PDB file using antechamber, parmchk2, and tleap.")
    )
    parser.add_argument("pdb_file", help="Input PDB file")
    parser.add_argument("--prmtop", help="Output AMBER topology file (default: <input>.prmtop)")
    parser.add_argument("--inpcrd", help="Output AMBER coordinate file (default: <input>.inpcrd)")
    parser.add_argument("--ac_opts", 
                        help=("Additional options to pass to antechamber (e.g., '-c bcc -s 2 -X <option>'). "
                              "These options will be appended to the default options."), 
                        default="")
    args = parser.parse_args()

    pdb_file = args.pdb_file
    # Get the base name without extension (e.g., mystructure from mystructure.pdb)
    base_name = os.path.splitext(os.path.basename(pdb_file))[0]

    # Set default filenames based on the input file name if not provided
    prmtop_file = args.prmtop if args.prmtop else base_name + ".prmtop"
    inpcrd_file = args.inpcrd if args.inpcrd else base_name + ".inpcrd"
    mol2_file = base_name + ".mol2"
    frcmod_file = base_name + ".frcmod"

    # Step 1: Use antechamber to generate a MOL2 file from the PDB.
    print("\n1. Converting PDB to MOL2 using antechamber...")
    antechamber_cmd = [
        "antechamber",
        "-i", pdb_file,
        "-fi", "pdb",
        "-o", mol2_file,
        "-fo", "mol2",
    ]
    # Add default options: charge method (-c bcc) and verbosity (-s 2)
    antechamber_cmd.extend(["-c", "bcc", "-s", "2"])
    # Append additional options provided by the user
    if args.ac_opts:
        extra_options = args.ac_opts.split()
        antechamber_cmd.extend(extra_options)
    run_command(antechamber_cmd)

    # Step 2: Run parmchk2 to generate missing force-field parameters.
    print("\n2. Generating frcmod file with parmchk2...")
    parmchk2_cmd = [
        "parmchk2",
        "-i", mol2_file,
        "-f", "mol2",
        "-o", frcmod_file
    ]
    run_command(parmchk2_cmd)

    # Step 3: Prepare a tleap input file.
    tleap_instructions = f"""\
source leaprc.gaff
mol = loadmol2 {mol2_file}
loadamberparams {frcmod_file}
saveamberparm mol {prmtop_file} {inpcrd_file}
quit
"""
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".in") as tleap_in:
        tleap_in.write(tleap_instructions)
        tleap_in_name = tleap_in.name

    print("\n3. Running tleap to generate prmtop and inpcrd files...")
    tleap_cmd = ["tleap", "-f", tleap_in_name]
    run_command(tleap_cmd)

    # Clean up the temporary tleap input file.
    os.remove(tleap_in_name)
    print("\nFiles generated successfully!")
    print(f"  Topology file (prmtop): {prmtop_file}")
    print(f"  Coordinate file (inpcrd): {inpcrd_file}")

if __name__ == "__main__":
    main()

