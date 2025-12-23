from __future__ import annotations
import argparse
import math
import sys
from typing import List, Set
from file_helpers import get_draft_dir, get_owned_path, get_downloads_folder
from binder import from_dek_file, from_txt_file, combine_binders

#!/usr/bin/env python3
"""
owned_stats.py

Compare a text list of card names to owned.dek and produce ownership stats.
Also compute hypergeometric probabilities of seeing >100 non-owned cards
in random samples of sizes 180, 270, 360 (without replacement).

Usage:
    python owned_stats.py cards.txt [--owned owned.dek] [--unique] [--threshold 100]

- cards.txt: one card name per line (duplicates allowed unless --unique).
- owned.dek: one owned card name per line (defaults to ./owned.dek).
- --unique: treat the input card list as a set (one copy per name).
- --threshold: threshold for "more than" (default 100).
- --output-file: path to write missing card names (one per line). If omitted, no file is written.
"""



def read_lines(path: str) -> List[str]:
        try:
                with open(path, encoding="utf-8") as f:
                        lines = [ln.strip() for ln in f if ln.strip() and not ln.strip().startswith("#")]
                return lines
        except FileNotFoundError:
                print(f"File not found: {path}", file=sys.stderr)
                sys.exit(2)

def hypergeom_p_more_than(N: int, K: int, n: int, threshold: int) -> float:
        """
        Probability that X > threshold where X ~ Hypergeometric(N, K, n)
        (K = number of 'successes' in population, here non-owned cards).
        Computed exactly by summing PMF terms using math.comb.
        """
        if n > N:
                raise ValueError("Sample size n cannot exceed population size N")
        # support of X is max(0, n-(N-K)) .. min(n, K)
        lo = max(0, n - (N - K))
        hi = min(n, K)
        if threshold < lo:
                return 1.0
        if threshold >= hi:
                return 0.0
        denom = math.comb(N, n)
        # sum P(X = i) for i = threshold+1 .. hi
        s = 0.0
        for i in range(threshold + 1, hi + 1):
                s += math.comb(K, i) * math.comb(N - K, n - i) / denom
        return s

def hypergeom_expected_sd(N: int, K: int, n: int):
        """
        Returns (expected_value, standard_deviation) for Hypergeometric(N,K,n)
        where 'success' count is K.
        """
        if N <= 0:
                return 0.0, 0.0
        p = K / N
        mean = n * p
        if N <= 1:
                return mean, 0.0
        var = n * p * (1 - p) * (N - n) / (N - 1)
        return mean, math.sqrt(var)

def write_names_to_file(path: str, names: Set[str]) -> None:
        try:
                with open(path, "w", encoding="utf-8") as f:
                        for name in sorted(names):
                                f.write(name + "\n")
        except OSError as e:
                print(f"Error writing to {path}: {e}", file=sys.stderr)
                sys.exit(2)

def main():
        p = argparse.ArgumentParser(description="Owned card stats + hypergeometric probabilities")
        p.add_argument("cards", help="text file with one card name per line")
        p.add_argument("--owned", default="owned.dek", help="owned.dek file (one name per line)")
        p.add_argument("--unique", action="store_true", help="treat cards file as a set (unique names)")
        p.add_argument("--threshold", type=int, default=100, help="threshold for 'more than' (default 100)")
        p.add_argument("--samples", nargs="*", type=int, default=[180,270,360], help="sample sizes to evaluate")
        p.add_argument("--output-file", "-o", default=None, help="path to write missing card names (one per line). If omitted, no file is written.")
        args = p.parse_args()

        cards_list = read_lines(args.cards)
        
        owned_card_binder = from_dek_file(get_owned_path())
        owned_list = owned_card_binder.card_names()
        owned_set: Set[str] = set(owned_list)
        print(owned_set)
        # normalize to lowercase for case-insensitive matching
        owned_set = {name.lower() for name in owned_set}
        cards_list = [name.lower() for name in cards_list]

        if args.unique:
                # treat input as set of unique card names (one copy each)
                population = list(dict.fromkeys(cards_list))  # preserves order, removes duplicates
        else:
                population = cards_list[:]  # allow duplicates (each line counts as separate card)

        N = len(population)
        if N == 0:
                print("No cards in population (cards file is empty after stripping).", file=sys.stderr)
                sys.exit(2)

        owned_count = sum(1 for name in population if name in owned_set)
        non_owned_count = N - owned_count
        pct_owned = owned_count / N * 100.0

        print(f"Population size (N): {N}")
        print(f"Owned (in owned.dek): {owned_count}")
        print(f"Not owned: {non_owned_count}")
        print(f"Percent owned: {pct_owned:.2f}%")
        print("")

        threshold = args.threshold
        for n in args.samples:
                if n > N:
                        print(f"Sample n={n}: sample size > population size (N={N}), skipping")
                        continue
                mean, sd = hypergeom_expected_sd(N, non_owned_count, n)
                try:
                        prob = hypergeom_p_more_than(N, non_owned_count, n, threshold)
                except ValueError as e:
                        print(f"Sample n={n}: error: {e}")
                        continue
                print(f"Sample n={n}: expected non-owned = {mean:.2f}, sd = {sd:.2f}")
                print(f"  P( > {threshold} non-owned ) = {prob:.6f}")
        print("")

        not_owned_set = {name for name in population if name not in owned_set}

        

        if args.output_file:
                write_names_to_file(args.output_file, not_owned_set)
                print(f"Wrote {len(not_owned_set)} names to {args.output_file}")

if __name__ == "__main__":
        main()