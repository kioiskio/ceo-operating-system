import { useEffect, useMemo, useState } from 'react';
import { App as AntdApp, ConfigProvider, theme as antdTheme } from 'antd';
import enUS from 'antd/locale/en_US';
import { Route, Routes } from 'react-router-dom';
import {
	loadThemeMode,
	saveThemeMode,
	useResolvedTheme,
	type ThemeMode,
} from './theme';
import { ThemeContext } from './theme-context';
import { Layout } from './components/Layout';
import Dashboard from './pages/Dashboard';
import SaasHealth from './pages/SaasHealth';
import Equity from './pages/Equity';
import DeckScorer from './pages/DeckScorer';
import Frameworks from './pages/Frameworks';
import Templates from './pages/Templates';
import History from './pages/History';
import Settings from './pages/Settings';

export default function App() {
	const [mode, setModeState] = useState<ThemeMode>(loadThemeMode);
	const resolved = useResolvedTheme(mode);

	const themeValue = useMemo(
		() => ({
			mode,
			resolved,
			setMode: (m: ThemeMode) => {
				saveThemeMode(m);
				setModeState(m);
			},
		}),
		[mode, resolved],
	);

	useEffect(() => {
		document.documentElement.classList.toggle('dark', resolved === 'dark');
		document.documentElement.style.colorScheme = resolved;
	}, [resolved]);

	return (
		<ConfigProvider
			locale={enUS}
			theme={{
				algorithm:
					resolved === 'dark' ? antdTheme.darkAlgorithm : antdTheme.defaultAlgorithm,
			}}
		>
			<AntdApp>
				<ThemeContext.Provider value={themeValue}>
					<Routes>
						<Route element={<Layout />}>
							<Route index element={<Dashboard />} />
							<Route path="saas-health" element={<SaasHealth />} />
							<Route path="equity" element={<Equity />} />
							<Route path="deck-scorer" element={<DeckScorer />} />
							<Route path="frameworks" element={<Frameworks />} />
							<Route path="templates" element={<Templates />} />
							<Route path="history" element={<History />} />
							<Route path="settings" element={<Settings />} />
						</Route>
					</Routes>
				</ThemeContext.Provider>
			</AntdApp>
		</ConfigProvider>
	);
}
