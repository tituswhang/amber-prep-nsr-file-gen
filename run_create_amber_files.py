#!/usr/bin/env python
import os
import subprocess
import sys

def main():
    # 1) locate create_amber_files.py
    cs = input("Enter the full or relative path to create_amber_files.py (press Enter if it's in the current directory): ").strip()
    script = os.path.abspath(cs) if cs else os.path.join(os.getcwd(), "create_amber_files.py")
    if not os.path.isfile(script):
        print("Error: cannot find create_amber_files.py at", script)
        sys.exit(1)

    # 2) locate input file
    inp = input("Enter the full or relative path to the input (.pdb or .mol2): ").strip()
    infile = os.path.abspath(inp)
    if not os.path.isfile(infile):
        print("Error: cannot find input file at", infile)
        sys.exit(1)
    _, ext = os.path.splitext(infile.lower())

    # 3) optional prmtop/inpcrd names
    prmtop = input("Enter desired name for output topology (.prmtop) file (press Enter to use default): ").strip()
    inpcrd = input("Enter desired name for output coordinate (.inpcrd) file (press Enter to use default): ").strip()

    # Automatically append extensions if missing
    if prmtop and not prmtop.lower().endswith('.prmtop'):
        prmtop += '.prmtop'
    if inpcrd and not inpcrd.lower().endswith('.inpcrd'):
        inpcrd += '.inpcrd'

    # 4) charge options: default for PDB, interactive for others
    if ext == ".pdb":
        print("\nInput is PDB: defaulting to AM1-BCC charges (-c bcc -s 2).")
        ac_opts = "-c bcc -s 2"
    else:
        opts = {
            "1": "-c resp",  "2": "-c bcc",   "3": "-c cm1", "4": "-c cm2",
            "5": "-c esp",   "6": "-c mul",   "7": "-c gas",  "8": "-c abcg2",
            "9": "-c rc",   "10": "-c wc",  "11": "-c dc"
        }
        desc = {
            "1": "RESP charges (requires .gout/.esp/.dat)",
            "2": "AM1-BCC (default)", "3": "CM1",      "4": "CM2",
            "5": "ESP (Kollman)",     "6": "Mulliken","7": "Gasteiger",
            "8": "ABCG2",             "9": "Read charge",
            "10": "Write charge",     "11": "Delete charge"
        }
        print("\nCharge options:")
        for k in sorted(opts, key=int):
            print(f"{k}. {desc[k]}: {opts[k]}")
        sel = input("Enter the numbers for the charge options you want (press Enter to use default -c bcc): ").strip().split()
        if not sel:
            ac_opts = "-c bcc"
        else:
            chosen = [opts.get(x) for x in sel if x in opts]
            ac_opts = " ".join(chosen) if chosen else "-c bcc"
        ac_opts += " -s 2"

        # RESP only valid for quantum outputs
        if "resp" in ac_opts and ext in [".mol2", ".pdb"]:
            print("\nError: RESP requires Gaussian (.gout/.esp) or GAMESS (.dat) input.")
            sys.exit(1)

    # 5) assemble command
    cmd = [sys.executable, script, infile]
    if prmtop:
        cmd += ["--prmtop", prmtop]
    if inpcrd:
        cmd += ["--inpcrd", inpcrd]
    cmd += ["--ac_opts", ac_opts]

    # 6) run
    print("\nRunning:", " ".join(cmd))
    rc = subprocess.call(cmd)
    if rc != 0:
        print("create_amber_files.py failed with exit code", rc)
        sys.exit(rc)
    else:
        print("Success")

if __name__ == "__main__":
    main()

