<script lang="ts">
	import { financialStore } from '$lib/stores/financial.svelte';
	import SearchableSelect from '$lib/components/ui/SearchableSelect.svelte';

	interface Props {
		value?: string;
		categoryType?: 'EXPENSE' | 'INCOME' | 'ALL';
		label?: string;
		placeholder?: string;
		error?: string;
		disabled?: boolean;
	}

	let {
		value = $bindable(''),
		categoryType = 'EXPENSE',
		label = 'Kategori',
		placeholder = 'Ketik atau pilih kategori...',
		error,
		disabled = false
	}: Props = $props();

	const availableCategories = $derived(
		financialStore.categories.filter((c) => {
			if (categoryType === 'ALL') return true;
			return c.type === categoryType || c.type === 'BOTH';
		})
	);

	const categoryOptions = $derived(
		availableCategories.map((c) => ({
			value: c.id,
			label: c.name
		}))
	);

	async function handleCreateCategory(name: string): Promise<string | void> {
		const created = await financialStore.addCategory({
			name: name.trim(),
			type: categoryType === 'ALL' ? 'EXPENSE' : categoryType,
			color: '#007AFF'
		});
		return created?.id;
	}
</script>

<SearchableSelect
	bind:value
	options={categoryOptions}
	{label}
	{placeholder}
	{error}
	{disabled}
	allowCreate={true}
	onCreate={handleCreateCategory}
/>
