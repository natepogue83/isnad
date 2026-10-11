# Independent per-item review

All 294 kept items were re-checked by independent reviewers (one per batch of 12, told to redo arithmetic, check for leaks and paraphrase hints, and check alias completeness). 291 passed. Three conflict items were flagged for documents that hinted at the real value (a famous siege date near the Bosphorus, Napoleon's jailer Hudson Lowe, and Charlotte Brontë's pseudonym "Currer Bell"); those hints were removed from the raw batches and the dataset rebuilt. Manual alias additions: "Shihuangdi"/"Shi Huangdi" (first Qin emperor) and "Lean" (director of Lawrence of Arabia).

Note: eight famous facts appear in both a memory_only item and a conflict item (e.g. the author of Moby-Dick). Every item is sent in its own isolated call, so this does not leak between items, but per-type rates are not fully independent samples of facts.
