<script lang="ts">
	interface Props {
		value: number;
		variant?: 'blue' | 'emerald' | 'amber' | 'rose' | 'purple' | 'auto';
		size?: 'sm' | 'md' | 'lg';
		showRadar?: boolean;
		class?: string;
	}

	let {
		value = 0,
		variant = 'blue',
		size = 'md',
		showRadar = true,
		class: className = ''
	}: Props = $props();

	const clampedValue = $derived(Math.max(0, Math.min(100, isNaN(value) ? 0 : value)));

	// Auto-detect variant based on percentage if set to auto
	const resolvedVariant = $derived.by(() => {
		if (variant !== 'auto') return variant;
		if (clampedValue >= 100) return 'rose';
		if (clampedValue >= 80) return 'amber';
		return 'blue';
	});

	const sizeClasses = $derived.by(() => {
		switch (size) {
			case 'sm':
				return 'h-1.5';
			case 'lg':
				return 'h-3';
			case 'md':
			default:
				return 'h-2';
		}
	});

	const gradientClasses = $derived.by(() => {
		switch (resolvedVariant) {
			case 'emerald':
				return 'bg-gradient-to-r from-emerald-600 via-emerald-500 to-teal-300';
			case 'amber':
				return 'bg-gradient-to-r from-amber-600 via-amber-500 to-yellow-300';
			case 'rose':
				return 'bg-gradient-to-r from-rose-600 via-rose-500 to-pink-400';
			case 'purple':
				return 'bg-gradient-to-r from-indigo-600 via-purple-500 to-pink-400';
			case 'blue':
			default:
				return 'bg-gradient-to-r from-blue-600 via-[#007AFF] to-cyan-300';
		}
	});

	const radarGlowClasses = $derived.by(() => {
		switch (resolvedVariant) {
			case 'emerald':
				return { ripple: 'bg-teal-400', shadow: 'shadow-[0_0_8px_#10B981]' };
			case 'amber':
				return { ripple: 'bg-yellow-400', shadow: 'shadow-[0_0_8px_#F59E0B]' };
			case 'rose':
				return { ripple: 'bg-pink-400', shadow: 'shadow-[0_0_8px_#F43F5E]' };
			case 'purple':
				return { ripple: 'bg-purple-400', shadow: 'shadow-[0_0_8px_#A855F7]' };
			case 'blue':
			default:
				return { ripple: 'bg-cyan-400', shadow: 'shadow-[0_0_8px_#007AFF]' };
		}
	});

	const radarSize = $derived.by(() => {
		switch (size) {
			case 'sm':
				return { ripple: 'w-3 h-3', dot: 'w-1.5 h-1.5' };
			case 'lg':
				return { ripple: 'w-5 h-5', dot: 'w-2.5 h-2.5' };
			case 'md':
			default:
				return { ripple: 'w-4 h-4', dot: 'w-2 h-2' };
		}
	});
</script>

<div class="relative w-full {sizeClasses} rounded-full bg-slate-100 dark:bg-white/10 {className}">
	<!-- Filled Bar with Gradient -->
	<div
		class="relative h-full rounded-full transition-all duration-500 ease-out {gradientClasses}"
		style="width: {clampedValue}%;"
	>
		<!-- Radar Blinking Animation at the Tip -->
		{#if showRadar && clampedValue > 0}
			<div
				class="absolute right-0 top-1/2 -translate-y-1/2 translate-x-1/2 z-10 flex items-center justify-center pointer-events-none"
				aria-hidden="true"
			>
				<!-- Radar Expanding Wave Ripple -->
				<span
					class="absolute {radarSize.ripple} rounded-full {radarGlowClasses.ripple} radar-ripple"
				></span>
				<!-- Radar Glowing Ambient Pulse -->
				<span
					class="absolute {radarSize.ripple} rounded-full bg-white/40 radar-glow"
				></span>
				<!-- Radar Center High-Intensity Beacon Core -->
				<span
					class="relative {radarSize.dot} rounded-full bg-white {radarGlowClasses.shadow} ring-1 ring-white/80"
				></span>
			</div>
		{/if}
	</div>
</div>
