<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import AppShell from '$lib/components/layout/AppShell.svelte';
	import Snackbar from '$lib/components/ui/Snackbar.svelte';
	import Modal from '$lib/components/ui/Modal.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import { authStore } from '$lib/stores/auth.svelte';

	let { children } = $props();

	onMount(() => {
		authStore.init();
	});

	const isLandingRoute = $derived(
		page.url.pathname === '/' ||
		page.url.pathname === '/landing'
	);

	const isAuthRoute = $derived(
		page.url.pathname === '/login' ||
		page.url.pathname === '/register' ||
		page.url.pathname === '/otp'
	);

	const isPublicRoute = $derived(isLandingRoute || isAuthRoute);

	// Client-side authentication guard
	$effect(() => {
		if (typeof window === 'undefined') return;
		if (authStore.isLoading) return;

		const currentPath = page.url.pathname;
		const search = page.url.search;

		if (!isPublicRoute && !authStore.isAuthenticated) {
			const redirectTarget = encodeURIComponent(currentPath + search);
			goto(`/login?redirect=${redirectTarget}`, { replaceState: true });
		} else if (isAuthRoute && authStore.isAuthenticated) {
			const redirectParam = page.url.searchParams.get('redirect');
			const target = (redirectParam && !redirectParam.startsWith('/login')) ? redirectParam : '/dashboard';
			goto(target, { replaceState: true });
		}
	});
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<title>PantauDuit — Telegram-First Personal Finance Command Center</title>
	<meta name="description" content="Personal finance command center dengan integrasi Telegram bot tercepat, tracking multi-rekening, anggaran cerdas, dan analisis portofolio." />
</svelte:head>

<Snackbar />

{#if isLandingRoute}
	<div class="min-h-screen bg-slate-50 dark:bg-[#0B0F19] text-slate-900 dark:text-slate-100 antialiased font-sans transition-colors duration-200">
		{@render children()}
	</div>
{:else if isAuthRoute}
	<div class="min-h-screen bg-slate-50 dark:bg-[#0B0F19] text-slate-900 dark:text-slate-100 flex flex-col justify-center p-4">
		{@render children()}
	</div>
{:else if authStore.isLoading}
	<!-- Minimalist Apple-like Session Verification Screen -->
	<div class="min-h-screen bg-slate-50 dark:bg-[#0B0F19] flex flex-col items-center justify-center p-6 text-center select-none">
		<div class="w-14 h-14 rounded-2xl bg-gradient-to-br from-[#007AFF] to-[#0055B3] text-white flex items-center justify-center font-bold text-2xl shadow-xl shadow-[#007AFF]/25 animate-pulse mb-4">
			P
		</div>
		<div class="flex items-center gap-2 text-sm font-medium text-slate-600 dark:text-slate-400">
			<div class="w-4 h-4 border-2 border-[#007AFF] border-t-transparent rounded-full animate-spin"></div>
			<span>Memverifikasi otentikasi sesi aman...</span>
		</div>
	</div>
{:else if !authStore.isAuthenticated}
	<!-- Unauthenticated placeholder while redirecting to /login -->
	<div class="min-h-screen bg-slate-50 dark:bg-[#0B0F19] flex items-center justify-center p-4">
		<div class="text-xs text-slate-400">Mengarahkan ke halaman masuk...</div>
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
		Sesi Anda akan ditutup dan token akses akan dihapus. Anda perlu memasukkan kembali email dan kata sandi untuk mengakses kembali data finansial dan operasional.
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
