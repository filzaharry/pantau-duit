<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	onMount(() => {
		goto('/login');
	});
</script>

<div class="min-h-screen flex items-center justify-center p-4">
	<p class="text-sm text-slate-500">Mengarahkan ke halaman masuk...</p>
</div>
