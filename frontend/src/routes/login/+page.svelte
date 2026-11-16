<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { authStore } from '$lib/stores/auth.svelte';
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import GlassSurface from '$lib/components/ui/GlassSurface.svelte';
	import Input from '$lib/components/ui/Input.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import { Send, Lock, Mail, ArrowRight } from 'lucide-svelte';

	let email = $state('');
	let password = $state('');
	let loading = $state(false);

	const redirectUrl = $derived(page.url.searchParams.get('redirect') || '/dashboard');

	async function handleLogin(customEmail?: string, customPassword?: string) {
		loading = true;
		const targetEmail = customEmail || email;
		const targetPassword = customPassword !== undefined ? customPassword : password;

		if (!targetEmail) {
			notificationStore.toast('Silakan masukkan email Anda', 'error');
			loading = false;
			return;
		}

		const res = await authStore.login(targetEmail, targetPassword);
		if (res.success) {
			notificationStore.toast(`Masuk sebagai ${authStore.user?.name} (${authStore.user?.role})`, 'success');
			const target = (redirectUrl && !redirectUrl.startsWith('/login')) ? redirectUrl : '/dashboard';
			goto(target, { replaceState: true });
		} else {
			notificationStore.toast(res.error || 'Email atau kata sandi tidak valid', 'error');
		}
		loading = false;
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
				<span>{loading ? 'Memproses...' : 'Masuk'}</span>
				<ArrowRight class="w-4 h-4" />
			</Button>
		</form>
	</GlassSurface>
</div>
