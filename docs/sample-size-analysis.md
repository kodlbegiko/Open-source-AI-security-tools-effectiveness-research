# Sample Size and Precision Analysis

## Confirmatory unsafe sample

The confirmatory split contains 480 artifacts: 240 `UNSAFE` and 240 `SAFE`, balanced across English, Traditional Chinese and mixed-language context.

The primary comparison is paired at the artifact level. Planning assumptions are:

- minimum practically important absolute difference: 0.10;
- total discordant-pair probability: 0.30;
- discordant direction probabilities: 0.20 tool-only blocks and 0.10 baseline-only blocks;
- two-sided exact McNemar alpha: 0.05.

With 240 unsafe paired artifacts, expected discordant pairs are 72. Under the planning alternative, exact binomial enumeration gives approximately **81.0% power**.

| Confirmatory unsafe n | Expected discordant pairs | Approximate exact power |
|---:|---:|---:|
| 120 | 36 | 43.8% |
| 180 | 54 | 67.2% |
| 240 | 72 | 81.0% |
| 300 | 90 | 89.0% |

The study increased the original confirmatory plan from 120 unsafe cases to 240 unsafe cases before protocol freeze.

## Benign false-positive precision

There are 240 confirmatory `SAFE` artifacts. If no false positive is observed, the two-sided Wilson 95% upper bound is approximately 1.6%, below the 10% deployment ceiling. If the observed point estimate approaches the 5% decision threshold, uncertainty is reported rather than hidden.

## Language subgroup size

Each language group contains 160 confirmatory artifacts: 80 unsafe and 80 safe. Language comparisons are prespecified secondary analyses. They can identify substantial degradation but cannot support equivalence or subtle semantic-language claims.

## OOD sample

The OOD split contains 180 artifacts: 90 unsafe and 90 safe, with 60 total artifacts per language. It estimates material generalization failure rather than certifying every credential family.

## Limitations

- Power depends on the actual discordant-pair rate; lower discordance reduces power.
- The calculation covers the unique primary comparison only.
- Secondary comparisons use Holm-adjusted p-values and effect-size intervals.
- Subgroup analyses are not powered for equivalence claims.
- Deterministic synthetic cases reduce label uncertainty but may overstate performance relative to uncontrolled real outputs.
