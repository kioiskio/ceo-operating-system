export interface LlmConfig {
	base_url: string;
	api_key: string;
	model: string;
}

const KEY = 'ceo-os-llm-config';

export const DEFAULT_LLM_CONFIG: LlmConfig = {
	base_url: 'https://api.openai.com/v1',
	api_key: '',
	model: 'gpt-4o-mini',
};

export function loadLlmConfig(): LlmConfig {
	try {
		const raw = localStorage.getItem(KEY);
		if (!raw) return { ...DEFAULT_LLM_CONFIG };
		const parsed = JSON.parse(raw) as Partial<LlmConfig>;
		return { ...DEFAULT_LLM_CONFIG, ...parsed };
	} catch {
		return { ...DEFAULT_LLM_CONFIG };
	}
}

export function saveLlmConfig(config: LlmConfig): void {
	localStorage.setItem(KEY, JSON.stringify(config));
}

export function isLlmConfigured(config: LlmConfig): boolean {
	return Boolean(config.base_url.trim() && config.api_key.trim() && config.model.trim());
}
