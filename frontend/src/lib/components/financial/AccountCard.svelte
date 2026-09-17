<script lang="ts">
	import type { Account } from '$lib/types';
	import { formatRupiah } from '$lib/utils/formatters';
	import { Building2, Wallet, Banknote, ArrowLeftRight } from 'lucide-svelte';

	interface Props {
		account: Account;
		ontransfer?: (acc: Account) => void;
	}

	let { account, ontransfer }: Props = $props();

	function getAccountIcon(type: string) {
		switch (type) {
			case 'BANK':
				return Building2;
			case 'E_WALLET':
				return Wallet;
			default:
				return Banknote;
		}
	}

	const Icon = $derived(getAccountIcon(account.type));
</script>

<div
	class="p-4 sm:p-5 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] flex flex-col justify-between gap-3 min-w-[240px] relative overflow-hidden group hover:border-[#007AFF]/40 hover:-translate-y-0.5 transition-all"
>
	<!-- Card Top -->
	<div class="flex items-center justify-between">
		<div class="flex items-center gap-2.5">
			<div
				class="w-10 h-10 rounded-xl flex items-center justify-center text-white font-semibold shrink-0"
				style="background-color: {account.color || '#007AFF'};"
			>
				<Icon class="w-5 h-5" />
			</div>
			<div class="min-w-0">
				<h4 class="text-sm font-semibold text-slate-900 dark:text-white tracking-tight leading-none truncate">
					{account.name}
				</h4>
				<span class="text-[11px] text-slate-500 dark:text-slate-400 mt-1 block truncate">
					{account.type.replace('_', ' ')}
					{#if account.account_number}
						• {account.account_number.slice(-4)}
					{/if}
				</span>
			</div>
		</div>

		{#if ontransfer}
			<button
				type="button"
				onclick={() => ontransfer(account)}
				class="p-2 rounded-xl text-slate-400 hover:text-[#007AFF] hover:bg-slate-100 dark:hover:bg-white/5 transition-colors"
				aria-label="Transfer dari {account.name}"
			>
				<ArrowLeftRight class="w-4 h-4" />
			</button>
		{/if}
	</div>

	<!-- Card Balance & Status -->
	<div class="pt-2.5 border-t border-slate-100 dark:border-white/5 flex items-center justify-between">
		<div class="flex items-center gap-1.5">
			<span class="w-2 h-2 rounded-full bg-[#007AFF]"></span>
			<span class="text-[10px] font-semibold text-slate-500 dark:text-slate-400">Aktif</span>
		</div>
		<span class="text-sm sm:text-base font-semibold text-slate-900 dark:text-white tracking-tight">
			{formatRupiah(account.current_balance)}
		</span>
	</div>
</div>
