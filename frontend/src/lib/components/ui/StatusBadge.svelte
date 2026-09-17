<script lang="ts">
	import {
		getEmployeeStatusInfo,
		getPayrollStatusInfo,
		getLeaveStatusInfo,
		getReimbursementStatusInfo,
		type StatusVariant
	} from '$lib/utils/status';

	interface Props {
		status: number;
		type?: 'employee' | 'payroll' | 'leave' | 'reimbursement' | 'custom';
		customLabel?: string;
		customVariant?: StatusVariant;
		showDot?: boolean;
		size?: 'xs' | 'sm' | 'md';
		class?: string;
	}

	let {
		status,
		type = 'employee',
		customLabel,
		customVariant,
		showDot = true,
		size = 'sm',
		class: customClass = ''
	}: Props = $props();

	const info = $derived.by(() => {
		if (type === 'custom' && customLabel) {
			return {
				label: customLabel,
				badgeClass: customVariant === 'success'
					? 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20'
					: customVariant === 'warning'
					? 'bg-amber-500/10 text-amber-600 border-amber-500/20'
					: customVariant === 'error'
					? 'bg-rose-500/10 text-rose-600 border-rose-500/20'
					: 'bg-blue-500/10 text-blue-600 border-blue-500/20',
				dotClass: customVariant === 'success'
					? 'bg-emerald-500'
					: customVariant === 'warning'
					? 'bg-amber-500'
					: customVariant === 'error'
					? 'bg-rose-500'
					: 'bg-blue-500',
				description: ''
			};
		}
		if (type === 'payroll') return getPayrollStatusInfo(status);
		if (type === 'leave') return getLeaveStatusInfo(status);
		if (type === 'reimbursement') return getReimbursementStatusInfo(status);
		return getEmployeeStatusInfo(status);
	});

	const sizeClasses = {
		xs: 'px-1.5 py-0.5 text-[10px] gap-1',
		sm: 'px-2 py-0.5 text-[11px] gap-1.5',
		md: 'px-2.5 py-1 text-xs gap-1.5'
	};

	const dotSizes = {
		xs: 'w-1 h-1',
		sm: 'w-1.5 h-1.5',
		md: 'w-2 h-2'
	};
</script>

<span
	class="inline-flex items-center font-semibold rounded-full border transition-all {sizeClasses[size]} {info.badgeClass} {customClass}"
	title="{info.label}: {info.description}"
>
	{#if showDot}
		<span class="rounded-full shrink-0 {dotSizes[size]} {info.dotClass}"></span>
	{/if}
	<span>{info.label}</span>
</span>
