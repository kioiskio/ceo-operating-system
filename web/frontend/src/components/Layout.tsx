import { useState } from 'react';
import {
	Button,
	Drawer,
	Grid,
	Layout as AntdLayout,
	Menu,
	Segmented,
	Tag,
	Tooltip,
} from 'antd';
import {
	AuditOutlined,
	DashboardOutlined,
	FileTextOutlined,
	HistoryOutlined,
	LineChartOutlined,
	MenuOutlined,
	MoonOutlined,
	PieChartOutlined,
	ReadOutlined,
	SettingOutlined,
	SunOutlined,
} from '@ant-design/icons';
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { isLlmConfigured, loadLlmConfig } from '../lib/llm-config';
import { useTheme } from '../theme-context';
import type { ThemeMode } from '../theme';

const NAV_ITEMS = [
	{ key: '/', icon: <DashboardOutlined />, label: 'Dashboard' },
	{ key: '/saas-health', icon: <LineChartOutlined />, label: 'SaaS Health' },
	{ key: '/equity', icon: <PieChartOutlined />, label: 'Equity Dilution' },
	{ key: '/deck-scorer', icon: <AuditOutlined />, label: 'Deck Scorer' },
	{ key: '/frameworks', icon: <ReadOutlined />, label: 'Frameworks' },
	{ key: '/templates', icon: <FileTextOutlined />, label: 'Templates' },
	{ key: '/history', icon: <HistoryOutlined />, label: 'History' },
	{ key: '/settings', icon: <SettingOutlined />, label: 'Settings' },
];

function selectedKey(pathname: string): string {
	if (pathname === '/') return '/';
	const match = NAV_ITEMS.find((item) => item.key !== '/' && pathname.startsWith(item.key));
	return match?.key ?? '/';
}

export function Layout() {
	const location = useLocation();
	const navigate = useNavigate();
	const screens = Grid.useBreakpoint();
	const [drawerOpen, setDrawerOpen] = useState(false);
	const { mode, resolved, setMode } = useTheme();
	const llmReady = isLlmConfigured(loadLlmConfig());

	const isDesktop = screens.lg ?? false;
	const menu = (
		<Menu
			mode="inline"
			items={NAV_ITEMS}
			selectedKeys={[selectedKey(location.pathname)]}
			onClick={({ key }) => {
				navigate(key);
				setDrawerOpen(false);
			}}
			style={{ borderInlineEnd: 'none' }}
		/>
	);

	return (
		<AntdLayout style={{ minHeight: '100vh' }}>
			{isDesktop ? (
				<AntdLayout.Sider theme={resolved === 'dark' ? 'dark' : 'light'} width={208}>
					<div
						style={{
							padding: '16px 24px',
							fontWeight: 600,
							fontSize: 15,
						}}
					>
						CEO Operating System
					</div>
					{menu}
				</AntdLayout.Sider>
			) : (
				<Drawer
					placement="left"
					open={drawerOpen}
					onClose={() => setDrawerOpen(false)}
					width={240}
					title="CEO Operating System"
					styles={{ body: { padding: 0 } }}
				>
					{menu}
				</Drawer>
			)}

			<AntdLayout>
				<AntdLayout.Header
					style={{
						display: 'flex',
						alignItems: 'center',
						gap: 12,
						paddingInline: isDesktop ? 24 : 12,
						background: 'transparent',
						height: 56,
						lineHeight: 'normal',
					}}
				>
					{!isDesktop && (
						<Button
							type="text"
							icon={<MenuOutlined />}
							onClick={() => setDrawerOpen(true)}
							aria-label="Open navigation"
						/>
					)}
					<div style={{ flex: 1 }} />
					<Tooltip
						title={
							llmReady
								? 'LLM configured — AI deep analysis available'
								: 'LLM not configured — go to Settings'
						}
					>
						<Link to="/settings">
							<Tag color={llmReady ? 'success' : 'default'} style={{ marginInlineEnd: 0 }}>
								{llmReady ? 'LLM Connected' : 'LLM Not Configured'}
							</Tag>
						</Link>
					</Tooltip>
					<Segmented<ThemeMode>
						size="small"
						value={mode}
						onChange={setMode}
						options={[
							{ value: 'light', icon: <SunOutlined />, title: 'Light' },
							{ value: 'dark', icon: <MoonOutlined />, title: 'Dark' },
							{ value: 'system', label: 'System' },
						]}
					/>
				</AntdLayout.Header>

				<AntdLayout.Content style={{ padding: isDesktop ? '16px 24px 32px' : '12px 12px 24px' }}>
					<div style={{ maxWidth: 1200, margin: '0 auto' }}>
						<Outlet />
					</div>
				</AntdLayout.Content>
			</AntdLayout>
		</AntdLayout>
	);
}
