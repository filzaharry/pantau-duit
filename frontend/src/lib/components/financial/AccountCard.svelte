<script lang="ts">
	import type { Account } from '$lib/types';
	import { formatRupiah } from '$lib/utils/formatters';
	import { getWalletImage } from '$lib/utils/walletIcons';
	import { ChevronRight } from 'lucide-svelte';

	interface Props {
		account: Account;
	}

	let { account }: Props = $props();

	const walletImage = $derived(getWalletImage(account.icon, account.type));
</script>

<a
	href="/accounts/{account.id}"
	class="p-4 sm:p-5 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] flex flex-col justify-between gap-3 min-w-[240px] relative overflow-hidden group hover:border-[#007AFF]/60 hover:shadow-lg hover:shadow-blue-500/5 hover:-translate-y-0.5 transition-all cursor-pointer block"
>
	<!-- Card Top: Wallet Image & Account Info -->
	<div class="flex items-center justify-between gap-3 min-w-0">
		<div class="flex items-center gap-3 min-w-0 flex-1">
			<div class="w-11 h-11 rounded-2xl flex items-center justify-center shrink-0 p-1 bg-slate-50 dark:bg-white/5 border border-slate-200/60 dark:border-white/10 shadow-sm relative overflow-hidden group-hover:scale-105 transition-transform">
				<img
					src={walletImage}
					alt={account.name}
					class="w-full h-full object-contain rounded-xl"
					loading="lazy"
				/>
			</div>
			<div class="min-w-0 flex-1">
				<h4
					class="text-sm font-semibold text-slate-900 dark:text-white tracking-tight leading-snug truncate group-hover:text-[#007AFF] dark:group-hover:text-[#0A84FF] transition-colors"
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

		<div class="w-7 h-7 rounded-xl bg-slate-100/60 dark:bg-white/5 flex items-center justify-center text-slate-400 group-hover:text-[#007AFF] group-hover:bg-blue-500/10 transition-colors shrink-0">
			<ChevronRight class="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
		</div>
	</div>

	<!-- Card Balance & Status -->
	<div class="pt-2.5 border-t border-slate-100 dark:border-white/5 flex items-center justify-between">
		<div class="flex items-center gap-1.5">
			<span class="w-2 h-2 rounded-full bg-[#007AFF]"></span>
			<span class="text-[10px] font-semibold text-slate-500 dark:text-slate-400">Aktif</span>
		</div>
		<span class="text-sm sm:text-base font-semibold text-slate-900 dark:text-white tracking-tight">
			{formatRupiah(account.current_balance || account.balance || 0)}
		</span>
	</div>
</a>
