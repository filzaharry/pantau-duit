<script lang="ts">
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth.svelte';
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import GlassSurface from '$lib/components/ui/GlassSurface.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import { ShieldCheck, ArrowRight, ArrowLeft } from 'lucide-svelte';

	let otpValues = $state(['', '', '', '', '', '']);
	let loading = $state(false);

	function handleInput(index: number, e: Event) {
		const target = e.target as HTMLInputElement;
		const val = target.value.slice(-1);
		otpValues[index] = val;

		if (val && index < 5) {
			const next = document.getElementById(`otp-box-${index + 1}`) as HTMLInputElement;
			next?.focus();
		}
	}

	function handleKeyDown(index: number, e: KeyboardEvent) {
		if (e.key === 'Backspace' && !otpValues[index] && index > 0) {
			const prev = document.getElementById(`otp-box-${index - 1}`) as HTMLInputElement;
			prev?.focus();
		}
	}

	async function handleVerify() {
		const code = otpValues.join('');
		if (code.length < 6) {
			notificationStore.toast('Masukkan 6 digit kode verifikasi.', 'error');
			return;
		}

		loading = true;
		await authStore.login('alex@example.com', 'otp-verified');
		notificationStore.toast('Otentikasi berhasil! Mengarahkan ke dasbor...', 'success');
		loading = false;
		goto('/dashboard');
	}
</script>

<div class="w-full max-w-md mx-auto my-auto py-8">
	<GlassSurface elevated class="p-8 rounded-3xl relative overflow-hidden">
		<div class="text-center mb-6">
			<div class="w-12 h-12 rounded-2xl bg-[#007AFF]/10 text-[#007AFF] flex items-center justify-center mx-auto mb-3">
				<ShieldCheck class="w-6 h-6" />
			</div>
			<h1 class="text-2xl font-semibold text-slate-900 dark:text-white tracking-tight">
				Verifikasi Kode OTP
			</h1>
			<p class="text-xs text-slate-500 dark:text-slate-400 mt-1">
				Masukkan 6-digit kode yang kami kirimkan ke Telegram Anda
			</p>
		</div>

		<!-- 6 Digit Input Boxes -->
		<div class="flex items-center justify-center gap-2 mb-6">
			{#each otpValues as digit, index}
				<input
					id={`otp-box-${index}`}
					type="text"
					inputmode="numeric"
					maxlength="1"
					value={digit}
					oninput={(e) => handleInput(index, e)}
					onkeydown={(e) => handleKeyDown(index, e)}
					class="w-11 h-13 text-center text-xl font-semibold rounded-xl border border-slate-200 dark:border-white/10 bg-white/70 dark:bg-white/5 text-slate-900 dark:text-white focus:outline-none focus:border-[#007AFF] focus:ring-2 focus:ring-[#007AFF]/20 transition-all"
				/>
			{/each}
		</div>

		<Button
			variant="primary"
			class="w-full"
			onclick={handleVerify}
			disabled={loading}
		>
			<span>{loading ? 'Memverifikasi...' : 'Verifikasi & Masuk'}</span>
			<ArrowRight class="w-4 h-4" />
		</Button>

		<div class="text-center mt-6 pt-4 border-t border-slate-100 dark:border-white/5 flex items-center justify-between text-xs">
			<a href="/login" class="text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 flex items-center gap-1">
				<ArrowLeft class="w-3.5 h-3.5" />
				<span>Kembali ke Login</span>
			</a>

			<button
				type="button"
				onclick={() => notificationStore.toast('Kode baru telah dikirimkan ke Telegram Anda!', 'info')}
				class="font-semibold text-[#007AFF] hover:underline"
			>
				Kirim Ulang Kode
			</button>
		</div>
	</GlassSurface>
</div>
