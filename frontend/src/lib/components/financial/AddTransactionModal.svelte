<script lang="ts">
	import Modal from '$lib/components/ui/Modal.svelte';
	import AmountInput from '$lib/components/ui/AmountInput.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import SearchableSelect from '$lib/components/ui/SearchableSelect.svelte';
	import CategorySuggestSelect from '$lib/components/ui/CategorySuggestSelect.svelte';
	import DatePicker from '$lib/components/ui/DatePicker.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import { financialStore } from '$lib/stores/financial.svelte';
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import { formatRupiah } from '$lib/utils/formatters';
	import type { TransactionType } from '$lib/types';
	import { ArrowDownLeft, ArrowUpRight, ArrowLeftRight, Wallet, Plus, AlertCircle } from 'lucide-svelte';

	interface Props {
		open?: boolean;
		defaultAccountId?: string;
		lockAccount?: boolean;
		initialType?: TransactionType;
		onclose?: () => void;
	}

	let {
		open = $bindable(false),
		defaultAccountId,
		lockAccount = false,
		initialType,
		onclose
	}: Props = $props();

	let transactionType = $state<TransactionType>('EXPENSE');
	let amount = $state(0);
	let description = $state('');
	let accountId = $state('');
	let destinationAccountId = $state(financialStore.accounts[1]?.id || '');
	let categoryId = $state(financialStore.categories.find((c) => c.type === 'EXPENSE')?.id || '');
	let transactionDate = $state(new Date().toISOString().split('T')[0]);
	let error = $state('');

	const selectedAccount = $derived(financialStore.accounts.find((a) => a.id === accountId));

	let lastOpen = false;

	// Reset / initialize form only once when modal opens
	$effect(() => {
		if (open && !lastOpen) {
			if (defaultAccountId) {
				accountId = defaultAccountId;
			} else if (!financialStore.accounts.some((a) => a.id === accountId)) {
				accountId = financialStore.accounts[0]?.id || '';
				destinationAccountId = financialStore.accounts[1]?.id || '';
			}

			if (initialType) {
				transactionType = initialType;
			}

			const targetType = initialType || transactionType;
			if (targetType === 'TRANSFER') {
				if (destinationAccountId === accountId) {
					const other = financialStore.accounts.find((a) => a.id !== accountId);
					if (other) destinationAccountId = other.id;
				}
			} else {
				const cat = financialStore.categories.find((c) => c.type === targetType);
				if (cat) categoryId = cat.id;
			}
		}
		lastOpen = open;
	});

	// React to tab switching when user clicks Pengeluaran, Pemasukan, or Transfer
	$effect(() => {
		if (transactionType === 'EXPENSE') {
			const cat = financialStore.categories.find((c) => c.type === 'EXPENSE');
			if (cat) categoryId = cat.id;
		} else if (transactionType === 'INCOME') {
			const cat = financialStore.categories.find((c) => c.type === 'INCOME');
			if (cat) categoryId = cat.id;
		} else if (transactionType === 'TRANSFER') {
			if (destinationAccountId === accountId) {
				const other = financialStore.accounts.find((a) => a.id !== accountId);
				if (other) destinationAccountId = other.id;
			}
		}
	});

	// Select options: 1 clean text per row, no color, no image, with search suggestion
	const accountOptions = $derived(
		financialStore.accounts.map((acc) => ({
			value: acc.id,
			label: acc.name
		}))
	);

	const destAccountOptions = $derived(
		financialStore.accounts
			.filter((acc) => acc.id !== accountId)
			.map((acc) => ({
				value: acc.id,
				label: acc.name
			}))
	);

	const categoryOptions = $derived(
		financialStore.categories
			.filter((c) => c.type === transactionType)
			.map((c) => ({
				value: c.id,
				label: c.name
			}))
	);

	let isSubmitting = $state(false);

	async function handleSubmit() {
		error = '';

		if (financialStore.accounts.length === 0) {
			error = 'Anda belum memiliki dompet atau rekening. Minimal harus ada 1 dompet/rekening sebelum mencatat transaksi.';
			return;
		}

		if (transactionType === 'TRANSFER' && financialStore.accounts.length < 2) {
			error = 'Transfer antar rekening membutuhkan minimal 2 dompet/rekening terdaftar.';
			return;
		}

		if (amount <= 0) {
			error = 'Jumlah nominal harus lebih dari 0.';
			return;
		}

		if (!description.trim()) {
			error = 'Catatan / deskripsi transaksi tidak boleh kosong.';
			return;
		}

		if (!accountId) {
			error = 'Pilih rekening asal.';
			return;
		}

		if (transactionType === 'TRANSFER') {
			if (!destinationAccountId) {
				error = 'Pilih rekening tujuan transfer.';
				return;
			}
			if (destinationAccountId === accountId) {
				error = 'Rekening tujuan tidak boleh sama dengan rekening asal.';
				return;
			}
		}

		isSubmitting = true;
		try {
			// Dispatch to financial store and persist to real database
			const res = await financialStore.addTransaction({
				account_id: accountId,
				destination_account_id: transactionType === 'TRANSFER' ? destinationAccountId : undefined,
				category_id: transactionType !== 'TRANSFER' ? categoryId : undefined,
				transaction_type: transactionType,
				amount,
				currency: 'IDR',
				transaction_date: `${transactionDate}T12:00:00Z`,
				description: description.trim(),
				status: 'COMPLETED',
				source: 'DASHBOARD'
			});

			if (!res) {
				error = 'Gagal menyimpan transaksi ke database. Silakan coba lagi.';
				return;
			}

			notificationStore.toast(
				transactionType === 'TRANSFER'
					? 'Transfer berhasil dicatat!'
					: transactionType === 'EXPENSE'
						? 'Pengeluaran berhasil dicatat!'
						: 'Pemasukan berhasil dicatat!',
				'success'
			);

			resetForm();
			open = false;
		} catch (err: any) {
			error = err?.message || 'Terjadi kesalahan sistem saat menyimpan transaksi.';
		} finally {
			isSubmitting = false;
		}
	}

	function resetForm() {
		amount = 0;
		description = '';
		error = '';
		transactionDate = new Date().toISOString().split('T')[0];
	}
</script>

<Modal
	bind:open
	title="Catat Transaksi Baru"
	description="Catat pengeluaran, pemasukan, atau transfer antar rekening"
	{onclose}
>
	{#if financialStore.accounts.length === 0}
		<div class="py-6 px-2 text-center space-y-4">
			<div class="w-14 h-14 rounded-2xl bg-amber-500/10 text-amber-500 mx-auto flex items-center justify-center border border-amber-500/20">
				<Wallet class="w-7 h-7" />
			</div>
			<div class="space-y-1.5 max-w-sm mx-auto">
				<h3 class="text-base font-semibold text-slate-900 dark:text-white">
					Belum Ada Dompet / Rekening
				</h3>
				<p class="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
					Anda belum memiliki rekening bank atau dompet digital aktif. Minimal harus ada 1 dompet atau rekening terdaftar terlebih dahulu sebelum dapat mencatat transaksi keuangan.
				</p>
			</div>
			<div class="pt-2 flex flex-col sm:flex-row items-center justify-center gap-2">
				<Button variant="ghost" onclick={() => (open = false)} class="w-full sm:w-auto text-xs">
					Tutup
				</Button>
				<a
					href="/accounts"
					onclick={() => (open = false)}
					class="w-full sm:w-auto inline-flex items-center justify-center gap-1.5 px-4 h-9 rounded-xl bg-[#007AFF] text-white text-xs font-semibold hover:bg-blue-600 transition-colors cursor-pointer"
				>
					<Plus class="w-3.5 h-3.5" />
					<span>Buat Rekening Pertama</span>
				</a>
			</div>
		</div>
	{:else}
		<div class="space-y-4">
			<!-- Transaction Type Selector -->
			<div class="p-1 rounded-xl bg-slate-100 dark:bg-white/5 grid grid-cols-3 gap-1">
				<button
					type="button"
					onclick={() => (transactionType = 'EXPENSE')}
					class="flex items-center justify-center gap-1.5 h-8.5 rounded-lg text-xs font-medium transition-all {transactionType === 'EXPENSE'
						? 'bg-rose-500 text-white'
						: 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'}"
				>
					<ArrowUpRight class="w-3.5 h-3.5" />
					<span>Pengeluaran</span>
				</button>

				<button
					type="button"
					onclick={() => (transactionType = 'INCOME')}
					class="flex items-center justify-center gap-1.5 h-8.5 rounded-lg text-xs font-medium transition-all {transactionType === 'INCOME'
						? 'bg-emerald-500 text-white'
						: 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'}"
				>
					<ArrowDownLeft class="w-3.5 h-3.5" />
					<span>Pemasukan</span>
				</button>

				<button
					type="button"
					onclick={() => (transactionType = 'TRANSFER')}
					class="flex items-center justify-center gap-1.5 h-8.5 rounded-lg text-xs font-medium transition-all {transactionType === 'TRANSFER'
						? 'bg-[#007AFF] text-white'
						: 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'}"
				>
					<ArrowLeftRight class="w-3.5 h-3.5" />
					<span>Transfer</span>
				</button>
			</div>

			{#if transactionType === 'TRANSFER'}
				{#if financialStore.accounts.length < 2}
					<div class="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-700 dark:text-amber-400 flex items-start gap-2">
						<AlertCircle class="w-4 h-4 shrink-0 mt-0.5 text-amber-500" />
						<span>
							<strong>Perhatian:</strong> Transfer saldo membutuhkan minimal 2 rekening terdaftar (rekening asal dan tujuan). Silakan tambahkan rekening kedua terlebih dahulu.
						</span>
					</div>
				{:else}
					<div class="p-3 rounded-xl bg-blue-500/10 border border-blue-500/20 text-xs text-blue-700 dark:text-blue-300">
						ℹ️ <strong>Aturan Bisnis:</strong> Transfer antar rekening mencatat mutasi saldo secara akurat tanpa mempengaruhi total pengeluaran belanja bulanan.
					</div>
				{/if}

				<!-- Source & Destination Account Selection (Top of Transfer) -->
				{#if lockAccount}
					<div class="w-full">
						<SearchableSelect
							bind:value={destinationAccountId}
							options={destAccountOptions}
							label="Ke Rekening (Tujuan)"
							placeholder="Pilih rekening tujuan..."
						/>
					</div>
				{:else}
					<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
						<SearchableSelect
							bind:value={accountId}
							options={accountOptions}
							label="Dari Rekening (Asal)"
							placeholder="Pilih rekening asal..."
						/>

						<SearchableSelect
							bind:value={destinationAccountId}
							options={destAccountOptions}
							label="Ke Rekening (Tujuan)"
							placeholder="Pilih rekening tujuan..."
						/>
					</div>
				{/if}
			{:else}
				<!-- Account & Category Selection for Expense / Income -->
				{#if lockAccount}
					<div class="w-full">
						<CategorySuggestSelect
							bind:value={categoryId}
							categoryType={transactionType === 'EXPENSE' ? 'EXPENSE' : 'INCOME'}
							label="Kategori"
							placeholder="Ketik atau pilih kategori..."
						/>
					</div>
				{:else}
					<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
						<SearchableSelect
							bind:value={accountId}
							options={accountOptions}
							label="Rekening / Dompet"
							placeholder="Pilih rekening..."
						/>

						<CategorySuggestSelect
							bind:value={categoryId}
							categoryType={transactionType === 'EXPENSE' ? 'EXPENSE' : 'INCOME'}
							label="Kategori"
							placeholder="Ketik atau pilih kategori..."
						/>
					</div>
				{/if}
			{/if}

			<!-- Amount Input with Percentage of Account Balance -->
			<AmountInput
				bind:value={amount}
				label="Jumlah Nominal"
				referenceBalance={transactionType === 'INCOME' ? financialStore.totalBalance : Number(selectedAccount?.current_balance || selectedAccount?.balance || 0)}
				balanceLabel={selectedAccount ? `Saldo ${selectedAccount.name}` : 'Saldo Tabungan'}
				showBalance={true}
			/>

			<!-- Description -->
			<Input
				bind:value={description}
				label="Deskripsi / Catatan"
				placeholder={transactionType === 'EXPENSE'
					? 'Contoh: Makan siang nasi padang'
					: transactionType === 'INCOME'
						? 'Contoh: Gaji bulanan / Freelance'
						: 'Contoh: Pindah saldo ke e-wallet'}
			/>

			<!-- Custom Indonesian Calendar DatePicker -->
			<DatePicker
				bind:value={transactionDate}
				label="Tanggal Transaksi"
			/>

			{#if error}
				<p class="text-xs font-medium text-rose-500 bg-rose-50 dark:bg-rose-950/30 p-2.5 rounded-xl border border-rose-200 dark:border-rose-900">
					{error}
				</p>
			{/if}
		</div>
	{/if}

	{#snippet footer()}
		{#if financialStore.accounts.length === 0}
			<Button variant="ghost" onclick={() => (open = false)}>Tutup</Button>
		{:else}
			<Button variant="ghost" onclick={() => (open = false)}>Batal</Button>
			<Button
				variant="primary"
				onclick={handleSubmit}
				disabled={isSubmitting || (transactionType === 'TRANSFER' && financialStore.accounts.length < 2)}
			>
				{isSubmitting ? 'Menyimpan...' : 'Simpan Transaksi'}
			</Button>
		{/if}
	{/snippet}
</Modal>
