import { useEffect, useState } from 'react';

export type ThemeMode = 'system' | 'light' | 'dark';
export type ResolvedTheme = 'light' | 'dark';

const KEY = 'ceo-os-theme';

export function loadThemeMode(): ThemeMode {
	const raw = localStorage.getItem(KEY);
	return raw === 'light' || raw === 'dark' ? raw : 'system';
}

export function saveThemeMode(mode: ThemeMode): void {
	localStorage.setItem(KEY, mode);
}

function systemTheme(): ResolvedTheme {
	return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

export function useResolvedTheme(mode: ThemeMode): ResolvedTheme {
	const [resolved, setResolved] = useState<ResolvedTheme>(() =>
		mode === 'system' ? systemTheme() : mode,
	);

	useEffect(() => {
		if (mode !== 'system') {
			setResolved(mode);
			return;
		}
		const mq = window.matchMedia('(prefers-color-scheme: dark)');
		const sync = () => setResolved(mq.matches ? 'dark' : 'light');
		sync();
		mq.addEventListener('change', sync);
		return () => mq.removeEventListener('change', sync);
	}, [mode]);

	return resolved;
}
