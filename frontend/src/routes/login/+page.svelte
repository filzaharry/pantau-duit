<script lang="ts">
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth.svelte';
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import GlassSurface from '$lib/components/ui/GlassSurface.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import { Send, Lock, Mail, ArrowRight } from 'lucide-svelte';

	let email = $state('alex@example.com');
	let password = $state('password123');
	let loading = $state(false);

	async function handleLogin(customEmail?: string) {
		loading = true;
		const targetEmail = customEmail || email;
		await authStore.login(targetEmail, password);
		notificationStore.toast(`Masuk sebagai ${authStore.user?.name} (${authStore.user?.role})`, 'success');
		loading = false;
		goto('/dashboard');
	}

	function handleTelegramLogin() {
		notificationStore.toast('Membuka otentikasi via Telegram Bot...', 'info');
		setTimeout(() => {
			handleLogin('budi@pantauduit.id');
		}, 600);
	}
</script>

<div class="w-full max-w-md mx-auto my-auto py-8">
	<GlassSurface elevated class="p-8 rounded-3xl relative overflow-hidden">
		<!-- Subtle ambient glow -->
		<div class="absolute -top-12 -right-12 w-40 h-40 rounded-full bg-[#007AFF]/15 blur-3xl pointer-events-none"></div>

		<!-- Logo & Headline -->
		<div class="text-center mb-6">
			<div class="w-12 h-12 rounded-2xl bg-gradient-to-br from-[#007AFF] to-[#0055B3] text-white flex items-center justify-center font-semibold text-2xl mx-auto mb-3 shadow-lg shadow-[#007AFF]/30">
				P
			</div>
			<h1 class="text-2xl font-semibold text-slate-900 dark:text-white tracking-tight">
				Masuk ke Pantau<span class="text-[#007AFF] dark:text-[#0A84FF]">Duit</span>
			</h1>
			<p class="text-xs text-slate-500 dark:text-slate-400 mt-1">
				Personal Finance Command Center berbasis Telegram
			</p>
		</div>


		<!-- Telegram 1-Click Login -->
		<button
			type="button"
			onclick={handleTelegramLogin}
			class="w-full py-3 px-4 rounded-2xl bg-[#0088cc] hover:bg-[#0077b5] text-white text-xs font-semibold flex items-center justify-center gap-2 shadow-md shadow-[#0088cc]/20 transition-all active:scale-[0.98] mb-5"
		>
			<Send class="w-4 h-4" />
			<span>Masuk Instan via Telegram Bot</span>
		</button>

		<div class="relative flex py-1 items-center mb-5">
			<div class="flex-grow border-t border-slate-200 dark:border-white/10"></div>
			<span class="flex-shrink mx-3 text-[10px] text-slate-400 font-semibold uppercase">Atau Form Manual</span>
			<div class="flex-grow border-t border-slate-200 dark:border-white/10"></div>
		</div>

		<!-- Form -->
		<form onsubmit={(e) => { e.preventDefault(); handleLogin(); }} class="space-y-4">
			<Input
				type="email"
				bind:value={email}
				label="Alamat Email"
				placeholder="nama@email.com"
				required
			/>

			<div>
				<Input
					type="password"
					bind:value={password}
					label="Kata Sandi"
					placeholder="••••••••"
					required
				/>
				<div class="flex justify-end mt-1.5">
					<a href="/otp" class="text-[11px] font-semibold text-[#007AFF] hover:underline">
						Masuk dengan Kode OTP &rarr;
					</a>
				</div>
			</div>

			<Button type="submit" variant="primary" class="w-full mt-2" disabled={loading}>
				<span>{loading ? 'Memproses...' : 'Masuk ke Dasbor'}</span>
				<ArrowRight class="w-4 h-4" />
			</Button>
		</form>

		<!-- Footer -->
		<div class="text-center mt-6 pt-4 border-t border-slate-100 dark:border-white/5">
			<p class="text-xs text-slate-500 dark:text-slate-400">
				Belum punya akun?
				<a href="/register" class="font-semibold text-[#007AFF] hover:underline">
					Daftar Sekarang
				</a>
			</p>
		</div>
	</GlassSurface>
</div>
