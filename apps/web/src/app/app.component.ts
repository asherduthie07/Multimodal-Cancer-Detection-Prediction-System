import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

interface Evidence { id: string; source_id: string; acquired_at: string; available_at: string; qc_passed: boolean; subtype?: string; view?: string; laterality?: string; assay_id?: string; features?: Record<string, number>; code?: string; value?: string | number; unit?: string; }
interface Case { id: string; dataset_id: string; cancer_type: string; mode: string; index_time: string; imaging: Evidence[]; assays: Evidence[]; clinical: Evidence[]; specimens: Evidence[]; }
interface AlignmentItem { source_id: string; modality: string; status: string; reason: string; }
interface Alignment { valid: boolean; accepted_modalities: string[]; items: AlignmentItem[]; }
interface Prediction { status: string; endpoint: string; evaluation_status: string; model_version: string | null; modalities_used: string[]; probability: number | null; risk_group: string | null; abstention_reasons: string[]; explanation: string; }
interface Job { id: string; status: string; prediction: Prediction | null; }

@Component({selector: 'app-root', standalone: true, imports: [CommonModule], templateUrl: './app.component.html'})
export class AppComponent implements OnInit {
  private http = inject(HttpClient);
  cases: Case[] = [];
  selected: Case | null = null;
  alignment: Alignment | null = null;
  job: Job | null = null;
  evaluation: {status: string; sample_count: number; message: string} | null = null;
  busy = false;
  error = '';
  tab: 'workspace' | 'evaluation' = 'workspace';
  taskId = 'breast_mammo_detection_demo';

  async ngOnInit() { await this.refresh(); }
  async refresh() {
    try {
      this.cases = await firstValueFrom(this.http.get<Case[]>('/api/cases'));
      if (this.cases.length && !this.selected) await this.select(this.cases[0]);
      this.evaluation = await firstValueFrom(this.http.get<any>(`/api/evaluations/${this.taskId}`));
    } catch { this.error = 'API unavailable. Start the FastAPI service on port 8000.'; }
  }
  async createDemo() {
    this.busy = true; this.error = '';
    try { const item = await firstValueFrom(this.http.post<Case>('/api/demo/case', {})); await this.refresh(); await this.select(item); }
    catch { this.error = 'Could not create synthetic case.'; }
    finally { this.busy = false; }
  }
  async select(item: Case) {
    this.selected = item; this.job = null; this.alignment = null; this.error = '';
    try { this.alignment = await firstValueFrom(this.http.post<Alignment>(`/api/cases/${item.id}/align/${this.taskId}`, {})); }
    catch { this.error = 'Could not load alignment report.'; }
  }
  async infer() {
    if (!this.selected) return;
    this.busy = true; this.error = '';
    try {
      this.job = await firstValueFrom(this.http.post<Job>(`/api/cases/${this.selected.id}/inference/${this.taskId}`, {}));
      for (let i = 0; i < 20 && this.job?.status !== 'completed' && this.job?.status !== 'failed'; i++) {
        await new Promise(resolve => setTimeout(resolve, 400));
        this.job = await firstValueFrom(this.http.get<Job>(`/api/jobs/${this.job!.id}`));
      }
      if (this.job?.status === 'failed') this.error = 'Inference job failed.';
    } catch { this.error = 'Could not submit inference job.'; }
    finally { this.busy = false; }
  }
  formatDate(value: string) { return new Date(value).toLocaleString('en-US', {month: 'short', day: 'numeric', year: 'numeric'}); }
  keys(value: Record<string, number> | undefined) { return Object.entries(value ?? {}); }
}
