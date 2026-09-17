<script lang="ts">
	interface Props {
		class?: string;
		rounded?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
	}

	let { class: className = '', rounded = 'xl' }: Props = $props();

	const roundedClasses = {
		sm: 'rounded-md',
		md: 'rounded-lg',
		lg: 'rounded-xl',
		xl: 'rounded-2xl',
		full: 'rounded-full'
	};
</script>

<div
	class="animate-pulse bg-slate-200/70 dark:bg-white/5 {roundedClasses[rounded]} {className}"
	aria-hidden="true"
></div>
