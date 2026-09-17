<script lang="ts">
	import Modal from '$lib/components/ui/Modal.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import { formatRelativeTime } from '$lib/utils/formatters';
	import {
		Bell,
		CheckCircle2,
		AlertTriangle,
		Info,
		Sparkles,
		CheckCheck
	} from 'lucide-svelte';

	interface Props {
		open?: boolean;
		onclose?: () => void;
	}

	let { open = $bindable(false), onclose }: Props = $props();

	function getNotificationIcon(type: string) {
		switch (type) {
			case 'SUCCESS':
				return CheckCircle2;
			case 'WARNING':
				return AlertTriangle;
			case 'ERROR':
				return AlertTriangle;
			case 'PROMOTION':
				return Sparkles;
			default:
				return Info;
		}
	}

	function getNotificationColor(type: string) {
		switch (type) {
			case 'SUCCESS':
				return 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20';
			case 'WARNING':
				return 'text-amber-500 bg-amber-500/10 border-amber-500/20';
			case 'ERROR':
				return 'text-rose-500 bg-rose-500/10 border-rose-500/20';
			case 'PROMOTION':
				return 'text-purple-500 bg-purple-500/10 border-purple-500/20';
			default:
				return 'text-[#007AFF] bg-[#007AFF]/10 border-[#007AFF]/20';
		}
	}
</script>

<Modal
	bind:open
	title="Notifikasi & Peringatan"
	description="{notificationStore.unreadCount} belum dibaca"
	{onclose}
>
	<div class="space-y-3">
		{#if notificationStore.notifications.length > 0}
			<div class="flex items-center justify-between pb-1">
				<span class="text-xs font-semibold text-slate-500 dark:text-slate-400">
					Terbaru
				</span>
				<button
					type="button"
					onclick={() => notificationStore.markAllAsRead()}
					class="text-xs font-semibold text-[#007AFF] dark:text-[#0A84FF] hover:underline flex items-center gap-1"
				>
					<CheckCheck class="w-3.5 h-3.5" />
					<span>Tandai Semua Dibaca</span>
				</button>
			</div>

			<div class="space-y-2 max-h-[60vh] overflow-y-auto no-scrollbar">
				{#each notificationStore.notifications as item}
					{@const Icon = getNotificationIcon(item.type)}
					<div
						class="p-3.5 rounded-2xl border transition-all flex items-start gap-3 {!item.is_read
							? 'bg-[#007AFF]/5 dark:bg-[#0A84FF]/10 border-[#007AFF]/20'
							: 'bg-white dark:bg-white/[0.02] border-slate-200/70 dark:border-white/5 opacity-80'}"
					>
						<div
							class="w-8 h-8 rounded-xl shrink-0 flex items-center justify-center border {getNotificationColor(item.type)}"
						>
							<Icon class="w-4 h-4" />
						</div>

						<div class="flex-1 min-w-0">
							<div class="flex items-center justify-between gap-1">
								<h4 class="text-xs font-semibold text-slate-900 dark:text-white truncate">
									{item.title}
								</h4>
								<span class="text-[10px] text-slate-400 shrink-0">
									{formatRelativeTime(item.created_at)}
								</span>
							</div>
							<p class="text-xs text-slate-600 dark:text-slate-300 mt-0.5 leading-relaxed">
								{item.message}
							</p>
						</div>

						{#if !item.is_read}
							<button
								type="button"
								onclick={() => notificationStore.markAsRead(item.id)}
								class="w-2 h-2 rounded-full bg-[#007AFF] shrink-0 mt-2"
								title="Tandai sudah dibaca"
								aria-label="Tandai sudah dibaca"
							></button>
						{/if}
					</div>
				{/each}
			</div>

			<div class="pt-2 text-center">
				<a
					href="/notifications"
					onclick={() => (open = false)}
					class="text-xs font-semibold text-[#007AFF] dark:text-[#0A84FF] hover:underline"
				>
					Lihat Semua Riwayat Notifikasi &rarr;
				</a>
			</div>
		{:else}
			<div class="py-12 text-center flex flex-col items-center">
				<div class="w-12 h-12 rounded-2xl bg-slate-100 dark:bg-white/5 flex items-center justify-center text-slate-400 mb-3">
					<Bell class="w-6 h-6" />
				</div>
				<p class="text-sm font-semibold text-slate-900 dark:text-white">Tidak ada notifikasi</p>
				<p class="text-xs text-slate-400 mt-1">Anda sudah melihat seluruh pembaruan sistem.</p>
			</div>
		{/if}
	</div>
</Modal>
