<script lang="ts">
	import Modal from '$lib/components/ui/Modal.svelte';
	import AmountInput from '$lib/components/ui/AmountInput.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import SearchableSelect from '$lib/components/ui/SearchableSelect.svelte';
	import DatePicker from '$lib/components/ui/DatePicker.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import { financialStore } from '$lib/stores/financial.svelte';
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import type { TransactionType } from '$lib/types';
	import { ArrowDownLeft, ArrowUpRight, ArrowLeftRight } from 'lucide-svelte';

	interface Props {
		open?: boolean;
		onclose?: () => void;
	}

	let { open = $bindable(false), onclose }: Props = $props();

	let transactionType = $state<TransactionType>('EXPENSE');
	let amount = $state(0);
	let description = $state('');
	let accountId = $state(financialStore.accounts[0]?.id || '');
	let destinationAccountId = $state(financialStore.accounts[1]?.id || '');
	let categoryId = $state(financialStore.categories.find((c) => c.type === 'EXPENSE')?.id || '');
	let transactionDate = $state(new Date().toISOString().split('T')[0]);
	let error = $state('');

	// Keep account & category in sync with active financial store data
	$effect(() => {
		if (open) {
			if (!financialStore.accounts.some((a) => a.id === accountId)) {
				accountId = financialStore.accounts[0]?.id || '';
				destinationAccountId = financialStore.accounts[1]?.id || '';
			}
			const cat = financialStore.categories.find((c) => c.type === transactionType);
			if (!financialStore.categories.some((c) => c.id === categoryId && c.type === transactionType)) {
				if (cat) categoryId = cat.id;
			}
		}
	});

	$effect(() => {
		if (transactionType === 'EXPENSE') {
			const cat = financialStore.categories.find((c) => c.type === 'EXPENSE');
			if (cat) categoryId = cat.id;
		} else if (transactionType === 'INCOME') {
			const cat = financialStore.categories.find((c) => c.type === 'INCOME');
			if (cat) categoryId = cat.id;
		}
	});

	// Select options with search suggest metadata
	const accountOptions = $derived(
		financialStore.accounts.map((acc) => ({
			value: acc.id,
			label: acc.name,
			sublabel: acc.type.replace('_', ' ')
		}))
	);

	const destAccountOptions = $derived(
		financialStore.accounts
			.filter((acc) => acc.id !== accountId)
			.map((acc) => ({
				value: acc.id,
				label: acc.name,
				sublabel: acc.type.replace('_', ' ')
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

	function handleSubmit() {
		error = '';

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

		// Dispatch to financial store
		financialStore.addTransaction({
			account_id: accountId,
			destination_account_id: transactionType === 'TRANSFER' ? destinationAccountId : undefined,
			category_id: transactionType !== 'TRANSFER' ? categoryId : undefined,
			transaction_type: transactionType,
			amount,
			currency: 'IDR',
			transaction_date: `${transactionDate}T12:00:00Z`,
			description: description.trim(),
			status: 'POSTED',
			source: 'MANUAL_WEB'
		});

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
			<div class="p-3 rounded-xl bg-blue-500/10 border border-blue-500/20 text-xs text-blue-700 dark:text-blue-300">
				ℹ️ <strong>Aturan Bisnis:</strong> Transfer antar rekening mencatat mutasi saldo secara akurat tanpa mempengaruhi total pengeluaran belanja bulanan.
			</div>
		{/if}

		<!-- Amount Input -->
		<AmountInput bind:value={amount} label="Jumlah Nominal" />

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

		<!-- Custom Indonesian Calendar DatePicker (Replacing Native HTML Date) -->
		<DatePicker
			bind:value={transactionDate}
			label="Tanggal Transaksi"
		/>

		<!-- Account Selection with Search Suggest Dropdown (Limit Max 10, Overflow Auto) -->
		{#if transactionType === 'TRANSFER'}
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
		{:else}
			<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
				<SearchableSelect
					bind:value={accountId}
					options={accountOptions}
					label="Rekening / Dompet"
					placeholder="Pilih rekening..."
				/>

				<SearchableSelect
					bind:value={categoryId}
					options={categoryOptions}
					label="Kategori"
					placeholder="Pilih kategori..."
				/>
			</div>
		{/if}

		{#if error}
			<p class="text-xs font-medium text-rose-500 bg-rose-50 dark:bg-rose-950/30 p-2.5 rounded-xl border border-rose-200 dark:border-rose-900">
				{error}
			</p>
		{/if}
	</div>

	{#snippet footer()}
		<Button variant="ghost" onclick={() => (open = false)}>Batal</Button>
		<Button variant="primary" onclick={handleSubmit}>Simpan Transaksi</Button>
	{/snippet}
</Modal>
