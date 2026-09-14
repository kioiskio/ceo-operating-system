export function formatMoney(n: number | null | undefined): string {
	if (n == null || Number.isNaN(n)) return '—';
	const abs = Math.abs(n);
	const sign = n < 0 ? '-' : '';
	if (abs >= 1e9) return `${sign}$${(abs / 1e9).toFixed(1)}B`;
	if (abs >= 1e6) return `${sign}$${(abs / 1e6).toFixed(1)}M`;
	if (abs >= 1e3) return `${sign}$${(abs / 1e3).toFixed(0)}K`;
	return `${sign}$${abs.toFixed(0)}`;
}

export function formatPct(n: number | null | undefined, digits = 1): string {
	if (n == null || Number.isNaN(n)) return '—';
	return `${n.toFixed(digits)}%`;
}

export function formatShares(n: number | null | undefined): string {
	if (n == null || Number.isNaN(n)) return '—';
	return n.toLocaleString('en-US');
}

export function formatTime(iso: string): string {
	const d = new Date(iso);
	if (Number.isNaN(d.getTime())) return iso;
	return d.toLocaleString('en-US', {
		month: 'short',
		day: 'numeric',
		year: 'numeric',
		hour: '2-digit',
		minute: '2-digit',
		hour12: false,
	});
}
