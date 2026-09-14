import { createContext, useContext } from 'react';
import type { ResolvedTheme, ThemeMode } from './theme';

export interface ThemeContextValue {
	mode: ThemeMode;
	resolved: ResolvedTheme;
	setMode: (mode: ThemeMode) => void;
}

export const ThemeContext = createContext<ThemeContextValue>({
	mode: 'system',
	resolved: 'light',
	setMode: () => {},
});

export function useTheme(): ThemeContextValue {
	return useContext(ThemeContext);
}
