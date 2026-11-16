<script lang="ts">
	import { financialStore } from '$lib/stores/financial.svelte';
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import { formatRupiah } from '$lib/utils/formatters';
	import GoalCard from '$lib/components/financial/GoalCard.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import AmountInput from '$lib/components/ui/AmountInput.svelte';
	import Select from '$lib/components/ui/Select.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import GlassSurface from '$lib/components/ui/GlassSurface.svelte';
	import EmptyState from '$lib/components/ui/EmptyState.svelte';
	import ProgressBar from '$lib/components/ui/ProgressBar.svelte';
	import {
		Target,
		Plus,
		Sparkles,
		CheckCircle2,
		Calendar,
		ArrowUpRight,
		Search,
		Filter,
		Trash2
	} from 'lucide-svelte';

	let isAddGoalOpen = $state(false);
	let isTopUpOpen = $state(false);
	let selectedGoalId = $state(financialStore.goals[0]?.id || '');
	let topUpAmount = $state(0);
	let sourceAccountId = $state(financialStore.accounts[0]?.id || '');
	let isSubmitting = $state(false);
	let topUpError = $state('');

	let searchQuery = $state('');
	let selectedStatus = $state<'ALL' | 'IN_PROGRESS' | 'COMPLETED'>('ALL');
	let isFilterOpen = $state(false);

	const isFilterActive = $derived(selectedStatus !== 'ALL');

	const selectedSourceAccount = $derived(financialStore.accounts.find((a) => a.id === sourceAccountId));

	const accountOptions = $derived(
		financialStore.accounts.map((a) => ({
			value: a.id,
			label: `${a.name} (Saldo: ${formatRupiah(a.current_balance)})`,
			sublabel: a.type.replace('_', ' ')
		}))
	);

	function resetFilters() {
		selectedStatus = 'ALL';
		isFilterOpen = false;
	}

	const filteredGoals = $derived(
		financialStore.goals.filter((g) => {
			if (selectedStatus === 'COMPLETED' && g.current_amount < g.target_amount) return false;
			if (selectedStatus === 'IN_PROGRESS' && g.current_amount >= g.target_amount) return false;

			if (searchQuery.trim()) {
				const q = searchQuery.toLowerCase();
				return g.name.toLowerCase().includes(q);
			}
			return true;
		})
	);

	function handleDeleteGoal(goal: any) {
		financialStore.deleteGoal(goal.id);
	}

	// Add Goal Form
	let goalName = $state('');
	let targetAmount = $state(0);
	let currentAmount = $state(0);
	let targetDate = $state('');
	let formError = $state('');

	// Overall calculations
	const totalTarget = $derived(
		financialStore.goals.reduce((acc, g) => acc + g.target_amount, 0)
	);

	const totalSaved = $derived(
		financialStore.goals.reduce((acc, g) => acc + g.current_amount, 0)
	);

	const overallPercent = $derived(
		totalTarget > 0 ? Math.round((totalSaved / totalTarget) * 100) : 0
	);

	async function handleAddGoal() {
		formError = '';
		if (!goalName.trim()) {
			formError = 'Nama target impian harus diisi.';
			return;
		}

		if (targetAmount <= 0) {
			formError = 'Nominal target tabungan harus lebih dari 0.';
			return;
		}

		if (currentAmount > 0) {
			if (!sourceAccountId) {
				formError = 'Pilih dompet/rekening asal untuk setoran tabungan pertama.';
				return;
			}
			const acc = financialStore.accounts.find((a) => a.id === sourceAccountId);
			if (acc && acc.current_balance < currentAmount) {
				formError = `Saldo di ${acc.name} tidak cukup (${formatRupiah(acc.current_balance)}).`;
				return;
			}
		}

		isSubmitting = true;
		try {
			const res = await financialStore.addGoal({
				name: goalName.trim(),
				target_amount: targetAmount,
				target_date: targetDate || undefined,
				initial_deposit: currentAmount > 0 ? currentAmount : 0,
				account_id: currentAmount > 0 ? sourceAccountId : undefined
			});

			if (res) {
				isAddGoalOpen = false;
				goalName = '';
				targetAmount = 0;
				currentAmount = 0;
			}
		} finally {
			isSubmitting = false;
		}
	}

	async function handleTopUp() {
		topUpError = '';
		if (topUpAmount <= 0) {
			topUpError = 'Nominal setoran tabungan harus lebih dari 0.';
			return;
		}

		if (!sourceAccountId) {
			topUpError = 'Pilih dompet/rekening asal uang yang mau disetor.';
			return;
		}

		const acc = financialStore.accounts.find((a) => a.id === sourceAccountId);
		if (acc && acc.current_balance < topUpAmount) {
			topUpError = `Saldo di ${acc.name} tidak cukup (${formatRupiah(acc.current_balance)}). Kurangi nominal atau pilih dompet lain.`;
			return;
		}

		isSubmitting = true;
		try {
			const res = await financialStore.contributeGoal(selectedGoalId, {
				account_id: sourceAccountId,
				amount: topUpAmount
			});

			if (res) {
				isTopUpOpen = false;
				topUpAmount = 0;
			}
		} finally {
			isSubmitting = false;
		}
	}
</script>

<div class="space-y-6 max-w-7xl mx-auto w-full pb-24 lg:pb-10">
	<!-- Page Header -->
	<div class="pb-2 border-b border-slate-200/80 dark:border-white/10">
		<h1 class="text-xl sm:text-2xl font-semibold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
			<Target class="w-6 h-6 text-[#007AFF] dark:text-[#0A84FF]" />
			<span>Target Tabungan Finansial</span>
		</h1>
		<p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
			Rencanakan dana darurat, liburan, gadget idaman, dan DP rumah secara terukur
		</p>
	</div>

	<!-- Overview Target Card -->
	<div class="p-6 sm:p-7 rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] space-y-5">
		<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
			<div>
				<div class="flex items-center gap-2">
					<span class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
						Total Tabungan Terkumpul
					</span>
					<span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
						{financialStore.goals.length} Target Aktif
					</span>
				</div>
				<h2 class="text-3xl sm:text-4xl font-semibold text-slate-900 dark:text-white tracking-tight mt-1">
					{formatRupiah(totalSaved)}
					<span class="text-base sm:text-lg font-semibold text-slate-400">/ {formatRupiah(totalTarget)}</span>
				</h2>
			</div>

			<span class="self-start sm:self-auto px-3.5 py-1.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
				{overallPercent}% dari Total Impian
			</span>
		</div>

		<!-- Overall Goals Progress with Radar Beacon & Gradient -->
		<ProgressBar value={overallPercent} variant="emerald" size="lg" />

		<!-- Cute & Lively Goal Summary Metric Badges -->
		<div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
			<!-- Saved Card -->
			<div class="p-3.5 sm:p-4 rounded-2xl bg-slate-50/70 dark:bg-white/[0.03] border border-slate-200/70 dark:border-white/10 flex items-center justify-between hover:border-emerald-500/30 transition-all">
				<div class="flex items-center gap-3">
					<div class="w-9 h-9 rounded-xl bg-emerald-500/10 dark:bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 flex items-center justify-center shrink-0">
						<CheckCircle2 class="w-4 h-4" />
					</div>
					<div>
						<span class="text-[10px] text-slate-400 font-semibold uppercase tracking-wider block leading-tight">Berhasil Disisihkan</span>
						<p class="text-sm sm:text-base font-semibold text-emerald-600 dark:text-emerald-400 leading-tight mt-0.5">
							{formatRupiah(totalSaved)}
						</p>
					</div>
				</div>
				<span class="text-xs font-semibold text-emerald-500 dark:text-emerald-400 px-2 py-0.5 rounded-lg bg-emerald-500/10">
					{overallPercent}%
				</span>
			</div>

			<!-- Remaining Card -->
			<div class="p-3.5 sm:p-4 rounded-2xl bg-slate-50/70 dark:bg-white/[0.03] border border-slate-200/70 dark:border-white/10 flex items-center justify-between hover:border-blue-500/30 transition-all">
				<div class="flex items-center gap-3">
					<div class="w-9 h-9 rounded-xl bg-blue-500/10 dark:bg-blue-500/20 text-[#007AFF] dark:text-[#0A84FF] border border-blue-500/20 flex items-center justify-center shrink-0">
						<Target class="w-4 h-4" />
					</div>
					<div>
						<span class="text-[10px] text-slate-400 font-semibold uppercase tracking-wider block leading-tight">Sisa Target Tambahan</span>
						<p class="text-sm sm:text-base font-semibold text-slate-900 dark:text-white leading-tight mt-0.5">
							{formatRupiah(Math.max(0, totalTarget - totalSaved))}
						</p>
					</div>
				</div>
				<span class="text-xs font-semibold text-blue-500 dark:text-blue-400 px-2 py-0.5 rounded-lg bg-blue-500/10">
					{100 - Math.min(overallPercent, 100)}%
				</span>
			</div>
		</div>
	</div>

	<!-- Unified Action Toolbar: Search (Max 40%), Filter Button & Action Buttons (Inline) -->
	<div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
		<!-- Search Field (Max 40% Width) -->
		<div class="relative w-full sm:w-[40%] sm:max-w-[40%]">
			<Search class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
			<input
				type="text"
				bind:value={searchQuery}
				placeholder="Cari target tabungan..."
				class="w-full h-9 pl-9 pr-3 rounded-xl border border-slate-200/80 dark:border-white/10 bg-white dark:bg-white/5 text-xs text-slate-900 dark:text-white placeholder:text-slate-400 focus:outline-none focus:border-[#007AFF] transition-colors"
			/>
		</div>

		<!-- Action Buttons: Filter, Nabung Cepat, Target Baru (Aligned inline) -->
		<div class="flex items-center gap-2">
			<!-- Filter Button with Popover -->
			<div class="relative">
				<Button
					variant="ghost"
					onclick={() => (isFilterOpen = !isFilterOpen)}
					class="h-9 px-3 text-xs border border-slate-200/80 dark:border-white/10 {isFilterActive ? 'text-[#007AFF] border-[#007AFF]/40 bg-[#007AFF]/5' : ''}"
				>
					<Filter class="w-3.5 h-3.5 mr-1.5" />
					<span>Filter</span>
					{#if isFilterActive}
						<span class="w-1.5 h-1.5 rounded-full bg-[#007AFF] ml-1"></span>
					{/if}
				</Button>

				{#if isFilterOpen}
					<button
						type="button"
						aria-label="Tutup menu filter"
						class="fixed inset-0 z-30 cursor-default bg-transparent"
						onclick={() => (isFilterOpen = false)}
					></button>

					<div class="absolute right-0 top-full mt-2 w-56 p-3 rounded-2xl bg-white dark:bg-[#151926] border border-slate-200/80 dark:border-white/10 shadow-2xl z-40 space-y-3">
						<div>
							<span class="text-[11px] font-semibold text-slate-700 dark:text-slate-300 block mb-1.5">Status Target</span>
							<select
								bind:value={selectedStatus}
								class="w-full h-8 px-2.5 rounded-lg border border-slate-200/80 dark:border-white/10 bg-slate-50 dark:bg-white/5 text-xs text-slate-700 dark:text-slate-300 focus:outline-none focus:border-[#007AFF]"
							>
								<option value="ALL">Semua Status</option>
								<option value="IN_PROGRESS">Sedang Berjalan</option>
								<option value="COMPLETED">Tercapai 100%</option>
							</select>
						</div>

						{#if isFilterActive}
							<div class="pt-1 border-t border-slate-100 dark:border-white/5 flex justify-end">
								<button
									type="button"
									onclick={resetFilters}
									class="text-[11px] font-semibold text-rose-500 hover:underline cursor-pointer"
								>
									Reset Filter
								</button>
							</div>
						{/if}
					</div>
				{/if}
			</div>

			<Button variant="outline" class="h-9 px-3 text-xs" onclick={() => (isTopUpOpen = true)}>
				<Plus class="w-3.5 h-3.5 mr-1.5" />
				<span>Nabung Cepat</span>
			</Button>

			<Button variant="primary" class="h-9 px-3.5 text-xs" onclick={() => (isAddGoalOpen = true)}>
				<Plus class="w-4 h-4 mr-1.5" />
				<span>Target Baru</span>
			</Button>
		</div>
	</div>

	<!-- Goals Grid -->
	<div class="space-y-3">
		<h3 class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
			Daftar Target Finansial ({filteredGoals.length})
		</h3>

		{#if filteredGoals.length > 0}
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
				{#each filteredGoals as goal}
					<GoalCard {goal} ontopup={() => { selectedGoalId = goal.id; isTopUpOpen = true; }} ondelete={handleDeleteGoal} />
				{/each}
			</div>
		{:else}
			<EmptyState
				title="Belum ada target tabungan yang cocok"
				description="Coba ubah kata kunci pencarian atau sesuaikan filter Anda."
			/>
		{/if}
	</div>

	<!-- Add Goal Modal -->
	<Modal
		bind:open={isAddGoalOpen}
		title="Buat Target Tabungan Baru"
		description="Tentukan barang atau impian yang ingin dibeli serta target tabungannya"
	>
		<div class="space-y-4">
			<Input
				bind:value={goalName}
				label="Nama Impian / Kebutuhan"
				placeholder="Contoh: Beli Laptop Baru, Liburan Akhir Tahun, Dana Darurat"
			/>

			<AmountInput
				bind:value={targetAmount}
				label="Berapa Total Target yang Ingin Dicapai?"
				referenceBalance={financialStore.totalBalance}
				balanceLabel="Total Saldo Kas Anda"
			/>

			<div class="p-3 rounded-xl bg-blue-50/70 dark:bg-blue-950/20 border border-blue-200/60 dark:border-blue-900/40 space-y-3">
				<Select
					bind:value={sourceAccountId}
					options={accountOptions}
					label="Ambil Uang Dari Dompet / Rekening (Jika Mau Langsung Setor)"
					placeholder="Pilih rekening sumber uang..."
				/>

				<AmountInput
					bind:value={currentAmount}
					label="Mau Langsung Nabung Berapa Sekarang? (Opsional)"
					referenceBalance={selectedSourceAccount?.current_balance}
					balanceLabel={selectedSourceAccount ? `Saldo ${selectedSourceAccount.name}` : 'Saldo Tabungan'}
				/>
				<p class="text-[11px] text-blue-600 dark:text-blue-400">
					Saldo dompet terpilih akan otomatis terpotong saat target tabungan dibuat.
				</p>
			</div>

			<Input
				type="date"
				bind:value={targetDate}
				label="Target Mau Tercapai Kapan? (Opsional)"
			/>

			{#if formError}
				<p class="text-xs font-medium text-rose-500 bg-rose-50 dark:bg-rose-950/30 p-2.5 rounded-xl border border-rose-200 dark:border-rose-900">
					{formError}
				</p>
			{/if}
		</div>

		{#snippet footer()}
			<Button variant="ghost" onclick={() => (isAddGoalOpen = false)}>Batal</Button>
			<Button variant="primary" onclick={handleAddGoal} disabled={isSubmitting}>
				{isSubmitting ? 'Menyimpan...' : 'Simpan Target Tabungan'}
			</Button>
		{/snippet}
	</Modal>

	<!-- Quick Top-Up Modal -->
	<Modal
		bind:open={isTopUpOpen}
		title="Nabung Sekarang (Pindahkan Saldo)"
		description="Pindahkan uang dari dompet atau rekening Anda ke dalam celengan impian ini"
	>
		<div class="space-y-4">
			<Select
				bind:value={selectedGoalId}
				options={financialStore.goals.map((g) => ({ value: g.id, label: g.name }))}
				label="Mau Nabung untuk Target Apa?"
			/>

			<Select
				bind:value={sourceAccountId}
				options={accountOptions}
				label="Ambil Uang Dari Dompet / Rekening Mana?"
				placeholder="Pilih dompet/rekening..."
			/>

			<AmountInput
				bind:value={topUpAmount}
				label="Berapa Jumlah yang Mau Ditabung?"
				referenceBalance={selectedSourceAccount?.current_balance}
				balanceLabel={selectedSourceAccount ? `Saldo ${selectedSourceAccount.name}` : 'Saldo Tabungan'}
			/>

			{#if topUpError}
				<p class="text-xs font-medium text-rose-500 bg-rose-50 dark:bg-rose-950/30 p-2.5 rounded-xl border border-rose-200 dark:border-rose-900">
					{topUpError}
				</p>
			{/if}
		</div>

		{#snippet footer()}
			<Button variant="ghost" onclick={() => (isTopUpOpen = false)}>Batal</Button>
			<Button variant="primary" onclick={handleTopUp} disabled={isSubmitting}>
				{isSubmitting ? 'Menyimpan...' : 'Setor ke Tabungan'}
			</Button>
		{/snippet}
	</Modal>
</div>
