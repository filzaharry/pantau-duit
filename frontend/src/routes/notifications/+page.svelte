<script lang="ts">
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import { formatDateTime, formatRelativeTime } from '$lib/utils/formatters';
	import GlassSurface from '$lib/components/ui/GlassSurface.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import EmptyState from '$lib/components/ui/EmptyState.svelte';
	import {
		Bell,
		CheckCircle2,
		AlertTriangle,
		Info,
		Sparkles,
		CheckCheck,
		Trash2
	} from 'lucide-svelte';

	let filterUnreadOnly = $state(false);

	const displayedNotifications = $derived(
		filterUnreadOnly
			? notificationStore.notifications.filter((n) => !n.is_read)
			: notificationStore.notifications
	);

	function getIcon(type: string) {
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

	function getColor(type: string) {
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

<div class="space-y-6 max-w-7xl mx-auto w-full">
	<!-- Page Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
		<div>
			<h1 class="text-xl sm:text-2xl font-semibold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
				<Bell class="w-6 h-6 text-rose-500" />
				<span>Pusat Notifikasi</span>
			</h1>
			<p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
				Peringatan overbudget, ringkasan transaksi Telegram, dan info sistem
			</p>
		</div>

		<div class="flex items-center gap-2 self-start sm:self-auto">
			<Button variant="outline" onclick={() => notificationStore.markAllAsRead()}>
				<CheckCheck class="w-4 h-4" />
				<span>Tandai Semua Dibaca</span>
			</Button>
		</div>
	</div>

	<!-- Filter Tabs -->
	<div class="flex items-center gap-2">
		<button
			type="button"
			onclick={() => (filterUnreadOnly = false)}
			class="px-3.5 py-1.5 rounded-full text-xs font-semibold transition-colors {!filterUnreadOnly
				? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900'
				: 'bg-slate-100 dark:bg-white/5 text-slate-600 dark:text-slate-400'}"
		>
			Semua ({notificationStore.notifications.length})
		</button>

		<button
			type="button"
			onclick={() => (filterUnreadOnly = true)}
			class="px-3.5 py-1.5 rounded-full text-xs font-semibold transition-colors {filterUnreadOnly
				? 'bg-[#007AFF] text-white'
				: 'bg-slate-100 dark:bg-white/5 text-slate-600 dark:text-slate-400'}"
		>
			Belum Dibaca ({notificationStore.unreadCount})
		</button>
	</div>

	<!-- Notifications List -->
	<div class="rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] divide-y divide-slate-100 dark:divide-white/5 overflow-hidden">
		{#if displayedNotifications.length > 0}
			{#each displayedNotifications as item (item.id)}
				{@const Icon = getIcon(item.type)}
				<div
					class="p-4 sm:p-5 flex items-start justify-between gap-4 transition-all {!item.is_read
						? 'bg-blue-50/40 dark:bg-[#007AFF]/[0.06]'
						: 'hover:bg-slate-50/60 dark:hover:bg-white/[0.02]'}"
				>
					<div class="flex items-start gap-3.5 flex-1 min-w-0">
						<div class="w-10 h-10 rounded-2xl shrink-0 flex items-center justify-center border {getColor(item.type)}">
							<Icon class="w-5 h-5" />
						</div>

						<div class="flex-1 min-w-0">
							<div class="flex items-center gap-2">
								<h3 class="text-sm font-semibold text-slate-900 dark:text-white truncate">
									{item.title}
								</h3>
								{#if !item.is_read}
									<span class="w-2 h-2 rounded-full bg-[#007AFF] shrink-0"></span>
								{/if}
							</div>
							<p class="text-xs text-slate-600 dark:text-slate-300 mt-1 leading-relaxed">
								{item.message}
							</p>
							<span class="text-[11px] text-slate-400 mt-2 inline-block">
								{formatDateTime(item.created_at)} ({formatRelativeTime(item.created_at)})
							</span>
						</div>
					</div>

					<div class="flex items-center gap-1 shrink-0">
						{#if !item.is_read}
							<button
								type="button"
								onclick={() => notificationStore.markAsRead(item.id)}
								class="p-2 rounded-xl text-slate-400 hover:text-[#007AFF] hover:bg-slate-100 dark:hover:bg-white/5 transition-colors"
								title="Tandai dibaca"
								aria-label="Tandai dibaca"
							>
								<CheckCheck class="w-4 h-4" />
							</button>
						{/if}

						<button
							type="button"
							onclick={() => notificationStore.deleteNotification(item.id)}
							class="p-2 rounded-xl text-slate-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/30 transition-colors"
							title="Hapus notifikasi"
							aria-label="Hapus notifikasi"
						>
							<Trash2 class="w-4 h-4" />
						</button>
					</div>
				</div>
			{/each}
		{:else}
			<EmptyState
				title="Tidak ada notifikasi"
				description={filterUnreadOnly
					? 'Semua notifikasi penting telah Anda baca.'
					: 'Belum ada notifikasi baru di sistem.'}
			/>
		{/if}
	</div>
</div>
