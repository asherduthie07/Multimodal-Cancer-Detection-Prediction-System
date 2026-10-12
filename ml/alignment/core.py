from packages.contracts.schemas import AlignmentItem, AlignmentReport, Case
from ml.tasks.registry import Task


def align_case(case: Case, task: Task) -> AlignmentReport:
    items: list[AlignmentItem] = []
    if case.cancer_type != task.cancer_type:
        return AlignmentReport(case_id=case.id, task_id=task.id, index_time=case.index_time,
            items=[], accepted_modalities=[], valid=False)
    specimen_ids = {s.id for s in case.specimens if s.case_id == case.id}
    evidence = [("imaging", x, x.subtype) for x in case.imaging]
    evidence += [("genomics", x, x.subtype) for x in case.assays]
    evidence += [("clinical", x, "structured") for x in case.clinical]
    for modality, item, subtype in evidence:
        reason = "Available at index time and associated with case"
        status = "accepted"
        if item.case_id != case.id:
            status, reason = "unmatched", "Patient/case ID differs"
        elif item.available_at > case.index_time:
            status, reason = "excluded", "Result became available after prediction index"
        elif item.acquired_at > case.index_time:
            status, reason = "excluded", "Evidence acquired after prediction index"
        elif case.split and item.split and case.split != item.split:
            status, reason = "excluded", "Evidence belongs to a different patient partition"
        elif not item.qc_passed:
            status, reason = "excluded", "Failed quality control: " + "; ".join(item.qc_reasons)
        elif subtype not in task.supported_subtypes.get(modality, ()):
            status, reason = "excluded", f"Unsupported {modality} subtype: {subtype}"
        elif modality == "genomics" and item.specimen_id not in specimen_ids:
            status, reason = "unmatched", "Assay specimen is not associated with this case"
        items.append(AlignmentItem(source_id=item.id, modality=modality, status=status, reason=reason))
    accepted = sorted({x.modality for x in items if x.status == "accepted"})
    return AlignmentReport(case_id=case.id, task_id=task.id, index_time=case.index_time,
        items=items, accepted_modalities=accepted,
        valid=all(x in accepted for x in task.required_modalities))
