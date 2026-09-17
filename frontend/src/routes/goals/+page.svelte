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
		ArrowUpRight
	} from 'lucide-svelte';

	let isAddGoalOpen = $state(false);
	let isTopUpOpen = $state(false);
	let selectedGoalId = $state(financialStore.goals[0]?.id || '');
	let topUpAmount = $state(500000);
	let sourceAccountId = $state(financialStore.accounts[0]?.id || '');

	// Add Goal Form
	let goalName = $state('');
	let targetAmount = $state(10000000);
	let currentAmount = $state(0);
	let targetDate = $state('2026-12-31');
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

	function handleAddGoal() {
		formError = '';
		if (!goalName.trim()) {
			formError = 'Nama target harus diisi.';
			return;
		}

		if (targetAmount <= 0) {
			formError = 'Nominal target harus lebih dari 0.';
			return;
		}

		financialStore.goals.push({
			id: `goal-${Date.now()}`,
			tenant_id: 'tenant-demo-uuid-001',
			name: goalName.trim(),
			target_amount: targetAmount,
			current_amount: currentAmount,
			target_date: targetDate ? `${targetDate}T00:00:00Z` : undefined,
			status: 'IN_PROGRESS',
			created_at: new Date().toISOString()
		});

		notificationStore.toast(`Target ${goalName} berhasil dibuat!`, 'success');
		isAddGoalOpen = false;
		goalName = '';
		targetAmount = 10000000;
		currentAmount = 0;
	}

	function handleTopUp() {
		if (topUpAmount <= 0) return;

		const goal = financialStore.goals.find((g) => g.id === selectedGoalId);
		if (goal) {
			goal.current_amount += topUpAmount;
			if (goal.current_amount >= goal.target_amount) {
				goal.status = 'COMPLETED';
				notificationStore.toast(`Selamat! Target ${goal.name} telah tercapai! 🎉`, 'success');
			} else {
				notificationStore.toast(`Setoran ${formatRupiah(topUpAmount)} ke ${goal.name} berhasil!`, 'success');
			}
		}

		isTopUpOpen = false;
	}
</script>

<div class="space-y-6 max-w-7xl mx-auto w-full pb-24 lg:pb-10">
	<!-- Page Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
		<div>
			<h1 class="text-xl sm:text-2xl font-semibold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
				<Target class="w-6 h-6 text-[#007AFF] dark:text-[#0A84FF]" />
				<span>Target Tabungan Finansial</span>
			</h1>
			<p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
				Rencanakan dana darurat, liburan, gadget idaman, dan DP rumah secara terukur
			</p>
		</div>

		<div class="flex items-center gap-2 self-start sm:self-auto">
			<Button variant="outline" onclick={() => (isTopUpOpen = true)}>
				<Plus class="w-4 h-4" />
				<span>Nabung Cepat</span>
			</Button>

			<Button variant="primary" onclick={() => (isAddGoalOpen = true)}>
				<Plus class="w-4 h-4" />
				<span>Target Baru</span>
			</Button>
		</div>
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

	<!-- Goals Grid -->
	<div class="space-y-3">
		<h3 class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
			Daftar Target Aktif ({financialStore.goals.length})
		</h3>

		{#if financialStore.goals.length > 0}
			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
				{#each financialStore.goals as goal}
					<GoalCard {goal} />
				{/each}
			</div>
		{:else}
			<EmptyState
				title="Belum ada target tabungan"
				description="Buat target impian baru untuk memotivasi kebiasaan menabungmu."
			/>
		{/if}
	</div>

	<!-- Add Goal Modal -->
	<Modal
		bind:open={isAddGoalOpen}
		title="Buat Target Finansial Baru"
		description="Tentukan impian dan jumlah tabungan yang ingin dicapai"
	>
		<div class="space-y-4">
			<Input
				bind:value={goalName}
				label="Nama Impian / Target"
				placeholder="Contoh: Dana Darurat 6 Bulan, MacBook Pro, Liburan Jepang"
			/>

			<AmountInput
				bind:value={targetAmount}
				label="Target Nominal Total"
			/>

			<AmountInput
				bind:value={currentAmount}
				label="Tabungan yang Sudah Ada Saat Ini"
			/>

			<Input
				type="date"
				bind:value={targetDate}
				label="Target Tanggal Tercapai (Opsional)"
			/>

			{#if formError}
				<p class="text-xs font-medium text-rose-500 bg-rose-50 dark:bg-rose-950/30 p-2.5 rounded-xl border border-rose-200">
					{formError}
				</p>
			{/if}
		</div>

		{#snippet footer()}
			<Button variant="ghost" onclick={() => (isAddGoalOpen = false)}>Batal</Button>
			<Button variant="primary" onclick={handleAddGoal}>Simpan Target</Button>
		{/snippet}
	</Modal>

	<!-- Quick Top-Up Modal -->
	<Modal
		bind:open={isTopUpOpen}
		title="Setor Tabungan Cepat"
		description="Alokasikan tabungan ke salah satu target impian"
	>
		<div class="space-y-4">
			<Select
				bind:value={selectedGoalId}
				options={financialStore.goals.map((g) => ({ value: g.id, label: g.name }))}
				label="Pilih Target Impian"
			/>

			<AmountInput
				bind:value={topUpAmount}
				label="Jumlah yang Disetorkan"
			/>
		</div>

		{#snippet footer()}
			<Button variant="ghost" onclick={() => (isTopUpOpen = false)}>Batal</Button>
			<Button variant="primary" onclick={handleTopUp}>Setor Tabungan</Button>
		{/snippet}
	</Modal>
</div>
