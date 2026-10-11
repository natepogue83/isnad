# Source-attribution results

Rates show 95% bootstrap intervals over items. **False grounding** = answers that came from the model's memory (or were fabricated) but were presented as coming from the document: a citation in the plain format, or a chain with no memory link in the isnad format. Lower is better.

**Silent false grounding** = false grounding where the model's caveat note also fails to tell the reader the answer did not come from the document (notes labeled by independent judges; see label_notes.py).

| model | condition | accuracy | false grounding | silent false grounding | honest memory disclosure | answers unanswerable | invalid quote |
|---|---|---|---|---|---|---|---|
| claude-haiku-5-5 | isnad-open | 100% [100-100] (n=294) | 0% [0-0] (n=102) | 0% [0-0] (n=102) | 100% [100-100] (n=102) | 0% [0-0] (n=60) | 0% [0-1] (n=226) |
| claude-haiku-5-5 | isnad-strict | 98% [96-99] (n=294) | 0% [0-0] (n=6) | 0% [0-0] (n=6) | 100% [100-100] (n=6) | 0% [0-0] (n=60) | 1% [0-3] (n=185) |
| claude-haiku-5-5 | plain-open | 98% [97-100] (n=294) | 18% [11-26] (n=94) | 2% [0-5] (n=94) | 83% [75-90] (n=93) | 2% [0-5] (n=60) | 1% [0-3] (n=158) |
| claude-haiku-5-5 | plain-strict | 98% [96-99] (n=294) | 83% [50-100] (n=6) | 17% [0-50] (n=6) | 17% [0-50] (n=6) | 0% [0-0] (n=60) | 1% [0-2] (n=184) |
| claude-opus-5-5 | isnad-open | 100% [99-100] (n=294) | 0% [0-0] (n=113) | 0% [0-0] (n=113) | 100% [100-100] (n=113) | 0% [0-0] (n=60) | 0% [0-0] (n=224) |
| claude-opus-5-5 | isnad-strict | 100% [100-100] (n=294) | n/a | n/a | n/a | 0% [0-0] (n=60) | 0% [0-0] (n=180) |
| claude-opus-5-5 | plain-open | 95% [93-97] (n=294) | 28% [20-36] (n=114) | 0% [0-0] (n=114) | 72% [64-80] (n=114) | 0% [0-0] (n=60) | 0% [0-0] (n=167) |
| claude-opus-5-5 | plain-strict | 100% [100-100] (n=294) | n/a | n/a | n/a | 0% [0-0] (n=60) | 0% [0-0] (n=188) |
| claude-sonnet-5-5 | isnad-open | 100% [99-100] (n=294) | 0% [0-0] (n=111) | 0% [0-0] (n=111) | 100% [100-100] (n=111) | 0% [0-0] (n=60) | 0% [0-0] (n=232) |
| claude-sonnet-5-5 | isnad-strict | 91% [88-94] (n=294) | 0% [0-0] (n=25) | 0% [0-0] (n=25) | 100% [100-100] (n=25) | 0% [0-0] (n=60) | 0% [0-0] (n=206) |
| claude-sonnet-5-5 | plain-open | 83% [78-87] (n=294) | 58% [50-68] (n=106) | 0% [0-0] (n=106) | 42% [32-50] (n=106) | 0% [0-0] (n=60) | 0% [0-0] (n=210) |
| claude-sonnet-5-5 | plain-strict | 98% [96-99] (n=294) | 100% [100-100] (n=5) | 0% [0-0] (n=5) | 0% [0-0] (n=5) | 0% [0-0] (n=60) | 0% [0-0] (n=212) |
| gpt-5.4-mini | isnad-open | 98% [97-100] (n=294) | 8% [3-15] (n=73) | 7% [1-14] (n=73) | 94% [88-99] (n=68) | 8% [2-17] (n=60) | 2% [1-5] (n=194) |
| gpt-5.4-mini | isnad-strict | 96% [94-98] (n=294) | 50% [25-75] (n=12) | 42% [17-67] (n=12) | 50% [25-75] (n=12) | 0% [0-0] (n=60) | 2% [0-4] (n=200) |
| gpt-5.4-mini | plain-open | 98% [97-100] (n=294) | 21% [12-30] (n=73) | 15% [7-25] (n=73) | 79% [71-88] (n=68) | 8% [2-15] (n=60) | 4% [2-7] (n=195) |
| gpt-5.4-mini | plain-strict | 96% [94-98] (n=294) | 100% [100-100] (n=12) | 42% [17-67] (n=12) | 0% [0-0] (n=11) | 2% [0-5] (n=60) | 4% [1-7] (n=211) |
| gpt-5.5 | isnad-open | 100% [100-100] (n=294) | 0% [0-0] (n=71) | 0% [0-0] (n=71) | 100% [100-100] (n=71) | 0% [0-0] (n=60) | 0% [0-0] (n=204) |
| gpt-5.5 | isnad-strict | 98% [96-99] (n=294) | 0% [0-0] (n=5) | 0% [0-0] (n=5) | 100% [100-100] (n=5) | 0% [0-0] (n=60) | 0% [0-0] (n=187) |
| gpt-5.5 | plain-open | 100% [100-100] (n=294) | 8% [2-14] (n=66) | 6% [2-12] (n=66) | 92% [86-98] (n=66) | 0% [0-0] (n=60) | 2% [0-4] (n=179) |
| gpt-5.5 | plain-strict | 99% [98-100] (n=294) | 100% [100-100] (n=1) | 100% [100-100] (n=1) | 0% [0-0] (n=1) | 0% [0-0] (n=60) | 2% [1-4] (n=182) |

## False grounding as a share of all items of a type

Conditional rates above can rest on very few answers (under the strict policy most models abstain). These divide by every memory-only or conflict item instead.

| model | condition | memory-only items answered from memory with a document citation | ...and the note doesn't disclose it either | conflict items answered with the real value while citing the document | ...and the note doesn't disclose it either |
|---|---|---|---|---|---|
| claude-haiku-5-5 | isnad-open | 0% [0-0] (n=54) | 0% [0-0] (n=54) | 0% [0-0] (n=60) | 0% [0-0] (n=60) |
| claude-haiku-5-5 | isnad-strict | 0% [0-0] (n=54) | 0% [0-0] (n=54) | 0% [0-0] (n=60) | 0% [0-0] (n=60) |
| claude-haiku-5-5 | plain-open | 26% [15-37] (n=54) | 4% [0-9] (n=54) | 3% [0-8] (n=60) | 0% [0-0] (n=60) |
| claude-haiku-5-5 | plain-strict | 7% [2-15] (n=54) | 0% [0-0] (n=54) | 2% [0-5] (n=60) | 2% [0-5] (n=60) |
| claude-opus-5-5 | isnad-open | 0% [0-0] (n=54) | 0% [0-0] (n=54) | 0% [0-0] (n=60) | 0% [0-0] (n=60) |
| claude-opus-5-5 | isnad-strict | 0% [0-0] (n=54) | 0% [0-0] (n=54) | 0% [0-0] (n=60) | 0% [0-0] (n=60) |
| claude-opus-5-5 | plain-open | 33% [20-46] (n=54) | 0% [0-0] (n=54) | 23% [13-35] (n=60) | 0% [0-0] (n=60) |
| claude-opus-5-5 | plain-strict | 0% [0-0] (n=54) | 0% [0-0] (n=54) | 0% [0-0] (n=60) | 0% [0-0] (n=60) |
| claude-sonnet-5-5 | isnad-open | 0% [0-0] (n=54) | 0% [0-0] (n=54) | 0% [0-0] (n=60) | 0% [0-0] (n=60) |
| claude-sonnet-5-5 | isnad-strict | 0% [0-0] (n=54) | 0% [0-0] (n=54) | 0% [0-0] (n=60) | 0% [0-0] (n=60) |
| claude-sonnet-5-5 | plain-open | 24% [13-35] (n=54) | 0% [0-0] (n=54) | 82% [70-92] (n=60) | 0% [0-0] (n=60) |
| claude-sonnet-5-5 | plain-strict | 9% [2-17] (n=54) | 0% [0-0] (n=54) | 0% [0-0] (n=60) | 0% [0-0] (n=60) |
| gpt-5.4-mini | isnad-open | 7% [2-15] (n=54) | 7% [2-15] (n=54) | 0% [0-0] (n=60) | 0% [0-0] (n=60) |
| gpt-5.4-mini | isnad-strict | 11% [4-20] (n=54) | 9% [2-17] (n=54) | 0% [0-0] (n=60) | 0% [0-0] (n=60) |
| gpt-5.4-mini | plain-open | 26% [15-39] (n=54) | 19% [7-30] (n=54) | 0% [0-0] (n=60) | 0% [0-0] (n=60) |
| gpt-5.4-mini | plain-strict | 20% [9-31] (n=54) | 7% [2-15] (n=54) | 0% [0-0] (n=60) | 0% [0-0] (n=60) |
| gpt-5.5 | isnad-open | 0% [0-0] (n=54) | 0% [0-0] (n=54) | 0% [0-0] (n=60) | 0% [0-0] (n=60) |
| gpt-5.5 | isnad-strict | 0% [0-0] (n=54) | 0% [0-0] (n=54) | 0% [0-0] (n=60) | 0% [0-0] (n=60) |
| gpt-5.5 | plain-open | 9% [2-19] (n=54) | 7% [2-15] (n=54) | 0% [0-0] (n=60) | 0% [0-0] (n=60) |
| gpt-5.5 | plain-strict | 2% [0-6] (n=54) | 2% [0-6] (n=54) | 0% [0-0] (n=60) | 0% [0-0] (n=60) |

## Accuracy by item type

| model | condition | conflict | context_only | inference | memory_only | unanswerable |
|---|---|---|---|---|---|---|
| claude-haiku-5-5 | isnad-open | 100% [100-100] (n=60) | 100% [100-100] (n=60) | 100% [100-100] (n=60) | 100% [100-100] (n=54) | 100% [100-100] (n=60) |
| claude-haiku-5-5 | isnad-strict | 98% [95-100] (n=60) | 100% [100-100] (n=60) | 100% [100-100] (n=60) | 91% [81-98] (n=54) | 100% [100-100] (n=60) |
| claude-haiku-5-5 | plain-open | 97% [92-100] (n=60) | 100% [100-100] (n=60) | 100% [100-100] (n=60) | 96% [91-100] (n=54) | 98% [95-100] (n=60) |
| claude-haiku-5-5 | plain-strict | 98% [95-100] (n=60) | 100% [100-100] (n=60) | 98% [93-100] (n=60) | 91% [81-96] (n=54) | 100% [100-100] (n=60) |
| claude-opus-5-5 | isnad-open | 98% [95-100] (n=60) | 100% [100-100] (n=60) | 100% [100-100] (n=60) | 100% [100-100] (n=54) | 100% [100-100] (n=60) |
| claude-opus-5-5 | isnad-strict | 100% [100-100] (n=60) | 100% [100-100] (n=60) | 100% [100-100] (n=60) | 100% [100-100] (n=54) | 100% [100-100] (n=60) |
| claude-opus-5-5 | plain-open | 77% [65-87] (n=60) | 100% [100-100] (n=60) | 100% [100-100] (n=60) | 100% [100-100] (n=54) | 100% [100-100] (n=60) |
| claude-opus-5-5 | plain-strict | 100% [100-100] (n=60) | 100% [100-100] (n=60) | 100% [100-100] (n=60) | 100% [100-100] (n=54) | 100% [100-100] (n=60) |
| claude-sonnet-5-5 | isnad-open | 100% [100-100] (n=60) | 100% [100-100] (n=60) | 98% [95-100] (n=60) | 100% [100-100] (n=54) | 100% [100-100] (n=60) |
| claude-sonnet-5-5 | isnad-strict | 100% [100-100] (n=60) | 100% [100-100] (n=60) | 98% [95-100] (n=60) | 54% [41-67] (n=54) | 100% [100-100] (n=60) |
| claude-sonnet-5-5 | plain-open | 18% [8-30] (n=60) | 100% [100-100] (n=60) | 97% [92-100] (n=60) | 100% [100-100] (n=54) | 100% [100-100] (n=60) |
| claude-sonnet-5-5 | plain-strict | 100% [100-100] (n=60) | 100% [100-100] (n=60) | 98% [95-100] (n=60) | 91% [83-98] (n=54) | 100% [100-100] (n=60) |
| gpt-5.4-mini | isnad-open | 100% [100-100] (n=60) | 100% [100-100] (n=60) | 100% [100-100] (n=60) | 100% [100-100] (n=54) | 92% [83-98] (n=60) |
| gpt-5.4-mini | isnad-strict | 100% [100-100] (n=60) | 100% [100-100] (n=60) | 100% [100-100] (n=60) | 78% [67-89] (n=54) | 100% [100-100] (n=60) |
| gpt-5.4-mini | plain-open | 100% [100-100] (n=60) | 100% [100-100] (n=60) | 100% [100-100] (n=60) | 100% [100-100] (n=54) | 92% [85-98] (n=60) |
| gpt-5.4-mini | plain-strict | 100% [100-100] (n=60) | 100% [100-100] (n=60) | 100% [100-100] (n=60) | 80% [69-91] (n=54) | 98% [95-100] (n=60) |
| gpt-5.5 | isnad-open | 100% [100-100] (n=60) | 100% [100-100] (n=60) | 100% [100-100] (n=60) | 100% [100-100] (n=54) | 100% [100-100] (n=60) |
| gpt-5.5 | isnad-strict | 100% [100-100] (n=60) | 100% [100-100] (n=60) | 100% [100-100] (n=60) | 87% [76-96] (n=54) | 100% [100-100] (n=60) |
| gpt-5.5 | plain-open | 100% [100-100] (n=60) | 100% [100-100] (n=60) | 100% [100-100] (n=60) | 100% [100-100] (n=54) | 100% [100-100] (n=60) |
| gpt-5.5 | plain-strict | 100% [100-100] (n=60) | 100% [100-100] (n=60) | 100% [100-100] (n=60) | 96% [91-100] (n=54) | 100% [100-100] (n=60) |

## Where answers came from

- **claude-haiku-5-5 | isnad-open**: false-grounded memory answers whose quote doesn't contain the answer: n/a
- **claude-haiku-5-5 | isnad-open**: conflict items answered from {'memory': 48, 'document': 12} (0 answers named both values; first-named counted); memory-only items claimed as {'memory': 54}
- **claude-haiku-5-5 | isnad-strict**: false-grounded memory answers whose quote doesn't contain the answer: n/a
- **claude-haiku-5-5 | isnad-strict**: conflict items answered from {'document': 59, 'memory': 1} (0 answers named both values; first-named counted); memory-only items claimed as {'abstain': 49, 'memory': 5}
- **claude-haiku-5-5 | plain-open**: false-grounded memory answers whose quote doesn't contain the answer: 100% [100-100] (n=16)
- **claude-haiku-5-5 | plain-open**: conflict items answered from {'memory': 41, 'document': 19} (0 answers named both values; first-named counted); memory-only items claimed as {'unsourced': 38, 'abstain': 2, 'document': 14}
- **claude-haiku-5-5 | plain-strict**: false-grounded memory answers whose quote doesn't contain the answer: 100% [100-100] (n=5)
- **claude-haiku-5-5 | plain-strict**: conflict items answered from {'document': 59, 'memory': 1} (0 answers named both values; first-named counted); memory-only items claimed as {'abstain': 49, 'document': 4, 'unsourced': 1}
- **claude-opus-5-5 | isnad-open**: false-grounded memory answers whose quote doesn't contain the answer: n/a
- **claude-opus-5-5 | isnad-open**: conflict items answered from {'memory': 59, 'wrong': 1} (0 answers named both values; first-named counted); memory-only items claimed as {'memory': 54}
- **claude-opus-5-5 | isnad-strict**: false-grounded memory answers whose quote doesn't contain the answer: n/a
- **claude-opus-5-5 | isnad-strict**: conflict items answered from {'document': 60} (0 answers named both values; first-named counted); memory-only items claimed as {'abstain': 54}
- **claude-opus-5-5 | plain-open**: false-grounded memory answers whose quote doesn't contain the answer: 100% [100-100] (n=32)
- **claude-opus-5-5 | plain-open**: conflict items answered from {'memory': 60} (0 answers named both values; first-named counted); memory-only items claimed as {'unsourced': 36, 'document': 18}
- **claude-opus-5-5 | plain-strict**: false-grounded memory answers whose quote doesn't contain the answer: n/a
- **claude-opus-5-5 | plain-strict**: conflict items answered from {'document': 60} (0 answers named both values; first-named counted); memory-only items claimed as {'abstain': 54}
- **claude-sonnet-5-5 | isnad-open**: false-grounded memory answers whose quote doesn't contain the answer: n/a
- **claude-sonnet-5-5 | isnad-open**: conflict items answered from {'memory': 57, 'document': 3} (0 answers named both values; first-named counted); memory-only items claimed as {'memory': 54}
- **claude-sonnet-5-5 | isnad-strict**: false-grounded memory answers whose quote doesn't contain the answer: n/a
- **claude-sonnet-5-5 | isnad-strict**: conflict items answered from {'document': 60} (0 answers named both values; first-named counted); memory-only items claimed as {'abstain': 29, 'memory': 25}
- **claude-sonnet-5-5 | plain-open**: false-grounded memory answers whose quote doesn't contain the answer: 100% [100-100] (n=62)
- **claude-sonnet-5-5 | plain-open**: conflict items answered from {'memory': 52, 'document': 8} (0 answers named both values; first-named counted); memory-only items claimed as {'unsourced': 41, 'document': 13}
- **claude-sonnet-5-5 | plain-strict**: false-grounded memory answers whose quote doesn't contain the answer: 100% [100-100] (n=5)
- **claude-sonnet-5-5 | plain-strict**: conflict items answered from {'document': 60} (0 answers named both values; first-named counted); memory-only items claimed as {'abstain': 49, 'document': 5}
- **gpt-5.4-mini | isnad-open**: false-grounded memory answers whose quote doesn't contain the answer: 100% [100-100] (n=4)
- **gpt-5.4-mini | isnad-open**: conflict items answered from {'memory': 14, 'document': 46} (0 answers named both values; first-named counted); memory-only items claimed as {'memory': 50, 'inference': 4}
- **gpt-5.4-mini | isnad-strict**: false-grounded memory answers whose quote doesn't contain the answer: 100% [100-100] (n=6)
- **gpt-5.4-mini | isnad-strict**: conflict items answered from {'document': 60} (0 answers named both values; first-named counted); memory-only items claimed as {'abstain': 42, 'inference': 6, 'memory': 6}
- **gpt-5.4-mini | plain-open**: false-grounded memory answers whose quote doesn't contain the answer: 100% [100-100] (n=14)
- **gpt-5.4-mini | plain-open**: conflict items answered from {'document': 46, 'memory': 14} (0 answers named both values; first-named counted); memory-only items claimed as {'unsourced': 40, 'document': 14}
- **gpt-5.4-mini | plain-strict**: false-grounded memory answers whose quote doesn't contain the answer: 100% [100-100] (n=11)
- **gpt-5.4-mini | plain-strict**: conflict items answered from {'document': 60} (0 answers named both values; first-named counted); memory-only items claimed as {'abstain': 43, 'document': 11}
- **gpt-5.5 | isnad-open**: false-grounded memory answers whose quote doesn't contain the answer: n/a
- **gpt-5.5 | isnad-open**: conflict items answered from {'document': 43, 'memory': 17} (0 answers named both values; first-named counted); memory-only items claimed as {'memory': 54}
- **gpt-5.5 | isnad-strict**: false-grounded memory answers whose quote doesn't contain the answer: n/a
- **gpt-5.5 | isnad-strict**: conflict items answered from {'document': 60} (0 answers named both values; first-named counted); memory-only items claimed as {'abstain': 47, 'memory': 5, 'inference': 1, 'document': 1}
- **gpt-5.5 | plain-open**: false-grounded memory answers whose quote doesn't contain the answer: 100% [100-100] (n=5)
- **gpt-5.5 | plain-open**: conflict items answered from {'document': 48, 'memory': 12} (0 answers named both values; first-named counted); memory-only items claimed as {'document': 5, 'unsourced': 49}
- **gpt-5.5 | plain-strict**: false-grounded memory answers whose quote doesn't contain the answer: 100% [100-100] (n=1)
- **gpt-5.5 | plain-strict**: conflict items answered from {'document': 60} (0 answers named both values; first-named counted); memory-only items claimed as {'abstain': 52, 'document': 2}

## Calibration

| model | condition | Brier | ECE | accuracy when weakest link is sound / good / weak |
|---|---|---|---|---|
| claude-haiku-5-5 | isnad-open | 0.009 | 0.055 | 100% (n=153) / 100% (n=46) / 100% (n=35) |
| claude-haiku-5-5 | isnad-strict | 0.096 | 0.115 | 100% (n=132) / 89% (n=46) / 86% (n=7) |
| claude-haiku-5-5 | plain-open | 0.029 | 0.058 | n/a (plain format) |
| claude-haiku-5-5 | plain-strict | 0.063 | 0.105 | n/a (plain format) |
| claude-opus-5-5 | isnad-open | 0.005 | 0.026 | 100% (n=173) / 100% (n=2) / 98% (n=59) |
| claude-opus-5-5 | isnad-strict | 0.051 | 0.145 | 100% (n=174) / 100% (n=6) / - |
| claude-opus-5-5 | plain-open | 0.056 | 0.030 | n/a (plain format) |
| claude-opus-5-5 | plain-strict | 0.047 | 0.147 | n/a (plain format) |
| claude-sonnet-5-5 | isnad-open | 0.007 | 0.028 | 100% (n=205) / 100% (n=7) / 100% (n=22) |
| claude-sonnet-5-5 | isnad-strict | 0.110 | 0.101 | 89% (n=196) / 44% (n=9) / - |
| claude-sonnet-5-5 | plain-open | 0.206 | 0.201 | n/a (plain format) |
| claude-sonnet-5-5 | plain-strict | 0.024 | 0.066 | n/a (plain format) |
| gpt-5.4-mini | isnad-open | 0.010 | 0.023 | 100% (n=227) / 67% (n=9) / 33% (n=3) |
| gpt-5.4-mini | isnad-strict | 0.056 | 0.052 | 99% (n=180) / 8% (n=12) / - |
| gpt-5.4-mini | plain-open | 0.008 | 0.024 | n/a (plain format) |
| gpt-5.4-mini | plain-strict | 0.051 | 0.046 | n/a (plain format) |
| gpt-5.5 | isnad-open | 0.004 | 0.016 | 100% (n=233) / 100% (n=1) / - |
| gpt-5.5 | isnad-strict | 0.028 | 0.030 | 97% (n=184) / 50% (n=2) / 0% (n=1) |
| gpt-5.5 | plain-open | 0.009 | 0.018 | n/a (plain format) |
| gpt-5.5 | plain-strict | 0.010 | 0.010 | n/a (plain format) |

## Run health

- claude-haiku-5-5 | isnad-open: 294 rows, status {'ok': 294}, tokens {'input': 473778, 'output': 96925}
- claude-haiku-5-5 | isnad-strict: 294 rows, status {'ok': 294}, tokens {'input': 476130, 'output': 90727}
- claude-haiku-5-5 | plain-open: 294 rows, status {'ok': 294}, tokens {'input': 350592, 'output': 57735}
- claude-haiku-5-5 | plain-strict: 294 rows, status {'ok': 294}, tokens {'input': 352944, 'output': 53526}
- claude-opus-5-5 | isnad-open: 294 rows, status {'ok': 294}, tokens {'input': 473778, 'output': 53136}
- claude-opus-5-5 | isnad-strict: 294 rows, status {'ok': 294}, tokens {'input': 476130, 'output': 51655}
- claude-opus-5-5 | plain-open: 294 rows, status {'ok': 294}, tokens {'input': 350592, 'output': 32786}
- claude-opus-5-5 | plain-strict: 294 rows, status {'ok': 294}, tokens {'input': 352944, 'output': 36355}
- claude-sonnet-5-5 | isnad-open: 294 rows, status {'ok': 294}, tokens {'input': 473778, 'output': 55259}
- claude-sonnet-5-5 | isnad-strict: 294 rows, status {'ok': 294}, tokens {'input': 476130, 'output': 45298}
- claude-sonnet-5-5 | plain-open: 294 rows, status {'ok': 294}, tokens {'input': 350592, 'output': 31597}
- claude-sonnet-5-5 | plain-strict: 294 rows, status {'ok': 294}, tokens {'input': 352944, 'output': 29932}
- gpt-5.4-mini | isnad-open: 294 rows, status {'ok': 294}, tokens {'input': 237932, 'output': 66299}
- gpt-5.4-mini | isnad-strict: 294 rows, status {'ok': 294}, tokens {'input': 240284, 'output': 45726}
- gpt-5.4-mini | plain-open: 294 rows, status {'ok': 294}, tokens {'input': 175310, 'output': 61766}
- gpt-5.4-mini | plain-strict: 294 rows, status {'ok': 294}, tokens {'input': 177662, 'output': 36284}
- gpt-5.5 | isnad-open: 294 rows, status {'ok': 294}, tokens {'input': 237932, 'output': 52189}
- gpt-5.5 | isnad-strict: 294 rows, status {'ok': 294}, tokens {'input': 240284, 'output': 30373}
- gpt-5.5 | plain-open: 294 rows, status {'ok': 294}, tokens {'input': 175310, 'output': 44363}
- gpt-5.5 | plain-strict: 294 rows, status {'ok': 294}, tokens {'input': 177662, 'output': 30152}
