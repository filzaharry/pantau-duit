<script lang="ts">
	interface Props {
		checked?: boolean;
		label?: string;
		description?: string;
		disabled?: boolean;
		onchange?: (checked: boolean) => void;
	}

	let {
		checked = $bindable(false),
		label,
		description,
		disabled = false,
		onchange
	}: Props = $props();

	function toggle() {
		if (disabled) return;
		checked = !checked;
		onchange?.(checked);
	}
</script>

<label class="inline-flex items-center justify-between gap-3 cursor-pointer select-none group">
	{#if label || description}
		<div class="flex flex-col">
			{#if label}
				<span class="text-sm font-medium text-slate-900 dark:text-slate-100">{label}</span>
			{/if}
			{#if description}
				<span class="text-xs text-slate-500 dark:text-slate-400">{description}</span>
			{/if}
		</div>
	{/if}

	<button
		type="button"
		role="switch"
		aria-label={label || 'Pilihan saklar'}
		aria-checked={checked}
		{disabled}
		onclick={toggle}
		class="relative inline-flex h-7 w-12 shrink-0 cursor-pointer rounded-full p-0.5 transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-[#007AFF]/20 {checked
			? 'bg-[#007AFF]'
			: 'bg-slate-300 dark:bg-slate-700'} disabled:opacity-50"
	>
		<span
			class="pointer-events-none inline-block h-6 w-6 transform rounded-full bg-white shadow-sm ring-0 transition duration-200 ease-in-out {checked
				? 'translate-x-5'
				: 'translate-x-0'}"
		></span>
	</button>
</label>
