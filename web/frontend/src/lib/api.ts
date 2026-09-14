const BASE = '/api';

export class ApiError extends Error {
	status: number;
	constructor(status: number, message: string) {
		super(message);
		this.status = status;
	}
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
	let res: Response;
	try {
		res = await fetch(`${BASE}${path}`, {
			headers: { 'Content-Type': 'application/json' },
			...init,
		});
	} catch {
		throw new ApiError(0, 'Cannot reach the backend (localhost:8000). Make sure the server is running.');
	}
	if (!res.ok) {
		let message = `Request failed (HTTP ${res.status})`;
		try {
			const body = await res.json();
			if (typeof body?.detail === 'string') message = body.detail;
			else if (Array.isArray(body?.detail)) {
				message = body.detail
					.map((d: { msg?: string }) => d?.msg ?? '')
					.filter(Boolean)
					.join('; ') || message;
			} else if (typeof body?.message === 'string') message = body.message;
		} catch {
			// keep default message
		}
		throw new ApiError(res.status, message);
	}
	return res.json() as Promise<T>;
}

/* ---------- types ---------- */

export type RagStatus = 'GREEN' | 'AMBER' | 'RED';

export interface SaasHealthRequest {
	arr: number;
	arr_growth_yoy: number;
	monthly_churn: number;
	net_revenue_retention: number;
	cac_payback_months: number;
	gross_margin: number;
	burn_rate_monthly: number;
	cash_on_hand: number;
}

export interface SaasMetric {
	key: string;
	label: string;
	value: number | null;
	unit: string;
	status: RagStatus;
	green_range: string;
	amber_range: string;
	red_range: string;
	recommendation: string;
}

export interface SaasHealthResponse {
	run_id: number;
	runway_months: number | null;
	metrics: SaasMetric[];
	score: number;
	summary: string;
}

export interface EquityRound {
	name: string;
	amount_raised: number;
	pre_money_valuation: number;
	option_pool_pct: number;
}

export interface EquityDilutionRequest {
	initial_shares: number;
	founder_shares: number;
	rounds: EquityRound[];
}

export interface EquitySnapshot {
	stage: string;
	total_shares: number;
	founder_pct: number;
	others_pct: number;
	investor_pct: number;
	cumulative_investor_pct: number;
	option_pool_pct: number;
	price_per_share: number | null;
	pre_money: number | null;
	amount_raised: number | null;
	post_money: number | null;
}

export interface EquityDilutionResponse {
	run_id: number;
	snapshots: EquitySnapshot[];
	summary: {
		initial_founder_pct: number;
		final_founder_pct: number;
		dilution_pp: number;
		retention_pct: number;
	};
}

export interface DeckSlideCriteria {
	name: string;
	criteria: string[];
	weight: number;
}

export interface DeckCriteriaResponse {
	slides: DeckSlideCriteria[];
}

export interface DeckScoreRequest {
	responses: boolean[][];
}

export interface DeckScoreResponse {
	run_id: number;
	score: number;
	max_score: number;
	percentage: number;
	verdict: string;
	verdict_message: string;
	slides: {
		slide: string;
		passed: number;
		total: number;
		percentage: number;
		weight: number;
		missed_criteria: string[];
	}[];
	priority_fixes: { slide: string; weight: number; missed: string[] }[];
}

export type ToolName = 'saas-health' | 'equity-dilution' | 'deck-score';

export interface LlmTestRequest {
	base_url: string;
	api_key: string;
	model: string;
}

export interface LlmAnalyzeRequest extends LlmTestRequest {
	tool: ToolName;
	result: object;
	run_id: number | null;
}

export interface HistoryRun {
	id: number;
	tool: string;
	title: string;
	score: number | null;
	created_at: string;
}

export interface HistoryDetail {
	id: number;
	tool: string;
	title: string;
	input: unknown;
	result: unknown;
	ai_analysis: string | null;
	created_at: string;
}

export interface Framework {
	id: 'fundraising' | 'pmf';
	title: string;
	content: string;
}

export interface Template {
	id: string;
	title: string;
	filename: string;
	content: string;
}

/* ---------- endpoints ---------- */

export const api = {
	health: () => request<{ ok: boolean }>('/health'),
	saasHealth: (body: SaasHealthRequest) =>
		request<SaasHealthResponse>('/tools/saas-health', {
			method: 'POST',
			body: JSON.stringify(body),
		}),
	equityDilution: (body: EquityDilutionRequest) =>
		request<EquityDilutionResponse>('/tools/equity-dilution', {
			method: 'POST',
			body: JSON.stringify(body),
		}),
	deckCriteria: () => request<DeckCriteriaResponse>('/tools/deck-criteria'),
	deckScore: (body: DeckScoreRequest) =>
		request<DeckScoreResponse>('/tools/deck-score', {
			method: 'POST',
			body: JSON.stringify(body),
		}),
	llmTest: (body: LlmTestRequest) =>
		request<{ ok: boolean; message: string }>('/llm/test', {
			method: 'POST',
			body: JSON.stringify(body),
		}),
	llmAnalyze: (body: LlmAnalyzeRequest) =>
		request<{ analysis: string }>('/llm/analyze', {
			method: 'POST',
			body: JSON.stringify(body),
		}),
	history: (tool?: string) =>
		request<{ runs: HistoryRun[] }>(`/history${tool ? `?tool=${encodeURIComponent(tool)}` : ''}`),
	historyDetail: (id: number) => request<HistoryDetail>(`/history/${id}`),
	historyDelete: (id: number) =>
		request<{ ok: boolean }>(`/history/${id}`, { method: 'DELETE' }),
	frameworks: () => request<{ frameworks: Framework[] }>('/frameworks'),
	templates: () => request<{ templates: Template[] }>('/templates'),
};
