<script lang="ts">
	import { page } from '$app/state';
	import {
		LayoutDashboard,
		Receipt,
		Plus,
		Wallet,
		Grid
	} from 'lucide-svelte';

	interface Props {
		onOpenQuickAction?: () => void;
		onOpenMenuSheet?: () => void;
	}

	let { onOpenQuickAction, onOpenMenuSheet }: Props = $props();

	function isActive(path: string): boolean {
		return page.url.pathname === path || (path !== '/dashboard' && page.url.pathname.startsWith(path));
	}
</script>

<nav
	class="lg:hidden fixed bottom-0 left-0 right-0 z-40 bg-gradient-to-t from-white/95 via-white/90 to-slate-50/80 dark:from-[#131726]/95 dark:via-[#101422]/90 dark:to-[#0c0f1a]/85 backdrop-blur-md border-t border-slate-200/60 dark:border-white/[0.06] safe-bottom transition-all duration-300 select-none"
	aria-label="Navigasi Utama Mobile"
>
	<div class="max-w-md mx-auto px-4 h-16 flex items-center justify-between relative">
		<!-- 1. Dashboard -->
		<a
			href="/dashboard"
			class="flex flex-col items-center justify-center min-w-[56px] min-h-[48px] rounded-xl transition-all duration-150 {isActive('/dashboard')
				? 'text-[#007AFF] dark:text-[#0A84FF]'
				: 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'}"
		>
			<LayoutDashboard class="w-5 h-5 transition-transform duration-200 {isActive('/dashboard') ? 'scale-110' : ''}" />
			<span class="text-[10px] font-semibold mt-1 tracking-tight">Beranda</span>
		</a>

		<!-- 2. Transaksi -->
		<a
			href="/transactions"
			class="flex flex-col items-center justify-center min-w-[56px] min-h-[48px] rounded-xl transition-all duration-150 {isActive('/transactions')
				? 'text-[#007AFF] dark:text-[#0A84FF]'
				: 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'}"
		>
			<Receipt class="w-5 h-5 transition-transform duration-200 {isActive('/transactions') ? 'scale-110' : ''}" />
			<span class="text-[10px] font-semibold mt-1 tracking-tight">Transaksi</span>
		</a>

		<!-- 3. Elevated Center Quick Action (+) Button -->
		<div class="relative -top-3 flex flex-col items-center">
			<button
				type="button"
				onclick={onOpenQuickAction}
				class="w-13 h-13 rounded-full bg-gradient-to-tr from-[#007AFF] via-[#0A84FF] to-[#38bdf8] text-white flex items-center justify-center active:scale-95 transition-all duration-200 hover:brightness-110"
				aria-label="Catat Transaksi Cepat"
			>
				<Plus class="w-6 h-6 stroke-[2.5]" />
			</button>
			<span class="text-[10px] font-semibold text-slate-700 dark:text-slate-300 mt-1">Catat</span>
		</div>

		<!-- 4. Rekening -->
		<a
			href="/accounts"
			class="flex flex-col items-center justify-center min-w-[56px] min-h-[48px] rounded-xl transition-all duration-150 {isActive('/accounts')
				? 'text-[#007AFF] dark:text-[#0A84FF]'
				: 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200'}"
		>
			<Wallet class="w-5 h-5 transition-transform duration-200 {isActive('/accounts') ? 'scale-110' : ''}" />
			<span class="text-[10px] font-semibold mt-1 tracking-tight">Rekening</span>
		</a>

		<!-- 5. Menu Lainnya -->
		<button
			type="button"
			onclick={onOpenMenuSheet}
			class="flex flex-col items-center justify-center min-w-[56px] min-h-[48px] rounded-xl text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 transition-all duration-150"
			aria-label="Buka Menu Lainnya"
		>
			<Grid class="w-5 h-5" />
			<span class="text-[10px] font-semibold mt-1 tracking-tight">Menu</span>
		</button>
	</div>
</nav>
