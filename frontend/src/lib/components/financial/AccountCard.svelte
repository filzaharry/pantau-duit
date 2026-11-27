<script lang="ts">
	import type { Account } from '$lib/types';
	import { formatRupiah } from '$lib/utils/formatters';
	import { getWalletImage, getWalletColor, hexToRgba } from '$lib/utils/walletIcons';
	import { ChevronRight } from 'lucide-svelte';

	interface Props {
		account: Account;
	}

	let { account }: Props = $props();

	const walletImage = $derived(getWalletImage(account.icon, account.type));
	const brandColor = $derived(getWalletColor(account.icon, account.type, account.color, account.name));
</script>

<a
	href="/accounts/{account.id}"
	class="p-4 sm:p-5 rounded-2xl bg-white dark:bg-[#151926] border flex flex-col justify-between gap-3 min-w-[240px] relative overflow-hidden group hover:-translate-y-0.5 hover:shadow-lg transition-all cursor-pointer block"
	style="
		border-color: {hexToRgba(brandColor, 0.28)};
		box-shadow: 0 4px 20px -4px {hexToRgba(brandColor, 0.08)};
	"
>
	<!-- Subtle Brand Tint Overlay with Opacity from Ciri Khas Dompet -->
	<div
		class="absolute inset-0 pointer-events-none transition-opacity duration-300"
		style="background: linear-gradient(135deg, {hexToRgba(brandColor, 0.08)} 0%, {hexToRgba(brandColor, 0.16)} 100%);"
	></div>

	<!-- Ambient soft radial light from top right -->
	<div
		class="absolute -top-12 -right-12 w-32 h-32 rounded-full pointer-events-none blur-2xl opacity-40 group-hover:opacity-70 transition-opacity"
		style="background: {brandColor};"
	></div>

	<!-- Hover border glow layer -->
	<div
		class="absolute inset-0 rounded-2xl border border-transparent group-hover:border-[var(--brand-border)] transition-colors pointer-events-none"
		style="--brand-border: {hexToRgba(brandColor, 0.6)};"
	></div>

	<!-- Card Content (relative z-10 for crisp rendering above tint overlay) -->
	<div class="relative z-10 flex flex-col justify-between gap-3 h-full">
		<!-- Card Top: Wallet Image & Account Info -->
		<div class="flex items-center justify-between gap-3 min-w-0">
			<div class="flex items-center gap-3 min-w-0 flex-1">
				<div
					class="w-11 h-11 rounded-2xl flex items-center justify-center shrink-0 p-1 border shadow-xs relative overflow-hidden group-hover:scale-105 transition-transform"
					style="background-color: {hexToRgba(brandColor, 0.12)}; border-color: {hexToRgba(brandColor, 0.25)};"
				>
					<img
						src={walletImage}
						alt={account.name}
						class="w-full h-full object-contain rounded-xl"
						loading="lazy"
					/>
				</div>
				<div class="min-w-0 flex-1">
					<h4
						class="text-sm font-semibold text-slate-900 dark:text-white tracking-tight leading-snug truncate group-hover:opacity-85 transition-opacity"
						title={account.name}
					>
						{account.name}
					</h4>
					<span class="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5 block truncate">
						{account.type.replace('_', ' ')}
						{#if account.account_number}
							• {account.account_number.slice(-4)}
						{/if}
					</span>
				</div>
			</div>

			<div
				class="w-7 h-7 rounded-xl flex items-center justify-center transition-colors shrink-0"
				style="background-color: {hexToRgba(brandColor, 0.12)}; color: {brandColor};"
			>
				<ChevronRight class="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
			</div>
		</div>

		<!-- Card Balance & Status -->
		<div
			class="pt-2.5 border-t flex items-center justify-between"
			style="border-color: {hexToRgba(brandColor, 0.18)};"
		>
			<div class="flex items-center gap-1.5">
				<span class="w-2 h-2 rounded-full" style="background-color: {brandColor};"></span>
				<span class="text-[10px] font-semibold text-slate-600 dark:text-slate-400">Aktif</span>
			</div>
			<span class="text-sm sm:text-base font-semibold text-slate-900 dark:text-white tracking-tight">
				{formatRupiah(account.current_balance || account.balance || 0)}
			</span>
		</div>
	</div>
</a>
