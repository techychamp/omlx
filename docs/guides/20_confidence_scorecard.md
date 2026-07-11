# Confidence Scorecard


| Component | Confidence | Evidence |
|---|---|---|
| Weight loading | 100% | Tensor names, shapes, dtypes match |
| Tokenizer | 100% | Token IDs identical on golden prompts |
| Embeddings | 90% | Tested but needs formal Cosine Sim metrics |
| Attention | 0% | Implementation pending |
| Hidden states | 0% | Implementation pending |
| Diffusion loop | 0% | Implementation pending |
| Streaming | 0% | Implementation pending |
| Overall | 30% | Needs comprehensive execution trace |
