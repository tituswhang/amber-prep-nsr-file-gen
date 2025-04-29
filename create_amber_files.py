#!/usr/bin/env python
import argparse
import subprocess
import sys
import os
import tempfile

def run_command(command, shell=False):
    print("Running command:", " ".join(command) if not shell else command)
    try:
        subprocess.check_call(command, shell=shell)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Generate AMBER topology (.prmtop) and coordinate (.inpcrd) files "
            "from a PDB or MOL2 file using antechamber (if needed), parmchk2, and tleap."
        )
    )
    parser.add_argument("input_file", help="Input: .pdb or .mol2 (MOL2 must be pre-charged by the user)")
    parser.add_argument("--prmtop", help="Output topology file (default: <base>.prmtop)")
    parser.add_argument("--inpcrd", help="Output coordinate file (default: <base>.inpcrd)")
    parser.add_argument(
        "--ac_opts",
        default="-c bcc -s 2",
        help="Options for antechamber when converting PDB → MOL2 (default: '-c bcc -s 2')"
    )
    args = parser.parse_args()

    inf = args.input_file
    base, ext = os.path.splitext(os.path.basename(inf))
    ext = ext.lower()

    # determine output names
    prmtop = args.prmtop if args.prmtop else f"{base}.prmtop"
    inpcrd = args.inpcrd if args.inpcrd else f"{base}.inpcrd"
    frcmod = f"{base}.frcmod"
    mol2   = f"{base}.mol2"

    # STEP 1: handle PDB vs MOL2
    if ext == ".pdb":
        print("\n1. Converting PDB into MOL2 via antechamber...")
        cmd = [
            "antechamber",
            "-i", inf,
            "-fi", "pdb",
            "-o", mol2,
            "-fo", "mol2"
        ] + args.ac_opts.split()
        run_command(cmd)

    elif ext == ".mol2":
        mol2 = inf
        print(f"\nInput is MOL2. skipping antechamber, using {mol2}")

    else:
        print("Error: Unsupported input extension.")
        print("       Please supply a .pdb (will be auto-converted) or a pre-charged .mol2 file.")
        sys.exit(1)

    # STEP 2: parmchk2 to generate frcmod
    print("\n2. Generating frcmod with parmchk2...")
    run_command([
        "parmchk2",
        "-i", mol2,
        "-f", "mol2",
        "-o", frcmod
    ])

    # STEP 3: tleap to produce prmtop & inpcrd
    tleap_input = f"""\
source leaprc.gaff
mol = loadmol2 {mol2}
loadamberparams {frcmod}
saveamberparm mol {prmtop} {inpcrd}
quit
"""
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".in") as tf:
        tf.write(tleap_input)
        tleap_file = tf.name

    print("\n3. Running tleap → prmtop & inpcrd")
    run_command(["tleap", "-f", tleap_file])
    os.remove(tleap_file)

    print("\nDone!")
    print(f"  Topology file:  {prmtop}")
    print(f"  Coordinate file: {inpcrd}")

if __name__ == "__main__":
    main()
