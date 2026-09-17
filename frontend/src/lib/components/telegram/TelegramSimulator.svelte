<script lang="ts">
	import { financialStore } from '$lib/stores/financial.svelte';
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import Button from '$lib/components/ui/Button.svelte';
	import GlassSurface from '$lib/components/ui/GlassSurface.svelte';
	import { Send, Bot, Check, Sparkles } from 'lucide-svelte';

	let inputText = $state('');
	let isProcessing = $state(false);

	interface Message {
		id: string;
		sender: 'user' | 'bot';
		text: string;
		parsedData?: {
			description: string;
			category: string;
			amount: number;
		};
		time: string;
	}

	let messages = $state<Message[]>([
		{
			id: 'm-1',
			sender: 'bot',
			text: 'Halo Budi! 👋 Saya bot Pantau-Duit. Ketik pengeluaranmu dengan format cepat contoh: "bakso;makanan;15000" atau bahasa santai seperti "tadi siang makan padang 25rb".',
			time: '09:00'
		}
	]);

	function parseQuickInput(text: string) {
		const parts = text.split(';').map((s) => s.trim());
		if (parts.length >= 3) {
			const desc = parts[0];
			const cat = parts[1];
			const amount = parseInt(parts[2].replace(/\D/g, ''), 10) || 0;
			return { description: desc, category: cat, amount };
		}

		// Basic Indonesian Natural Language Parser fallback
		let amount = 0;
		const numMatch = text.match(/(\d+[\d\.,]*)\s*(rb|ribu|k)?/i);
		if (numMatch) {
			let val = parseFloat(numMatch[1].replace(/\./g, '').replace(/,/g, '.'));
			if (numMatch[2] && /rb|ribu|k/i.test(numMatch[2])) {
				val *= 1000;
			}
			amount = Math.round(val);
		}

		let category = 'Food & Beverage';
		if (/bensin|ojek|grab|gojek|parkir|toll/i.test(text)) category = 'Transportation';
		if (/listrik|wifi|pulsa|token/i.test(text)) category = 'Utilities & Bills';
		if (/gaji|salary|bonus|freelance/i.test(text)) category = 'Salary';

		return {
			description: text,
			category,
			amount: amount || 20000
		};
	}

	async function handleSend() {
		if (!inputText.trim()) return;
		const userMsg = inputText.trim();
		inputText = '';

		const timeNow = new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' });

		// Add User message
		messages = [
			...messages,
			{
				id: 'm-' + Date.now(),
				sender: 'user',
				text: userMsg,
				time: timeNow
			}
		];

		isProcessing = true;

		// Simulate natural bot latency (400ms)
		setTimeout(() => {
			const parsed = parseQuickInput(userMsg);

			// Match category
			const matchedCat = financialStore.categories.find(
				(c) =>
					c.name.toLowerCase().includes(parsed.category.toLowerCase()) ||
					c.slug.toLowerCase().includes(parsed.category.toLowerCase())
			) || financialStore.categories[0];

			// Auto-record transaction into financial store
			financialStore.addTransaction({
				account_id: financialStore.accounts[0].id,
				category_id: matchedCat.id,
				amount: parsed.amount,
				transaction_type: 'EXPENSE',
				description: parsed.description,
				source: 'TELEGRAM',
				notes: `Dicatat dari Telegram: "${userMsg}"`
			});

			// Bot reply
			messages = [
				...messages,
				{
					id: 'm-' + Date.now(),
					sender: 'bot',
					text: `✅ Berhasil dicatat! Pengeluaran Rp ${parsed.amount.toLocaleString('id-ID')} untuk "${parsed.description}" dimasukkan ke kategori ${matchedCat.name}.`,
					parsedData: {
						description: parsed.description,
						category: matchedCat.name,
						amount: parsed.amount
					},
					time: new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })
				}
			];

			isProcessing = false;
		}, 400);
	}

	function sendExample(sample: string) {
		inputText = sample;
		handleSend();
	}
</script>

<div class="rounded-3xl bg-gradient-to-b from-white via-white/95 to-slate-50/80 dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border border-slate-200/70 dark:border-white/[0.06] flex flex-col h-[460px] sm:h-[520px] overflow-hidden">
	<!-- Simulator Header -->
	<div class="px-5 py-3.5 border-b border-slate-100 dark:border-white/5 flex items-center justify-between bg-slate-50/50 dark:bg-white/[0.02]">
		<div class="flex items-center gap-2.5">
			<div class="w-8 h-8 rounded-full bg-[#007AFF] text-white flex items-center justify-center">
				<Bot class="w-4 h-4" />
			</div>
			<div>
				<h4 class="text-xs sm:text-sm font-semibold text-slate-900 dark:text-white leading-none">
					@PantauDuitBot Simulator
				</h4>
				<span class="text-[10px] text-emerald-500 font-semibold flex items-center gap-1 mt-0.5">
					<span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
					Online • Webhook Active
				</span>
			</div>
		</div>

		<div class="flex items-center gap-1.5">
			<span class="text-[11px] font-semibold text-slate-400">Telegram Engine</span>
		</div>
	</div>

	<!-- Chat Area -->
	<div class="flex-1 p-4 sm:p-5 overflow-y-auto flex flex-col gap-3 no-scrollbar">
		{#each messages as msg}
			<div class="flex flex-col {msg.sender === 'user' ? 'items-end' : 'items-start'}">
				<div
					class="max-w-[85%] sm:max-w-[75%] px-4 py-2.5 rounded-2xl text-xs sm:text-sm leading-relaxed {msg.sender ===
					'user'
						? 'bg-[#007AFF] text-white rounded-br-sm'
						: 'bg-slate-50 dark:bg-[#191E2D] border border-slate-200/80 dark:border-white/10 text-slate-800 dark:text-slate-100 rounded-bl-sm'}"
				>
					{msg.text}

					{#if msg.parsedData}
						<div class="mt-2 pt-2 border-t border-slate-200/60 dark:border-white/10 text-[11px] text-slate-500 dark:text-slate-400 flex flex-col gap-0.5">
							<span>Nominal: <strong class="text-rose-500">Rp {msg.parsedData.amount.toLocaleString('id-ID')}</strong></span>
							<span>Kategori: {msg.parsedData.category}</span>
						</div>
					{/if}
				</div>
				<span class="text-[10px] text-slate-400 mt-1 px-1">{msg.time}</span>
			</div>
		{/each}

		{#if isProcessing}
			<div class="flex items-center gap-1.5 text-xs text-slate-400 italic px-2">
				<div class="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce"></div>
				<div class="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce [animation-delay:0.2s]"></div>
				<div class="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce [animation-delay:0.4s]"></div>
				<span>Bot sedang mencatat...</span>
			</div>
		{/if}
	</div>

	<!-- Quick Sample Prompts -->
	<div class="px-4 sm:px-5 py-2.5 border-t border-slate-100 dark:border-white/5 bg-slate-50/50 dark:bg-white/[0.01] flex items-center gap-1.5 overflow-x-auto no-scrollbar">
		<span class="text-[10px] font-semibold text-slate-400 shrink-0">Contoh Cepat:</span>
		<button
			type="button"
			onclick={() => sendExample('bakso;makanan;15000')}
			class="text-[11px] px-2.5 py-1 rounded-full bg-white dark:bg-[#191E2D] border border-slate-200 dark:border-white/10 text-slate-700 dark:text-slate-300 hover:border-[#007AFF] transition-colors shrink-0"
		>
			bakso;makanan;15000
		</button>
		<button
			type="button"
			onclick={() => sendExample('tadi beli bensin 35rb')}
			class="text-[11px] px-2.5 py-1 rounded-full bg-white dark:bg-[#191E2D] border border-slate-200 dark:border-white/10 text-slate-700 dark:text-slate-300 hover:border-[#007AFF] transition-colors shrink-0"
		>
			tadi beli bensin 35rb
		</button>
		<button
			type="button"
			onclick={() => sendExample('kopi kenangan;makanan;22000')}
			class="text-[11px] px-2.5 py-1 rounded-full bg-white dark:bg-[#191E2D] border border-slate-200 dark:border-white/10 text-slate-700 dark:text-slate-300 hover:border-[#007AFF] transition-colors shrink-0"
		>
			kopi kenangan;22rb
		</button>
	</div>

	<!-- Input Bar -->
	<form
		onsubmit={(e) => {
			e.preventDefault();
			handleSend();
		}}
		class="p-3 sm:p-4 border-t border-slate-100 dark:border-white/5 flex items-center gap-2 bg-white dark:bg-[#131620]"
	>
		<input
			type="text"
			bind:value={inputText}
			placeholder="Ketik pengeluaranmu (misal: bakso 15rb)..."
			class="flex-1 h-11 px-4 text-xs sm:text-sm rounded-xl bg-slate-100 dark:bg-white/[0.05] border border-transparent focus:border-[#007AFF] focus:bg-white dark:focus:bg-[#191E2D] outline-none text-slate-900 dark:text-white transition-all"
		/>
		<Button type="submit" size="md" variant="primary" disabled={!inputText.trim() || isProcessing}>
			<Send class="w-4 h-4" />
		</Button>
	</form>
</div>
