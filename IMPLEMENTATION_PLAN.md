# OncoFusion implementation plan

1. Establish typed case, evidence, feature, alignment, model, job, and prediction contracts. Build a synthetic, visibly labeled end-to-end API and dashboard.
2. Add bounded source manifests, validation, patient-level immutable splits, and a clinical baseline for one audited real cohort.
3. Add subtype-specific encoders and cached feature artifacts, then compare unimodal heads with patient-matched concatenation.
4. Add calibrated, evaluated fusion and supported missing-input routes. Keep learned alignment and gating experimental until paired training data exists.
5. Complete the evidence dashboard, model cards, container startup, and tested evaluation reports.

Initial demonstrable task: synthetic mammography-study malignancy classification at the examination index time. All synthetic predictions are deterministic software fixtures, not fitted model outputs. No real-data cohort or evaluated model is bundled.
