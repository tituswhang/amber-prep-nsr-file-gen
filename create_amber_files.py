# create_amber_files.py
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
            "from a PDB/MOL2 or Gaussian/GAMESS output using antechamber (if needed), parmchk2, and tleap."
        )
    )
    parser.add_argument("input_file", help="Input: .pdb, .mol2, .gout/.esp (Gaussian), or .dat (GAMESS)")
    parser.add_argument("--prmtop", help="Output topology file (default: <base>.prmtop)")
    parser.add_argument("--inpcrd", help="Output coordinate file (default: <base>.inpcrd)")
    parser.add_argument(
        "--ac_opts",
        default="",
        help="Extra options for antechamber (e.g. '-c bcc -s 2')."
    )
    args = parser.parse_args()

    inf = args.input_file
    base, ext = os.path.splitext(os.path.basename(inf))
    ext = ext.lower()

    # output names
    prmtop = args.prmtop if args.prmtop else f"{base}.prmtop"
    inpcrd = args.inpcrd if args.inpcrd else f"{base}.inpcrd"
    frcmod = f"{base}.frcmod"
    mol2   = f"{base}.mol2"

    # helper to see if RESP was requested
    want_resp = ("-c" in args.ac_opts and "resp" in args.ac_opts.split())

    # STEP 1: generate MOL2 if needed
    if ext == ".pdb":
        if want_resp:
            print("Error: RESP charges cannot be generated directly from a PDB file.")
            print("You must supply a Gaussian ESP (.esp) or output (.gout) or GAMESS .dat file.")
            sys.exit(1)
        print("\n1. Converting PDB → MOL2 with AM1‑BCC (or other) via antechamber...")
        cmd = ["antechamber", "-i", inf, "-fi", "pdb", "-o", mol2, "-fo", "mol2"]
        if args.ac_opts:
            cmd += args.ac_opts.split()
        run_command(cmd)

    elif ext == ".mol2":
        if want_resp:
            print("Error: RESP charges cannot be generated from a raw MOL2 file.")
            print("You must supply a Gaussian ESP (.esp) or output (.gout) or GAMESS .dat file.")
            sys.exit(1)
        mol2 = inf
        print(f"\nInput is MOL2 → skipping antechamber, using {mol2}")

    elif ext in (".gout", ".esp", ".dat"):
        # user supplied quantum chemistry output → RESP path
        fmt_map = {".gout":"gout", ".esp":"gesp", ".dat":"gamess"}
        fi_flag = fmt_map[ext]
        print(f"\n1. Generating RESP‐charged MOL2 from {ext[1:]} via antechamber...")
        cmd = [
            "antechamber",
            "-i", inf,
            "-fi", fi_flag,
            "-o", mol2,
            "-fo", "mol2"
        ]
        # ensure RESP is in the opts
        if not want_resp:
            print("Warning: no `-c resp` in options; request will default to whatever charge method you gave.")
        cmd += args.ac_opts.split()
        run_command(cmd)

    else:
        print("Error: Unsupported extension. Provide a .pdb, .mol2, .gout/.esp, or .dat file.")
        sys.exit(1)

    # STEP 2: parmchk2 → frcmod
    print("\n2. Generating frcmod with parmchk2...")
    run_command(["parmchk2", "-i", mol2, "-f", "mol2", "-o", frcmod])

    # STEP 3: tleap → prmtop + inpcrd
    tleap_in = f"""
source leaprc.gaff
mol = loadmol2 {mol2}
loadamberparams {frcmod}
saveamberparm mol {prmtop} {inpcrd}
quit
"""
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".in") as tf:
        tf.write(tleap_in)
        tfin = tf.name

    print("\n3. Running tleap → prmtop & inpcrd")
    run_command(["tleap", "-f", tfin])
    os.remove(tfin)

    print("\nDone")
    print(f"  Topology:  {prmtop}")
    print(f"  Coordinates:{inpcrd}")

if __name__ == "__main__":
    main()
