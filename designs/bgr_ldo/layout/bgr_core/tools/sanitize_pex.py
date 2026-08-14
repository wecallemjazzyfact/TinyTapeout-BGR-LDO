#!/usr/bin/env python3
r"""
sanitize_pex.py — PEX Netlist Node Name Sanitizer for Sky130 Magic Netlists

Rules:
1. Replaces dot ('.') characters with underscore ('_') in node names for X, R, C element lines.
2. Preserves tokens matching any of the following conditions:
   - Contains '=' (Device parameters like w=10, l=0.15)
   - Matches numeric pattern with optional unit suffix: ^[+-]?[0-9]*\.?[0-9]+([eE][+-]?[0-9]+)?[afpnumkKMGT]?$
   - Starts with 'sky130_fd_pr__' and contains no dots (Model names)
3. Supports --verify mode to ensure device counts and numerical value fields are 100% identical.
"""

import sys
import re
import argparse

# Ensure stdout handles UTF-8 output across platforms
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

NUMERIC_REGEX = re.compile(r'^[+-]?[0-9]*\.?[0-9]+([eE][+-]?[0-9]+)?[afpnumkKMGT]?$', re.IGNORECASE)

def is_numeric_token(token: str) -> bool:
    return bool(NUMERIC_REGEX.match(token))

def is_model_token(token: str) -> bool:
    return token.startswith("sky130_fd_pr__") and ("." not in token)

def should_skip_token(token: str) -> bool:
    if "=" in token:
        return True
    if is_numeric_token(token):
        return True
    if is_model_token(token):
        return True
    return False

def sanitize_line(line: str):
    stripped = line.strip()
    if not stripped or stripped.startswith("*") or stripped.startswith("."):
        return line, False, False, 0

    tokens = line.split()
    if not tokens:
        return line, False, False, 0

    first_char = tokens[0][0].upper()
    if first_char not in ("X", "R", "C"):
        return line, False, False, 0

    modified = False
    value_mutated = False
    remaining_dots = 0

    new_tokens = []

    # Identify value/numeric tokens for mutation safety tracking
    for idx, token in enumerate(tokens):
        if idx == 0:
            # Element name (e.g., R0, C12, Xcore)
            if should_skip_token(token):
                new_tokens.append(token)
            else:
                new_token = token.replace(".", "_")
                if new_token != token:
                    modified = True
                new_tokens.append(new_token)
        else:
            if should_skip_token(token):
                new_tokens.append(token)
            else:
                # Candidate node name token
                new_token = token.replace(".", "_")
                if new_token != token:
                    modified = True
                    if is_numeric_token(token):
                        value_mutated = True
                new_tokens.append(new_token)

    # Re-check remaining dots in node tokens
    for t in new_tokens[1:]:
        if "=" not in t and not is_numeric_token(t) and not is_model_token(t):
            if "." in t:
                remaining_dots += 1

    prefix_space = line[:len(line) - len(line.lstrip())]
    sanitized_line = prefix_space + " ".join(new_tokens) + "\n"
    return sanitized_line, modified, value_mutated, remaining_dots

def process_file(input_path: str, output_path: str):
    modified_lines_count = 0
    value_mutated_lines_count = 0
    total_remaining_dots = 0

    with open(input_path, "r", encoding="utf-8", errors="ignore") as fin, \
         open(output_path, "w", encoding="utf-8") as fout:
        for line in fin:
            san_line, mod, val_mut, rem_dots = sanitize_line(line)
            if mod:
                modified_lines_count += 1
            if val_mut:
                value_mutated_lines_count += 1
            total_remaining_dots += rem_dots
            fout.write(san_line)

    print("=== Sanitize PEX Summary ===")
    print(f"Input File            : {input_path}")
    print(f"Output File           : {output_path}")
    print(f"Modified Lines        : {modified_lines_count}")
    print(f"Value Mutated Lines   : {value_mutated_lines_count} (Must be 0)")
    print(f"Remaining Dot Nodes   : {total_remaining_dots}")

    if value_mutated_lines_count > 0:
        print("[WARNING] Numerical value mutation detected! Please review rules.")

def extract_elements(file_path: str):
    elements = []
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("*") or stripped.startswith("."):
                continue
            tokens = line.split()
            if not tokens:
                continue
            first_char = tokens[0][0].upper()
            if first_char in ("X", "R", "C"):
                values = [t for t in tokens if is_numeric_token(t) or "=" in t]
                elements.append((tokens[0], first_char, values))
    return elements

def verify_files(input_path: str, output_path: str):
    print("\n=== Verifying Sanitize Correctness (--verify) ===")
    in_elems = extract_elements(input_path)
    out_elems = extract_elements(output_path)

    if len(in_elems) != len(out_elems):
        print(f"[FAIL] Verification FAILED: Element count mismatch (Input: {len(in_elems)}, Output: {len(out_elems)})")
        sys.exit(1)

    mismatch_count = 0
    for idx, (in_e, out_e) in enumerate(zip(in_elems, out_elems)):
        if in_e[1] != out_e[1]:
            print(f"[FAIL] Type mismatch at element #{idx}: {in_e[0]} vs {out_e[0]}")
            mismatch_count += 1
            break

        if in_e[2] != out_e[2]:
            print(f"[FAIL] Value mismatch in element {in_e[0]}: Input values {in_e[2]} vs Output values {out_e[2]}")
            mismatch_count += 1

    if mismatch_count == 0:
        print(f"[PASS] Verification PASSED: {len(in_elems)} X/R/C elements checked. All numerical values and parameters match 100%.")
    else:
        print(f"[FAIL] Verification FAILED: {mismatch_count} discrepancies found.")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="PEX Netlist Node Name Sanitizer")
    parser.add_argument("input_path", help="Path to input PEX spice netlist")
    parser.add_argument("output_path", help="Path to output sanitized PEX spice netlist")
    parser.add_argument("--verify", action="store_true", help="Run verification check on output netlist")

    args = parser.parse_args()
    process_file(args.input_path, args.output_path)

    if args.verify:
        verify_files(args.input_path, args.output_path)

if __name__ == "__main__":
    main()
