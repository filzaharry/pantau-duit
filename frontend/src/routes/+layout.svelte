<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import { page } from '$app/state';
	import AppShell from '$lib/components/layout/AppShell.svelte';
	import Snackbar from '$lib/components/ui/Snackbar.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import { authStore } from '$lib/stores/auth.svelte';

	let { children } = $props();

	const isAuthRoute = $derived(
		page.url.pathname === '/login' ||
		page.url.pathname === '/register' ||
		page.url.pathname === '/otp'
	);
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<title>PantauDuit — Telegram-First Personal Finance Command Center</title>
	<meta name="description" content="Personal finance command center dengan integrasi Telegram bot tercepat, tracking multi-rekening, anggaran cerdas, dan analisis portofolio." />
</svelte:head>

<Snackbar />

{#if isAuthRoute}
	<div class="min-h-screen bg-slate-50 dark:bg-[#0B0F19] text-slate-900 dark:text-slate-100 flex flex-col justify-center p-4">
		{@render children()}
	</div>
{:else}
	<AppShell>
		{@render children()}
	</AppShell>
{/if}

<!-- Modal Konfirmasi Logout Global -->
<Modal
	bind:open={authStore.isLogoutModalOpen}
	title="Konfirmasi Keluar Akun"
	description="Apakah Anda yakin ingin mengakhiri sesi login saat ini?"
>
	<p class="text-xs text-slate-600 dark:text-slate-400 py-2 leading-relaxed">
		Sesi Anda akan ditutup. Anda perlu memasukkan kembali email dan kata sandi untuk mengakses kembali data finansial dan operasional perusahaan.
	</p>
	{#snippet footer()}
		<div class="flex items-center justify-end gap-2">
			<Button variant="ghost" onclick={() => authStore.cancelLogout()}>
				Batal
			</Button>
			<Button variant="danger" onclick={() => authStore.confirmLogout()}>
				Ya, Keluar
			</Button>
		</div>
	{/snippet}
</Modal>

