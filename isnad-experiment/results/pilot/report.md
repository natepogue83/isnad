# Source-attribution results

Rates show 95% bootstrap intervals over items. **False grounding** = answers that came from the model's memory (or were fabricated) but were presented as coming from the document: a citation in the plain format, or a chain with no memory link in the isnad format. Lower is better.

| model | condition | accuracy | false grounding | honest memory disclosure | answers unanswerable | invalid quote |
|---|---|---|---|---|---|---|
| pilot | isnad-open | 100% [100-100] (n=20) | 0% [0-0] (n=8) | 100% [100-100] (n=8) | 0% [0-0] (n=4) | 0% [0-0] (n=20) |
| pilot | isnad-strict | 100% [100-100] (n=20) | n/a | n/a | 0% [0-0] (n=4) | 0% [0-0] (n=20) |
| pilot | plain-open | 100% [100-100] (n=20) | 12% [0-38] (n=8) | 88% [62-100] (n=8) | 0% [0-0] (n=4) | 0% [0-0] (n=10) |
| pilot | plain-strict | 100% [100-100] (n=20) | n/a | n/a | 0% [0-0] (n=4) | 0% [0-0] (n=13) |

## Accuracy by item type

| model | condition | conflict | context_only | inference | memory_only | unanswerable |
|---|---|---|---|---|---|---|
| pilot | isnad-open | 100% [100-100] (n=4) | 100% [100-100] (n=4) | 100% [100-100] (n=4) | 100% [100-100] (n=4) | 100% [100-100] (n=4) |
| pilot | isnad-strict | 100% [100-100] (n=4) | 100% [100-100] (n=4) | 100% [100-100] (n=4) | 100% [100-100] (n=4) | 100% [100-100] (n=4) |
| pilot | plain-open | 100% [100-100] (n=4) | 100% [100-100] (n=4) | 100% [100-100] (n=4) | 100% [100-100] (n=4) | 100% [100-100] (n=4) |
| pilot | plain-strict | 100% [100-100] (n=4) | 100% [100-100] (n=4) | 100% [100-100] (n=4) | 100% [100-100] (n=4) | 100% [100-100] (n=4) |

## Where answers came from

- **pilot | isnad-open**: false-grounded memory answers whose quote doesn't contain the answer: n/a
- **pilot | isnad-open**: conflict items answered from {'memory': 4} (4 answers named both values; first-named counted); memory-only items claimed as {'memory': 4}
- **pilot | isnad-strict**: false-grounded memory answers whose quote doesn't contain the answer: n/a
- **pilot | isnad-strict**: conflict items answered from {'document': 4} (4 answers named both values; first-named counted); memory-only items claimed as {'abstain': 4}
- **pilot | plain-open**: false-grounded memory answers whose quote doesn't contain the answer: 100% [100-100] (n=1)
- **pilot | plain-open**: conflict items answered from {'memory': 4} (4 answers named both values; first-named counted); memory-only items claimed as {'unsourced': 3, 'document': 1}
- **pilot | plain-strict**: false-grounded memory answers whose quote doesn't contain the answer: n/a
- **pilot | plain-strict**: conflict items answered from {'document': 4} (3 answers named both values; first-named counted); memory-only items claimed as {'abstain': 4}

## Calibration

| model | condition | Brier | ECE | accuracy when weakest link is sound / good / weak |
|---|---|---|---|---|
| pilot | isnad-open | 0.001 | 0.031 | 100% (n=13) / 100% (n=1) / 100% (n=2) |
| pilot | isnad-strict | 0.028 | 0.118 | 100% (n=10) / 100% (n=2) / - |
| pilot | plain-open | 0.002 | 0.037 | n/a (plain format) |
| pilot | plain-strict | 0.009 | 0.076 | n/a (plain format) |

## Run health

- pilot | isnad-open: 20 rows, status {'ok': 20}, tokens {'input': 0, 'output': 0}
- pilot | isnad-strict: 20 rows, status {'ok': 20}, tokens {'input': 0, 'output': 0}
- pilot | plain-open: 20 rows, status {'ok': 20}, tokens {'input': 0, 'output': 0}
- pilot | plain-strict: 20 rows, status {'ok': 20}, tokens {'input': 0, 'output': 0}
