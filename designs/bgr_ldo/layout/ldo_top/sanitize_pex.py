#!/usr/bin/env python3
r"""
sanitize_pex.py — PEX Netlist Node Name Sanitizer for Sky130 Magic Netlists

Rules:
1. Replaces dot ('.') characters with underscore ('_') in node names for X, R, C element lines.
2. Preserves tokens matching any of the following conditions:
   - Contains '=' (Device parameters like w=10, l=0.15)
   - Matches numeric pattern with optional unit suffix: ^[+-]?[0-9]*\.?[0-9]+([eE][+-]?[0-9]+)?[afpnumkKMGT]?$
   - Starts with 'sky130_fd_pr__' and contains no dots (Model names)
3. Strips 'u' / 'p' suffixes from MOS parameters (w, l, ad, as, pd, ps) because Sky130 PDK subcircuits 
   already multiply internal scaling factors (e.g. w*1e-6, ad*1e-12).
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
PARAM_UNIT_REGEX = re.compile(r'^(w|l|ad|as|pd|ps)=([0-9]*\.?[0-9]+([eE][+-]?[0-9]+)?)[upUP]$', re.IGNORECASE)

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

def clean_param_token(token: str) -> str:
    m = PARAM_UNIT_REGEX.match(token)
    if m:
        return f"{m.group(1)}={m.group(2)}"
    return token

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

    for idx, token in enumerate(tokens):
        if "=" in token:
            cleaned = clean_param_token(token)
            if cleaned != token:
                modified = True
            new_tokens.append(cleaned)
        elif idx == 0:
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
                new_token = token.replace(".", "_")
                if new_token != token:
                    modified = True
                    if is_numeric_token(token):
                        value_mutated = True
                new_tokens.append(new_token)

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

def main():
    parser = argparse.ArgumentParser(description="PEX Netlist Node Name Sanitizer")
    parser.add_argument("input_path", nargs="?", default="ldo_top_pex.spice", help="Path to input PEX spice netlist")
    parser.add_argument("output_path", nargs="?", default="ldo_top_pex_rc_safe.spice", help="Path to output sanitized PEX spice netlist")

    args = parser.parse_args()
    process_file(args.input_path, args.output_path)

if __name__ == "__main__":
    main()
