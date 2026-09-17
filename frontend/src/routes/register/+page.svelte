<script lang="ts">
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth.svelte';
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import GlassSurface from '$lib/components/ui/GlassSurface.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import { ArrowRight, Sparkles } from 'lucide-svelte';

	let name = $state('');
	let email = $state('');
	let password = $state('');
	let workspaceName = $state('Keuangan Pribadi');
	let loading = $state(false);

	async function handleRegister() {
		loading = true;
		await authStore.login(email || 'user@example.com', password);
		if (authStore.user && name) {
			authStore.user.name = name;
		}
		if (workspaceName) {
			authStore.workspace.name = workspaceName;
		}
		notificationStore.toast('Pendaftaran berhasil! Selamat datang di PantauDuit.', 'success');
		loading = false;
		goto('/dashboard');
	}
</script>

<div class="w-full max-w-md mx-auto my-auto py-8">
	<GlassSurface elevated class="p-8 rounded-3xl relative overflow-hidden">
		<div class="text-center mb-6">
			<div class="w-12 h-12 rounded-2xl bg-gradient-to-br from-[#007AFF] to-[#0055B3] text-white flex items-center justify-center font-semibold text-2xl mx-auto mb-3 shadow-lg shadow-[#007AFF]/30">
				P
			</div>
			<h1 class="text-2xl font-semibold text-slate-900 dark:text-white tracking-tight">
				Mulai Pantau<span class="text-[#007AFF] dark:text-[#0A84FF]">Duit</span>
			</h1>
			<p class="text-xs text-slate-500 dark:text-slate-400 mt-1">
				Buat akun & hubungkan asisten keuangan Telegram Anda
			</p>
		</div>

		<form onsubmit={(e) => { e.preventDefault(); handleRegister(); }} class="space-y-4">
			<Input
				bind:value={name}
				label="Nama Lengkap"
				placeholder="Alex Kurniawan"
				required
			/>

			<Input
				type="email"
				bind:value={email}
				label="Alamat Email"
				placeholder="alex@example.com"
				required
			/>

			<Input
				bind:value={workspaceName}
				label="Nama Ruang Kerja (Workspace)"
				placeholder="Keuangan Pribadi"
			/>

			<Input
				type="password"
				bind:value={password}
				label="Kata Sandi Baru"
				placeholder="Minimal 8 karakter"
				required
			/>

			<Button type="submit" variant="primary" class="w-full mt-2" disabled={loading}>
				<span>{loading ? 'Mendaftarkan...' : 'Daftar Akun Baru'}</span>
				<ArrowRight class="w-4 h-4" />
			</Button>
		</form>

		<div class="text-center mt-6 pt-4 border-t border-slate-100 dark:border-white/5">
			<p class="text-xs text-slate-500 dark:text-slate-400">
				Sudah memiliki akun?
				<a href="/login" class="font-semibold text-[#007AFF] hover:underline">
					Masuk di Sini
				</a>
			</p>
		</div>
	</GlassSurface>
</div>
