<script lang="ts">
	import { authStore } from '$lib/stores/auth.svelte';
	import UserDashboard from '$lib/components/dashboard/UserDashboard.svelte';
	import SuperAdminDashboard from '$lib/components/dashboard/SuperAdminDashboard.svelte';
</script>

{#if authStore.isSuperuser}
	<SuperAdminDashboard />
{:else}
	<UserDashboard />
{/if}
