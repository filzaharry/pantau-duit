<script lang="ts">
	import type { Account } from '$lib/types';
	import { formatRupiah } from '$lib/utils/formatters';
	import { getWalletImage } from '$lib/utils/walletIcons';
	import { ArrowLeftRight, Trash2, Image as ImageIcon } from 'lucide-svelte';

	interface Props {
		account: Account;
		ontransfer?: (acc: Account) => void;
		ondelete?: (acc: Account) => void;
		onedit?: (acc: Account) => void;
	}

	let { account, ontransfer, ondelete, onedit }: Props = $props();

	const walletImage = $derived(getWalletImage(account.icon, account.type));
</script>

<div
	class="p-4 sm:p-5 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] flex flex-col justify-between gap-3 min-w-[240px] relative overflow-hidden group hover:border-[#007AFF]/40 hover:-translate-y-0.5 transition-all"
>
	<!-- Static Action Buttons Anchored to Top Right -->
	<div class="absolute top-3.5 right-3.5 flex items-center gap-1 z-10">
		{#if onedit}
			<button
				type="button"
				onclick={() => onedit(account)}
				class="p-1.5 rounded-lg text-slate-400 hover:text-[#007AFF] hover:bg-slate-100 dark:hover:bg-white/5 transition-colors cursor-pointer"
				aria-label="Ubah gambar dan detail dompet {account.name}"
				title="Ubah Gambar & Rekening"
			>
				<ImageIcon class="w-3.5 h-3.5" />
			</button>
		{/if}
		{#if ontransfer}
			<button
				type="button"
				onclick={() => ontransfer(account)}
				class="p-1.5 rounded-lg text-slate-400 hover:text-[#007AFF] hover:bg-slate-100 dark:hover:bg-white/5 transition-colors cursor-pointer"
				aria-label="Transfer dari {account.name}"
				title="Transfer Saldo"
			>
				<ArrowLeftRight class="w-3.5 h-3.5" />
			</button>
		{/if}
		{#if ondelete}
			<button
				type="button"
				onclick={() => ondelete(account)}
				class="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/30 transition-colors cursor-pointer"
				aria-label="Hapus rekening {account.name}"
				title="Hapus Rekening"
			>
				<Trash2 class="w-3.5 h-3.5" />
			</button>
		{/if}
	</div>

	<!-- Card Top: Wallet Image & Account Info with Truncate Safe Space -->
	<div class="flex items-center gap-3 pr-20 min-w-0">
		<div class="w-11 h-11 rounded-2xl flex items-center justify-center shrink-0 p-1 bg-slate-50 dark:bg-white/5 border border-slate-200/60 dark:border-white/10 shadow-sm relative overflow-hidden">
			<img
				src={walletImage}
				alt={account.name}
				class="w-full h-full object-contain rounded-xl"
				loading="lazy"
			/>
		</div>
		<div class="min-w-0 flex-1">
			<h4
				class="text-sm font-semibold text-slate-900 dark:text-white tracking-tight leading-snug truncate"
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
</div>
