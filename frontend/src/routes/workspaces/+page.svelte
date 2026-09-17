<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	onMount(() => {
		goto('/users', { replaceState: true });
	});
</script>

<div class="p-8 text-center text-slate-400 text-xs">
	Mengalihkan ke Manajemen Pengguna...
</div>
