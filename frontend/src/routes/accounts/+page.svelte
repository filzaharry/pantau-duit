<script lang="ts">
	import { authStore } from '$lib/stores/auth.svelte';
	import { financialStore } from '$lib/stores/financial.svelte';
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import { formatRupiah } from '$lib/utils/formatters';
	import AccountCard from '$lib/components/financial/AccountCard.svelte';
	import TransactionRow from '$lib/components/financial/TransactionRow.svelte';
	import AddTransactionModal from '$lib/components/financial/AddTransactionModal.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import AmountInput from '$lib/components/ui/AmountInput.svelte';
	import Select from '$lib/components/ui/Select.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import GlassSurface from '$lib/components/ui/GlassSurface.svelte';
	import EmptyState from '$lib/components/ui/EmptyState.svelte';
	import ProgressBar from '$lib/components/ui/ProgressBar.svelte';
	import type { AccountType } from '$lib/types';
	import {
		Wallet,
		Plus,
		ArrowLeftRight,
		Building2,
		Banknote,
		CreditCard,
		Coins,
		ShieldCheck,
		Smartphone,
		Globe,
		Shield,
		ArrowUpRight,
		TrendingUp
	} from 'lucide-svelte';


	let isTransferModalOpen = $state(false);
	let isAddAccountOpen = $state(false);

	// Add Account Form
	let accountName = $state('');
	let accountType = $state<AccountType>('BANK');
	let institutionName = $state('');
	let initialBalance = $state(0);
	let accountNumber = $state('');
	let formError = $state('');

	const accountTypeOptions = [
		{ value: 'BANK', label: 'Rekening Bank' },
		{ value: 'E_WALLET', label: 'Dompet Digital (E-Wallet)' },
		{ value: 'CASH', label: 'Uang Tunai (Cash)' },
		{ value: 'INVESTMENT', label: 'Rekening Investasi (RDN/Crypto)' }
	];

	function handleAddAccount() {
		formError = '';
		if (!accountName.trim()) {
			formError = 'Nama rekening harus diisi.';
			return;
		}

		financialStore.accounts.push({
			id: `acc-${Date.now()}`,
			tenant_id: 'tenant-demo-uuid-001',
			name: accountName.trim(),
			type: accountType,
			currency: 'IDR',
			current_balance: initialBalance,
			balance: initialBalance,
			status: 'ACTIVE',
			institution_name: institutionName.trim() || undefined,
			account_number: accountNumber.trim() || undefined,
			is_active: true,
			created_at: new Date().toISOString(),
			updated_at: new Date().toISOString()
		});

		notificationStore.toast(`Rekening ${accountName} berhasil ditambahkan!`, 'success');
		isAddAccountOpen = false;
		accountName = '';
		institutionName = '';
		initialBalance = 0;
		accountNumber = '';
	}

	// Calculate counts & balances
	const bankAccounts = $derived(financialStore.accounts.filter((a) => a.type === 'BANK'));
	const eWalletAccounts = $derived(financialStore.accounts.filter((a) => a.type === 'E_WALLET'));
	const cashAccounts = $derived(financialStore.accounts.filter((a) => a.type === 'CASH'));

	const bankCount = $derived(bankAccounts.length);
	const eWalletCount = $derived(eWalletAccounts.length);
	const cashCount = $derived(cashAccounts.length);

	const bankBalance = $derived(
		bankAccounts.reduce((acc, a) => acc + (a.current_balance || a.balance || 0), 0)
	);
	const eWalletBalance = $derived(
		eWalletAccounts.reduce((acc, a) => acc + (a.current_balance || a.balance || 0), 0)
	);
	const cashBalance = $derived(
		cashAccounts.reduce((acc, a) => acc + (a.current_balance || a.balance || 0), 0)
	);
</script>

<div class="space-y-6 max-w-7xl mx-auto w-full pb-24 lg:pb-10">
	<!-- Page Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
		<div>
			<h1 class="text-xl sm:text-2xl font-semibold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
				<Wallet class="w-6 h-6 text-[#007AFF] dark:text-[#0A84FF]" />
				<span>{authStore.isSuperuser ? 'Kas & Rekening Sistem' : 'Rekening & Dompet Digital'}</span>
			</h1>
			<p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
				{authStore.isSuperuser
					? 'Saldo terkumpul dari payment gateway dan bank operasional'
					: 'Kelola seluruh saldo akun bank, e-wallet, uang tunai, dan akun investasi'}
			</p>
		</div>

			<!-- Action Buttons -->
			<div class="grid grid-cols-2 sm:flex items-center gap-2 w-full sm:w-auto">
				<Button variant="outline" class="w-full sm:w-auto justify-center" onclick={() => (isTransferModalOpen = true)}>
					<ArrowLeftRight class="w-4 h-4" />
					<span>Transfer Saldo</span>
				</Button>

				<Button variant="primary" class="w-full sm:w-auto justify-center" onclick={() => (isAddAccountOpen = true)}>
					<Plus class="w-4 h-4" />
					<span>Tambah Rekening</span>
				</Button>
			</div>
		</div>

	<!-- Top Metric Ribbon Strip (Segmented Accounts Overview - 2x2 on mobile, 4-col on desktop) -->
	<div class="p-3 sm:p-5 rounded-2xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06]">
		<div class="grid grid-cols-2 lg:grid-cols-4 gap-2.5 sm:gap-4 lg:divide-x divide-slate-100 dark:divide-white/5">
			<!-- Col 1: Total Kekayaan (Net Worth) -->
			<div class="flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-blue-500/10 text-[#007AFF] dark:text-[#0A84FF] flex items-center justify-center shrink-0">
					<Wallet class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">Total Saldo</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">{formatRupiah(financialStore.totalBalance)}</span>
					<span class="text-[10px] sm:text-[11px] text-slate-400 truncate block">{financialStore.accounts.length} Akun Aktif</span>
				</div>
			</div>

			<!-- Col 2: Rekening Bank -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-blue-500/10 dark:bg-blue-500/20 text-[#007AFF] dark:text-[#0A84FF] flex items-center justify-center shrink-0">
					<Building2 class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">
						{authStore.isSuperuser ? 'Bank Bisnis' : 'Rekening Bank'}
					</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">{formatRupiah(bankBalance)}</span>
					<span class="text-[10px] sm:text-[11px] text-slate-400 truncate block">{bankCount} Akun Bank</span>
				</div>
			</div>

			<!-- Col 3: Dompet Digital (E-Wallet) -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-cyan-500/10 dark:bg-cyan-500/20 text-cyan-600 dark:text-cyan-400 flex items-center justify-center shrink-0">
					<Smartphone class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">
						{authStore.isSuperuser ? 'Payment Gateway' : 'Dompet Digital'}
					</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">{formatRupiah(eWalletBalance)}</span>
					<span class="text-[10px] sm:text-[11px] text-slate-400 truncate block">{eWalletCount} Akun PG</span>
				</div>
			</div>

			<!-- Col 4: Uang Kas & Tunai -->
			<div class="lg:pl-5 flex items-center gap-2.5 sm:gap-3 min-w-0">
				<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-emerald-500/10 dark:bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 flex items-center justify-center shrink-0">
					<Banknote class="w-4 h-4 sm:w-5 sm:h-5" />
				</div>
				<div class="min-w-0 flex-1">
					<span class="text-[9px] sm:text-[10px] uppercase tracking-wider text-slate-400 font-semibold truncate block">
						{authStore.isSuperuser ? 'Saldo Server' : 'Uang Kas & Tunai'}
					</span>
					<span class="text-xs sm:text-base font-semibold text-slate-900 dark:text-white truncate block">{formatRupiah(cashBalance)}</span>
					<span class="text-[10px] sm:text-[11px] text-slate-400 truncate block">{cashCount} Akun Kas</span>
				</div>
			</div>
		</div>
	</div>

	<!-- Accounts Cards Grid -->
	<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 sm:gap-4">
		{#each financialStore.accounts as account}
			<AccountCard {account} />
		{/each}

		<!-- + Tambah Rekening Interactive Card (Responsive horizontal strip on mobile, vertical card on desktop) -->
		<button
			type="button"
			onclick={() => (isAddAccountOpen = true)}
			class="p-3.5 sm:p-5 rounded-2xl border border-dashed border-slate-200/90 dark:border-white/10 hover:border-[#007AFF] dark:hover:border-[#0A84FF] flex flex-row sm:flex-col items-center justify-center text-left sm:text-center gap-3 sm:gap-2.5 group transition-all min-h-[56px] sm:min-h-[140px] bg-slate-50/50 dark:bg-white/[0.01] hover:bg-blue-50/20 dark:hover:bg-blue-500/[0.02] cursor-pointer"
		>
			<div class="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-blue-500/10 dark:bg-blue-500/20 text-[#007AFF] dark:text-[#0A84FF] flex items-center justify-center shrink-0 group-hover:scale-110 transition-transform">
				<Plus class="w-4 h-4 sm:w-5 sm:h-5" />
			</div>
			<div>
				<span class="text-xs font-semibold text-slate-900 dark:text-white block group-hover:text-[#007AFF] dark:group-hover:text-[#0A84FF]">Tambah Rekening</span>
				<span class="text-[10px] sm:text-[11px] text-slate-400 block">Hubungkan bank / e-wallet baru</span>
			</div>
		</button>
	</div>

	<!-- Transfer & Add Account Modals -->
	<AddTransactionModal bind:open={isTransferModalOpen} />

	<!-- Add Account Modal -->
	<Modal
		bind:open={isAddAccountOpen}
		title="Tambah Rekening / Dompet Baru"
		description="Tambahkan sumber dana baru untuk dicatat di PantauDuit"
	>
		<div class="space-y-4">
			<Input
				bind:value={accountName}
				label="Nama Rekening / Dompet"
				placeholder="Contoh: BCA Utama, GoPay, Dompet Saku"
			/>

			<Select
				bind:value={accountType}
				options={accountTypeOptions}
				label="Tipe Akun"
			/>

			<Input
				bind:value={institutionName}
				label="Nama Institusi / Bank (Opsional)"
				placeholder="Contoh: Bank Central Asia, GoTo, Bank Jago"
			/>

			<Input
				bind:value={accountNumber}
				label="Nomor Rekening / HP (Opsional)"
				placeholder="Contoh: 1234567890 atau 0812xxxx"
			/>

			<AmountInput
				bind:value={initialBalance}
				label="Saldo Awal Saat Ini"
			/>

			{#if formError}
				<p class="text-xs font-semibold text-rose-500 bg-rose-50 dark:bg-rose-950/30 p-2.5 rounded-xl border border-rose-200">
					{formError}
				</p>
			{/if}
		</div>

		{#snippet footer()}
			<Button variant="ghost" onclick={() => (isAddAccountOpen = false)}>Batal</Button>
			<Button variant="primary" onclick={handleAddAccount}>Simpan Rekening</Button>
		{/snippet}
	</Modal>
</div>
