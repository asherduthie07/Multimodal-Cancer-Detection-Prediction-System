# Dataset onboarding

Candidate sources require separate audits. GDC/TCGA may support matched pathology, tissue molecular, and clinical research for selected cancers. CBIS-DDSM is a separate mammography workflow. Published blood-assay datasets may be considered only when patient-level features, labels, pairing, and reuse permissions are verified. These sources must not be joined by cancer type alone. None is downloaded or bundled here.

1. Define cancer type, endpoint, label, index time, and permitted evidence window before inspecting labels.
2. Obtain a bounded manifest containing pseudonymous patient ID, source ID, cancer type, modality, subtype, availability time, and index time. Record reuse permission, source version, storage estimate, and manifest hash.
3. Run `PYTHONPATH=. python -m ml.data.audit path/to/manifest.csv --split-output path/to/split.json`. The tool rejects oversized manifests, missing identifiers, and duplicate source IDs. It writes patient assignments once and refuses to overwrite a split file.
4. Audit actual patient overlap and specimen relationships. Verify deidentification, file integrity, image labels, assay units, and clinical result times. Do not infer pairs from matching cancer type.
5. Fit preprocessing only on training patients. Tune on validation patients. Keep final test patients untouched until model selection is complete.

The current audit utility does not validate source-specific clinical labels or download files. A real cohort adapter, training, and evaluation remain outstanding.
