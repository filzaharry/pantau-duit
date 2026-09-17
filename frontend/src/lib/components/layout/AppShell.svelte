<script lang="ts">
	import type { Snippet } from 'svelte';
	import Header from '$lib/components/layout/Header.svelte';
	import Sidebar from '$lib/components/layout/Sidebar.svelte';
	import BottomNav from '$lib/components/layout/BottomNav.svelte';
	import AddTransactionModal from '$lib/components/financial/AddTransactionModal.svelte';
	import MobileMenuSheet from '$lib/components/layout/MobileMenuSheet.svelte';

	interface Props {
		children?: Snippet;
	}

	let { children }: Props = $props();

	let sidebarCollapsed = $state(false);
	let isAddModalOpen = $state(false);
	let isMenuSheetOpen = $state(false);

</script>

<div class="min-h-screen flex flex-col bg-slate-50 dark:bg-[#0B0F19] text-slate-900 dark:text-slate-100 antialiased font-sans transition-colors duration-200">
	<!-- Top Navigation Header -->
	<Header />

	<!-- Layout Body: Sidebar docked to absolute left (x=0) -->
	<div class="flex-1 flex w-full">
		<!-- Desktop Collapsible Sidebar -->
		<Sidebar
			bind:collapsed={sidebarCollapsed}
			onToggleCollapse={() => (sidebarCollapsed = !sidebarCollapsed)}
			onOpenQuickAction={() => (isAddModalOpen = true)}
		/>

		<!-- Scrollable Main View Container with uniform max-w-7xl across all modules -->
		<main class="flex-1 flex flex-col min-w-0 px-4 sm:px-6 lg:px-8 py-4 sm:py-6 pb-28 lg:pb-12 overflow-x-hidden">
			<div class="w-full max-w-7xl mx-auto flex-1 flex flex-col">
				{@render children?.()}
			</div>
		</main>
	</div>

	<!-- Mobile Bottom Navigation (Visible only on <lg) -->
	<BottomNav
		onOpenQuickAction={() => (isAddModalOpen = true)}
		onOpenMenuSheet={() => (isMenuSheetOpen = true)}
	/>

	<!-- Global Modals & Sheets -->
	<AddTransactionModal bind:open={isAddModalOpen} />
	<MobileMenuSheet bind:open={isMenuSheetOpen} />
</div>
