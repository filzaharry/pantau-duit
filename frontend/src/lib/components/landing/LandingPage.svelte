<script lang="ts">
	import { authStore } from '$lib/stores/auth.svelte';
	import { themeStore } from '$lib/stores/theme.svelte';
	import { notificationStore } from '$lib/stores/notifications.svelte';
	import { formatRupiah } from '$lib/utils/formatters';
	import {
		Send,
		Shield,
		Bot,
		Sparkles,
		Check,
		ChevronRight,
		ArrowRight,
		Zap,
		PieChart,
		Wallet,
		CreditCard,
		Building2,
		Users,
		Lock,
		Sun,
		Moon,
		Menu,
		X,
		ArrowUpRight,
		TrendingUp,
		Target,
		Receipt,
		CheckCircle2,
		Star,
		HelpCircle,
		Smartphone,
		Eye,
		MessageSquare,
		Clock,
		Coins,
		BarChart3,
		FileSpreadsheet
	} from 'lucide-svelte';

	// Billing cycle toggle
	let billingCycle = $state<'monthly' | 'yearly'>('monthly');

	// Workspace preview tabs
	let activeWorkspaceTab = $state<'personal' | 'family' | 'business'>('personal');

	// Mobile Navigation Menu state
	let isMobileMenuOpen = $state(false);

	// FAQ Accordion active index
	let activeFaqIndex = $state<number | null>(0);

	function toggleFaq(index: number) {
		activeFaqIndex = activeFaqIndex === index ? null : index;
	}

	function toggleTheme() {
		themeStore.setTheme(themeStore.isDark ? 'light' : 'dark');
	}

	// Interactive Telegram Simulator on Landing Page
	let simInput = $state('');
	let isSimTyping = $state(false);

	interface SimMessage {
		id: string;
		sender: 'user' | 'bot';
		text: string;
		time: string;
		parsed?: {
			category: string;
			amount: number;
			account: string;
		};
	}

	let simMessages = $state<SimMessage[]>([
		{
			id: 'm1',
			sender: 'bot',
			text: 'Halo! 👋 Saya bot PantauDuit. Coba ketik pengeluaranmu, misal: "kopi kenangan 28rb" atau "isi bensin shell 100k".',
			time: '10:30'
		},
		{
			id: 'm2',
			sender: 'user',
			text: 'kopi americano 28rb',
			time: '10:31'
		},
		{
			id: 'm3',
			sender: 'bot',
			text: '✅ Transaksi berhasil dicatat!\n🍔 Kategori: Makanan & Minuman\n💳 Sumber: GoPay\n💰 Nominal: Rp 28.000\nSisa budget pos jajan bulan ini: Rp 472.000 (Aman)',
			time: '10:31',
			parsed: {
				category: 'Makanan & Minuman',
				amount: 28000,
				account: 'GoPay'
			}
		}
	]);

	const quickPrompts = [
		'nasi padang 25rb',
		'bensin pertamax 100k',
		'gaji freelance 2.5jt',
		'netflix bulanan 65rb'
	];

	function handleQuickPrompt(text: string) {
		simInput = text;
		sendSimMessage();
	}

	function sendSimMessage() {
		if (!simInput.trim()) return;
		const userText = simInput.trim();
		simInput = '';

		const timeNow = new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' });

		// Add user message
		simMessages = [
			...simMessages,
			{
				id: `usr-${Date.now()}`,
				sender: 'user',
				text: userText,
				time: timeNow
			}
		];

		isSimTyping = true;

		// Simulated AI Parsing
		setTimeout(() => {
			let amount = 30000;
			const numMatch = userText.match(/(\d+[\d\.,]*)\s*(jt|juta|rb|ribu|k)?/i);
			if (numMatch) {
				let val = parseFloat(numMatch[1].replace(/\./g, '').replace(/,/g, '.'));
				const unit = (numMatch[2] || '').toLowerCase();
				if (unit === 'jt' || unit === 'juta') val *= 1000000;
				else if (unit === 'rb' || unit === 'ribu' || unit === 'k') val *= 1000;
				amount = Math.round(val);
			}

			let category = 'Makanan & Minuman';
			let account = 'BCA Prioritas';
			let isIncome = false;

			if (/bensin|pertamax|shell|ojek|grab|gojek|toll|parkir/i.test(userText)) {
				category = 'Transportasi';
				account = 'GoPay';
			} else if (/gaji|salary|bonus|freelance|transfer/i.test(userText)) {
				category = 'Pendapatan';
				account = 'BCA Tabungan';
				isIncome = true;
			} else if (/netflix|spotify|pulsa|listrik|wifi|tagihan/i.test(userText)) {
				category = 'Tagihan & Utilitas';
				account = 'Mandiri Debit';
			}

			const botReply: SimMessage = {
				id: `bot-${Date.now()}`,
				sender: 'bot',
				text: isIncome
					? `🎉 Pemasukan berhasil masuk!\n📈 Kategori: ${category}\n🏦 Rekening: ${account}\n💰 Nominal: +${formatRupiah(amount)}\nSaldo bertambah dan grafik keuangan telah diperbarui!`
					: `✅ Pengeluaran tercatat!\n🏷️ Kategori: ${category}\n💳 Sumber: ${account}\n💸 Nominal: -${formatRupiah(amount)}\nDashboard dan batas anggaran Anda langsung diselaraskan!`,
				time: new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' }),
				parsed: {
					category,
					amount,
					account
				}
			};

			simMessages = [...simMessages, botReply];
			isSimTyping = false;
			notificationStore.toast('Simulasi Telegram berhasil diparsing!', 'success');
		}, 600);
	}

	const plans = [
		{
			id: 'free',
			name: 'Starter',
			tagline: 'Gratis Selamanya',
			priceMonthly: 0,
			priceYearly: 0,
			description: 'Ideal untuk individu yang baru mulai membiasakan pencatatan pengeluaran harian.',
			badge: 'Pemula',
			features: [
				'Maksimal 2 Rekening / Dompet Digital',
				'Maksimal 50 chat Telegram / bulan',
				'Pencatatan Pemasukan & Pengeluaran',
				'Grafik Ringkasan Bulanan',
				'Dukungan Komunitas Telegram'
			],
			buttonText: 'Mulai Gratis',
			popular: false
		},
		{
			id: 'pro',
			name: 'Pro Member',
			tagline: 'Pilihan Paling Populer',
			priceMonthly: 49000,
			priceYearly: 470000, // Hemat ~20%
			description: 'Bagi profesional yang ingin kemudahan catat cepat tanpa batas dan analisis cerdas.',
			badge: 'Paling Diminati ⭐',
			features: [
				'Chat Telegram Unlimited (Tanpa Batas)',
				'Hingga 20 Rekening Bank & E-Wallet',
				'AI Natural Language Parser Bahasa Indonesia',
				'Budgeting & Batas Belanja Tak Terbatas',
				'Target Tabungan dengan Glow Radar',
				'Laporan Lengkap & Ekspor Excel/PDF',
				'Dukungan Prioritas Responsif'
			],
			buttonText: 'Pilih Pro Member',
			popular: true
		},
		{
			id: 'enterprise',
			name: 'Family & Bisnis',
			tagline: 'Kolaborasi Lengkap',
			priceMonthly: 149000,
			priceYearly: 1430000,
			description: 'Untuk keluarga atau UMKM yang membutuhkan multi-user dan tata kelola terpadu.',
			badge: 'Multi-User',
			features: [
				'Semua fitur paket Pro Member',
				'Multi-User RBAC (Role-Based Access Control)',
				'Instance Bot Telegram Khusus',
				'Modul Perusahaan (HR, Shift & Payroll)',
				'Audit Trail Keuangan Anti-Hapus',
				'Akses API & Webhook Kustom',
				'Konsultasi Perencana Keuangan'
			],
			buttonText: 'Pilih Family & Bisnis',
			popular: false
		}
	];

	const faqs = [
		{
			q: 'Bagaimana cara kerja pencatatan via Telegram Bot?',
			a: 'Sangat simpel! Anda cukup menghubungkan akun Telegram Anda sekali saja melalui kode OTP atau klik satu kali. Setelah terhubung, setiap kali Anda bertransaksi, cukup kirim chat biasa seperti "kopi 25rb" atau "beli bensin 50k". AI kami otomatis mengenali jenis transaksi, nominal, dan kategorinya lalu menyimpannya ke database dashboard Anda.'
		},
		{
			q: 'Apakah data keuangan dan saldo saya aman?',
			a: 'Keamanan dan privasi adalah fondasi PantauDuit. Semua data disimpan dengan enkripsi bank-grade AES-256. Kami tidak pernah meminta kredensial perbankan Anda (password/PIN/OTP bank). Anda memegang kendali penuh atas data Anda, termasuk fitur Incognito Mode untuk menyembunyikan nominal saldo saat berada di ruang publik.'
		},
		{
			q: 'Apakah bisa digunakan untuk mencatat keuangan keluarga bersama pasangan?',
			a: 'Ya, tentu! Melalui Workspace Family, Anda dan pasangan dapat berbagi akun/rekening tertentu (misalnya rekening belanja bersama) dengan hak akses yang dapat diatur, sementara rekening pribadi masing-masing tetap terlindungi secara privat.'
		},
		{
			q: 'Bagaimana cara mencoba fitur sebelum berlangganan?',
			a: 'Tentu! Anda dapat langsung masuk melalui halaman login untuk mengeksplorasi seluruh modul fitur finansial, budgeting, dan pencatatan bot Telegram.'
		},
		{
			q: 'Apakah ada batasan jenis bank atau e-wallet yang didukung?',
			a: 'PantauDuit mendukung semua bank di Indonesia (BCA, Mandiri, BRI, BNI, CIMB, Jago, Jenius, dsb), seluruh e-wallet (GoPay, OVO, ShopeePay, DANA), uang tunai (cash wallet), hingga aset investasi seperti Bibit, Reksa Dana, Saham, dan Aset Kripto.'
		}
	];
</script>

<div class="w-full bg-slate-50 dark:bg-[#0B0F19] text-slate-900 dark:text-slate-100 selection:bg-[#007AFF]/20 selection:text-[#007AFF]">
	<!-- ========================================================================= -->
	<!-- 1. STICKY TOP NAVIGATION BAR (Glassmorphism iOS Vibe) -->
	<!-- ========================================================================= -->
	<header class="sticky top-0 z-50 w-full bg-white/80 dark:bg-[#0B0F19]/80 backdrop-blur-xl border-b border-slate-200/70 dark:border-white/10 transition-colors duration-200">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 sm:h-20 flex items-center justify-between">
			<!-- Brand Logo -->
			<a href="/" class="flex items-center gap-2.5 group select-none">
				<div class="w-10 h-10 rounded-2xl bg-gradient-to-br from-[#007AFF] to-[#0055B3] text-white flex items-center justify-center font-bold text-xl shadow-lg shadow-[#007AFF]/25 group-hover:scale-105 transition-transform">
					P
				</div>
				<div class="flex flex-col">
					<div class="flex items-center gap-2">
						<span class="text-lg sm:text-xl font-bold tracking-tight text-slate-900 dark:text-white leading-none">
							Pantau<span class="text-[#007AFF] dark:text-[#0A84FF]">Duit</span>
						</span>
						<span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-[#0088cc]/10 text-[#0088cc] border border-[#0088cc]/20 hidden sm:inline-block">
							Telegram-First
						</span>
					</div>
					<span class="text-[11px] text-slate-500 dark:text-slate-400 font-medium">Personal Finance Command Center</span>
				</div>
			</a>

			<!-- Desktop Navigation Links -->
			<nav class="hidden md:flex items-center gap-8 text-sm font-medium text-slate-600 dark:text-slate-300">
				<a href="#features" class="hover:text-[#007AFF] dark:hover:text-[#0A84FF] transition-colors">Fitur Unggulan</a>
				<a href="#telegram" class="hover:text-[#007AFF] dark:hover:text-[#0A84FF] transition-colors">Simulasi Telegram</a>
				<a href="#workspaces" class="hover:text-[#007AFF] dark:hover:text-[#0A84FF] transition-colors">Solusi Workspace</a>
				<a href="#pricing" class="hover:text-[#007AFF] dark:hover:text-[#0A84FF] transition-colors">Harga</a>
				<a href="#faq" class="hover:text-[#007AFF] dark:hover:text-[#0A84FF] transition-colors">FAQ</a>
			</nav>

			<!-- Right CTAs & Theme Toggle -->
			<div class="flex items-center gap-2.5 sm:gap-4">
				<!-- Theme Switcher Button -->
				<button
					type="button"
					onclick={toggleTheme}
					aria-label="Ganti Mode Tampilan"
					class="p-2 sm:p-2.5 rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/10 transition-colors"
				>
					{#if themeStore.isDark}
						<Sun class="w-4 h-4 sm:w-5 sm:h-5 text-amber-400" />
					{:else}
						<Moon class="w-4 h-4 sm:w-5 sm:h-5 text-slate-700" />
					{/if}
				</button>

				<!-- Primary CTA: Masuk -->
				<a
					href="/login"
					class="inline-flex items-center gap-1.5 px-3.5 sm:px-5 py-2 sm:py-2.5 rounded-xl sm:rounded-2xl bg-gradient-to-r from-[#007AFF] to-[#0062CC] hover:from-[#0069D9] hover:to-[#0055B3] text-white text-xs sm:text-sm font-semibold shadow-md shadow-[#007AFF]/25 transition-all active:scale-[0.98]"
				>
					<span>Masuk</span>
					<ChevronRight class="w-4 h-4" />
				</a>

				<!-- Mobile Menu Button -->
				<button
					type="button"
					onclick={() => (isMobileMenuOpen = !isMobileMenuOpen)}
					aria-label="Toggle Menu"
					class="md:hidden p-2 rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/10"
				>
					{#if isMobileMenuOpen}
						<X class="w-6 h-6" />
					{:else}
						<Menu class="w-6 h-6" />
					{/if}
				</button>
			</div>
		</div>

		<!-- Mobile Dropdown Menu -->
		{#if isMobileMenuOpen}
			<div class="md:hidden bg-white/95 dark:bg-[#0B0F19]/95 backdrop-blur-xl border-b border-slate-200 dark:border-white/10 px-4 py-4 space-y-3">
				<a
					href="#features"
					onclick={() => (isMobileMenuOpen = false)}
					class="block py-2 text-sm font-medium text-slate-700 dark:text-slate-200"
				>
					Fitur Unggulan
				</a>
				<a
					href="#telegram"
					onclick={() => (isMobileMenuOpen = false)}
					class="block py-2 text-sm font-medium text-slate-700 dark:text-slate-200"
				>
					Simulasi Telegram
				</a>
				<a
					href="#workspaces"
					onclick={() => (isMobileMenuOpen = false)}
					class="block py-2 text-sm font-medium text-slate-700 dark:text-slate-200"
				>
					Solusi Workspace
				</a>
				<a
					href="#pricing"
					onclick={() => (isMobileMenuOpen = false)}
					class="block py-2 text-sm font-medium text-slate-700 dark:text-slate-200"
				>
					Harga
				</a>
				<a
					href="#faq"
					onclick={() => (isMobileMenuOpen = false)}
					class="block py-2 text-sm font-medium text-slate-700 dark:text-slate-200"
				>
					FAQ
				</a>
				<div class="pt-3 border-t border-slate-200 dark:border-white/10 flex flex-col gap-2">
					<a
						href="/login"
						class="w-full text-center py-2.5 rounded-xl bg-[#007AFF] text-white text-xs font-semibold"
					>
						Masuk
					</a>
				</div>
			</div>
		{/if}
	</header>

	<!-- ========================================================================= -->
	<!-- 2. HERO SECTION (Ambient 3D Glow, Nano Banana Illustration & Trust Badges) -->
	<!-- ========================================================================= -->
	<section class="relative pt-12 pb-20 sm:pt-20 sm:pb-32 overflow-hidden">
		<!-- Subtle ambient backdrop light blobs -->
		<div class="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-gradient-to-tr from-[#007AFF]/15 to-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>
		<div class="absolute top-1/3 -right-20 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl pointer-events-none"></div>

		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
			<div class="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
				<!-- Left Column: Copywriting & Instant CTAs -->
				<div class="lg:col-span-7 space-y-6 text-center lg:text-left">
					<!-- Pill Badge -->
					<div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-500/10 dark:bg-blue-400/10 border border-blue-500/20 text-[#007AFF] dark:text-[#0A84FF] text-xs font-semibold">
						<span class="w-2 h-2 rounded-full bg-[#007AFF] dark:bg-[#0A84FF] animate-pulse"></span>
						<span>Revolusi Finansial Berbasis Telegram</span>
					</div>

					<!-- Main Headline -->
					<h1 class="text-3xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-slate-900 dark:text-white leading-[1.15]">
						Catat Duit Selesai dalam <span class="text-transparent bg-clip-text bg-gradient-to-r from-[#007AFF] to-[#00C6FF]">3 Detik</span>.<br />
						Cukup Lewat Chat Telegram.
					</h1>

					<!-- Subtitle -->
					<p class="text-base sm:text-lg text-slate-600 dark:text-slate-300 max-w-2xl mx-auto lg:mx-0 font-normal leading-relaxed">
						Lupakan keribetan membuka aplikasi finansial konvensional. Cukup ketik <span class="font-semibold text-slate-900 dark:text-white">"kopi 28k"</span> atau <span class="font-semibold text-slate-900 dark:text-white">"bensin 100rb"</span> ke bot Telegram kami. AI akan memilah kategori, memperbarui saldo rekening, dan memantau anggaran Anda secara otomatis.
					</p>

					<!-- Action Buttons -->
					<div class="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-3 sm:gap-4 pt-2">
						<a
							href="/login"
							class="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-2xl bg-[#007AFF] hover:bg-[#0062CC] text-white text-sm font-semibold shadow-lg shadow-[#007AFF]/25 transition-all active:scale-[0.98]"
						>
							<span>Mulai Sekarang</span>
							<ArrowRight class="w-4 h-4" />
						</a>

						<a
							href="#features"
							class="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-2xl bg-white dark:bg-[#151926] hover:bg-slate-50 dark:hover:bg-[#1A2030] text-slate-800 dark:text-white border border-slate-200 dark:border-white/10 text-sm font-semibold shadow-sm transition-all active:scale-[0.98]"
						>
							<span>Pelajari Fitur</span>
						</a>
					</div>

					<!-- Key Solution Capabilities -->
					<div class="flex items-center justify-center lg:justify-start gap-2 pt-2 text-xs text-slate-500 dark:text-slate-400">
						<span class="flex h-2 w-2 rounded-full bg-emerald-500"></span>
						<span>Dirancang untuk multi-kebutuhan: <b>Personal</b>, <b>Keluarga</b>, hingga <b>Bisnis & UMKM</b>.</span>
					</div>

					<!-- Key Proof Stats -->
					<div class="grid grid-cols-3 gap-4 pt-6 border-t border-slate-200/80 dark:border-white/10 max-w-lg mx-auto lg:mx-0">
						<div>
							<p class="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white">&lt;3 dtk</p>
							<p class="text-[11px] sm:text-xs text-slate-500 dark:text-slate-400 mt-0.5">Waktu Catat Cepat</p>
						</div>
						<div>
							<p class="text-2xl sm:text-3xl font-bold text-emerald-600 dark:text-emerald-400">100%</p>
							<p class="text-[11px] sm:text-xs text-slate-500 dark:text-slate-400 mt-0.5">Bank & E-Wallet RI</p>
						</div>
						<div>
							<p class="text-2xl sm:text-3xl font-bold text-[#007AFF] dark:text-[#0A84FF]">AES-256</p>
							<p class="text-[11px] sm:text-xs text-slate-500 dark:text-slate-400 mt-0.5">Enkripsi Bank Grade</p>
						</div>
					</div>
				</div>

				<!-- Right Column: 3D FinTech Hero Image (Generated with Nano Banana) & Interactive Floating Elements -->
				<div class="lg:col-span-5 relative flex items-center justify-center">
					<!-- Visual Card Frame with Glassmorphism -->
					<div class="relative w-full max-w-md lg:max-w-none rounded-3xl p-2.5 sm:p-3 bg-gradient-to-b from-white/90 via-white/80 to-slate-100/70 dark:from-[#151926]/90 dark:via-[#131622]/85 dark:to-[#0f121d]/80 backdrop-blur-2xl border border-slate-200/80 dark:border-white/15 shadow-2xl shadow-blue-500/10">
						<!-- Generated 3D Asset -->
						<div class="relative rounded-2xl overflow-hidden aspect-[4/3] sm:aspect-square bg-slate-900 flex items-center justify-center">
							<img
								src="/hero-illustration.png"
								alt="PantauDuit 3D Telegram-First Finance Illustration"
								class="w-full h-full object-cover transform hover:scale-105 transition-transform duration-700"
								loading="eager"
							/>

							<!-- Subtle Gradient Overlay -->
							<div class="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-transparent to-transparent"></div>

							<!-- Floating Badge 1: Top Right Telegram Connected -->
							<div class="absolute top-4 right-4 px-3 py-1.5 rounded-full bg-[#0088cc]/90 text-white text-[11px] font-semibold flex items-center gap-1.5 shadow-lg backdrop-blur-md">
								<Send class="w-3.5 h-3.5" />
								<span>@PantauDuitBot Terhubung</span>
							</div>

							<!-- Floating Badge 2: Bottom Overlay Live Transaction -->
							<div class="absolute bottom-4 left-4 right-4 p-3 rounded-xl bg-white/90 dark:bg-[#131B2A]/90 backdrop-blur-md border border-white/20 dark:border-white/10 flex items-center justify-between shadow-lg">
								<div class="flex items-center gap-2.5">
									<div class="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center font-bold text-xs">
										☕
									</div>
									<div>
										<p class="text-xs font-bold text-slate-900 dark:text-white leading-none">Kopi Kenangan</p>
										<p class="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5">Otomatis Masuk Pos Jajan</p>
									</div>
								</div>
								<div class="text-right">
									<p class="text-xs font-bold text-rose-500">-Rp 28.000</p>
									<p class="text-[9px] text-emerald-600 dark:text-emerald-400 font-medium">Sisa Budget 72%</p>
								</div>
							</div>
						</div>
					</div>

					<!-- Floating Micro-Card Behind/Aside -->
					<div class="absolute -bottom-6 -left-6 hidden sm:flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-white/95 dark:bg-[#161d2d]/95 backdrop-blur-xl border border-slate-200 dark:border-white/10 shadow-xl">
						<div class="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></div>
						<span class="text-xs font-semibold text-slate-700 dark:text-slate-200">
							Sinkronisasi Multi-Rekening Real-Time
						</span>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- ========================================================================= -->
	<!-- 3. INTERACTIVE TELEGRAM SIMULATOR SECTION -->
	<!-- ========================================================================= -->
	<section id="telegram" class="py-16 sm:py-24 bg-slate-100/60 dark:bg-[#0f1422] border-y border-slate-200/70 dark:border-white/5 relative">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="text-center max-w-3xl mx-auto mb-12 sm:mb-16">
				<div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#0088cc]/10 text-[#0088cc] text-xs font-semibold mb-3">
					<Bot class="w-3.5 h-3.5" />
					<span>Uji Coba Langsung di Sini</span>
				</div>
				<h2 class="text-2xl sm:text-4xl font-extrabold text-slate-900 dark:text-white tracking-tight">
					Rasakan Sensasi Catat Finansial Secepat Mengetik Chat
				</h2>
				<p class="text-sm sm:text-base text-slate-600 dark:text-slate-400 mt-3">
					Ketik pesan transaksi Anda sendiri atau klik salah satu contoh di bawah. Perhatikan bagaimana bot mengurai teks dan mengategorikannya seketika.
				</p>
			</div>

			<div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
				<!-- Left 5 cols: Interactive Chat Simulator Box -->
				<div class="lg:col-span-6 w-full max-w-lg mx-auto">
					<div class="rounded-3xl bg-white dark:bg-[#131726] border border-slate-200/80 dark:border-white/10 shadow-2xl overflow-hidden flex flex-col h-[520px]">
						<!-- Chat Header (Telegram Style) -->
						<div class="p-3.5 sm:p-4 bg-[#0088cc] text-white flex items-center justify-between">
							<div class="flex items-center gap-3">
								<div class="w-10 h-10 rounded-full bg-white text-[#0088cc] flex items-center justify-center font-bold text-base shadow-sm">
									🤖
								</div>
								<div>
									<h3 class="text-sm font-bold leading-none">Pantau Duit Bot</h3>
									<p class="text-[11px] text-blue-100 mt-1 flex items-center gap-1">
										<span class="w-1.5 h-1.5 rounded-full bg-emerald-300 animate-ping"></span>
										<span>bot aktif (NLP engine v2.4)</span>
									</p>
								</div>
							</div>
							<span class="text-[10px] bg-black/15 px-2 py-1 rounded-md font-medium text-white/90">
								Telegram Web Simulator
							</span>
						</div>

						<!-- Chat Message Feed -->
						<div class="flex-1 p-4 overflow-y-auto space-y-3 bg-slate-50 dark:bg-[#0c0f1a]">
							{#each simMessages as msg (msg.id)}
								<div class="flex {msg.sender === 'user' ? 'justify-end' : 'justify-start'}">
									<div class="max-w-[85%] rounded-2xl px-4 py-2.5 text-xs sm:text-sm leading-relaxed shadow-sm {msg.sender === 'user'
										? 'bg-[#007AFF] text-white rounded-tr-none'
										: 'bg-white dark:bg-[#1a2133] text-slate-800 dark:text-slate-100 border border-slate-200/60 dark:border-white/10 rounded-tl-none whitespace-pre-line'}">
										<p>{msg.text}</p>
										<span class="block text-[10px] text-right mt-1 opacity-70">
											{msg.time}
										</span>
									</div>
								</div>
							{/each}

							{#if isSimTyping}
								<div class="flex justify-start">
									<div class="rounded-2xl rounded-tl-none bg-white dark:bg-[#1a2133] px-4 py-2 border border-slate-200/60 dark:border-white/10 text-xs text-slate-400 italic flex items-center gap-1.5">
										<span class="w-1.5 h-1.5 rounded-full bg-[#0088cc] animate-bounce"></span>
										<span class="w-1.5 h-1.5 rounded-full bg-[#0088cc] animate-bounce [animation-delay:0.2s]"></span>
										<span class="w-1.5 h-1.5 rounded-full bg-[#0088cc] animate-bounce [animation-delay:0.4s]"></span>
										<span>Bot sedang memproses transaksi...</span>
									</div>
								</div>
							{/if}
						</div>

						<!-- Quick Chips -->
						<div class="p-2.5 bg-slate-100 dark:bg-[#111624] border-t border-slate-200/60 dark:border-white/5 flex items-center gap-1.5 overflow-x-auto no-scrollbar">
							<span class="text-[10px] text-slate-400 shrink-0 font-medium ml-1">Contoh:</span>
							{#each quickPrompts as prompt}
								<button
									type="button"
									onclick={() => handleQuickPrompt(prompt)}
									class="shrink-0 px-2.5 py-1 rounded-full bg-white dark:bg-[#1c2438] hover:bg-slate-200 dark:hover:bg-[#25304a] text-slate-700 dark:text-slate-200 text-[11px] font-medium border border-slate-200 dark:border-white/10 transition-colors"
								>
									{prompt}
								</button>
							{/each}
						</div>

						<!-- Chat Input Bar -->
						<form
							onsubmit={(e) => { e.preventDefault(); sendSimMessage(); }}
							class="p-3 bg-white dark:bg-[#131726] border-t border-slate-200/80 dark:border-white/10 flex items-center gap-2"
						>
							<input
								type="text"
								bind:value={simInput}
								placeholder="Ketik pengeluaranmu (misal: bensin 50rb)..."
								class="flex-1 bg-slate-100 dark:bg-[#1a2133] text-slate-900 dark:text-white text-xs sm:text-sm px-3.5 py-2.5 rounded-xl border-none focus:outline-none focus:ring-2 focus:ring-[#0088cc]"
							/>
							<button
								type="submit"
								disabled={!simInput.trim() || isSimTyping}
								class="p-2.5 rounded-xl bg-[#0088cc] hover:bg-[#0077b5] disabled:opacity-50 text-white transition-all shadow-sm active:scale-95"
							>
								<Send class="w-4 h-4" />
							</button>
						</form>
					</div>
				</div>

				<!-- Right 6 cols: Explanatory Graphic (Generated with Nano Banana) & Highlights -->
				<div class="lg:col-span-6 space-y-6">
					<div class="rounded-3xl overflow-hidden border border-slate-200/80 dark:border-white/10 shadow-lg relative bg-slate-950">
						<img
							src="/telegram-bot-feature.png"
							alt="Telegram Bot Natural Language Interface Mockup"
							class="w-full h-auto object-cover hover:scale-102 transition-transform duration-500"
							loading="lazy"
						/>
					</div>

					<div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
						<div class="p-4 rounded-2xl bg-white dark:bg-[#131726] border border-slate-200/80 dark:border-white/5">
							<div class="w-8 h-8 rounded-xl bg-[#007AFF]/10 text-[#007AFF] flex items-center justify-center mb-2 font-bold">
								🧠
							</div>
							<h4 class="text-xs sm:text-sm font-bold text-slate-900 dark:text-white">Smart NLP Bahasa Indonesia</h4>
							<p class="text-xs text-slate-500 dark:text-slate-400 mt-1">
								Memahami singkatan seperti "25k", "50rb", "1.5jt", dan nama tempat lokal dengan akurasi 98%.
							</p>
						</div>

						<div class="p-4 rounded-2xl bg-white dark:bg-[#131726] border border-slate-200/80 dark:border-white/5">
							<div class="w-8 h-8 rounded-xl bg-emerald-500/10 text-emerald-600 flex items-center justify-center mb-2 font-bold">
								⚡
							</div>
							<h4 class="text-xs sm:text-sm font-bold text-slate-900 dark:text-white">Sinkronisasi 0-Lag</h4>
							<p class="text-xs text-slate-500 dark:text-slate-400 mt-1">
								Transaksi langsung terefleksi di dashboard SvelteKit secara instan tanpa perlu refresh halaman.
							</p>
						</div>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- ========================================================================= -->
	<!-- 4. KEY FEATURES GRID (Matches Dashboard Glass Card Theme) -->
	<!-- ========================================================================= -->
	<section id="features" class="py-20 sm:py-28">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="text-center max-w-3xl mx-auto mb-16">
				<div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 text-[#007AFF] dark:text-[#0A84FF] text-xs font-semibold mb-3">
					<Sparkles class="w-3.5 h-3.5" />
					<span>Dibangun untuk Kenyamanan Anda</span>
				</div>
				<h2 class="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white tracking-tight">
					Fitur Lengkap Command Center Finansial Modern
				</h2>
				<p class="text-sm sm:text-base text-slate-600 dark:text-slate-400 mt-3">
					Semua kebutuhan keuangan pribadi, keluarga, dan tim usaha terpusat dalam satu dashboard yang cepat, rapi, dan menawan.
				</p>
			</div>

			<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
				<!-- Card 1: Multi-Rekening -->
				<div class="p-6 sm:p-8 rounded-3xl bg-white/80 dark:bg-[#131726]/80 backdrop-blur-xl border border-slate-200/80 dark:border-white/10 hover:border-[#007AFF]/50 transition-all shadow-sm hover:shadow-xl hover:-translate-y-1">
					<div class="w-12 h-12 rounded-2xl bg-blue-500/10 text-[#007AFF] flex items-center justify-center mb-5">
						<Wallet class="w-6 h-6" />
					</div>
					<h3 class="text-lg font-bold text-slate-900 dark:text-white tracking-tight">
						Multi-Rekening & E-Wallet
					</h3>
					<p class="text-xs sm:text-sm text-slate-600 dark:text-slate-400 mt-2 leading-relaxed">
						Kelola BCA, Mandiri, Jenius, GoPay, OVO, ShopeePay hingga kas dompet fisik dalam satu ringkasan total kekayaan bersih (Net Worth).
					</p>
					<div class="mt-4 pt-4 border-t border-slate-100 dark:border-white/5 flex items-center gap-2 text-xs font-semibold text-[#007AFF] dark:text-[#0A84FF]">
						<span>Transfer Antar Rekening</span>
						<ArrowUpRight class="w-3.5 h-3.5" />
					</div>
				</div>

				<!-- Card 2: Smart Budgeting -->
				<div class="p-6 sm:p-8 rounded-3xl bg-white/80 dark:bg-[#131726]/80 backdrop-blur-xl border border-slate-200/80 dark:border-white/10 hover:border-emerald-500/50 transition-all shadow-sm hover:shadow-xl hover:-translate-y-1">
					<div class="w-12 h-12 rounded-2xl bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center mb-5">
						<PieChart class="w-6 h-6" />
					</div>
					<h3 class="text-lg font-bold text-slate-900 dark:text-white tracking-tight">
						Anggaran Cerdas & Anti-Boncos
					</h3>
					<p class="text-xs sm:text-sm text-slate-600 dark:text-slate-400 mt-2 leading-relaxed">
						Tetapkan batas belanja per kategori (Makanan, Hiburan, Tagihan). Dapatkan peringatan otomatis via Telegram sebelum anggaran Anda habis.
					</p>
					<div class="mt-4 pt-4 border-t border-slate-100 dark:border-white/5 flex items-center gap-2 text-xs font-semibold text-emerald-600 dark:text-emerald-400">
						<span>Visual Progress & Threshold Alert</span>
						<ArrowUpRight class="w-3.5 h-3.5" />
					</div>
				</div>

				<!-- Card 3: Financial Goals -->
				<div class="p-6 sm:p-8 rounded-3xl bg-white/80 dark:bg-[#131726]/80 backdrop-blur-xl border border-slate-200/80 dark:border-white/10 hover:border-amber-500/50 transition-all shadow-sm hover:shadow-xl hover:-translate-y-1">
					<div class="w-12 h-12 rounded-2xl bg-amber-500/10 text-amber-500 flex items-center justify-center mb-5">
						<Target class="w-6 h-6" />
					</div>
					<h3 class="text-lg font-bold text-slate-900 dark:text-white tracking-tight">
						Target Tabungan (Goals)
					</h3>
					<p class="text-xs sm:text-sm text-slate-600 dark:text-slate-400 mt-2 leading-relaxed">
						Rencanakan tabungan untuk Dana Darurat, Liburan, Gadget baru, atau DP Rumah dengan animasi visual radar glow pencapaian target.
					</p>
					<div class="mt-4 pt-4 border-t border-slate-100 dark:border-white/5 flex items-center gap-2 text-xs font-semibold text-amber-500">
						<span>Radar Glow Milestone</span>
						<ArrowUpRight class="w-3.5 h-3.5" />
					</div>
				</div>

				<!-- Card 4: Portofolio Investasi -->
				<div class="p-6 sm:p-8 rounded-3xl bg-white/80 dark:bg-[#131726]/80 backdrop-blur-xl border border-slate-200/80 dark:border-white/10 hover:border-purple-500/50 transition-all shadow-sm hover:shadow-xl hover:-translate-y-1">
					<div class="w-12 h-12 rounded-2xl bg-purple-500/10 text-purple-600 dark:text-purple-400 flex items-center justify-center mb-5">
						<TrendingUp class="w-6 h-6" />
					</div>
					<h3 class="text-lg font-bold text-slate-900 dark:text-white tracking-tight">
						Portofolio & Investasi
					</h3>
					<p class="text-xs sm:text-sm text-slate-600 dark:text-slate-400 mt-2 leading-relaxed">
						Lacak kepemilikan Reksadana, Saham IHSG, Emas Antam, dan Kripto dengan perhitungan rata-rata beli (average buy price) otomatis.
					</p>
					<div class="mt-4 pt-4 border-t border-slate-100 dark:border-white/5 flex items-center gap-2 text-xs font-semibold text-purple-600 dark:text-purple-400">
						<span>Pelacakan Multi-Aset</span>
						<ArrowUpRight class="w-3.5 h-3.5" />
					</div>
				</div>

				<!-- Card 5: Incognito Privacy Mode -->
				<div class="p-6 sm:p-8 rounded-3xl bg-white/80 dark:bg-[#131726]/80 backdrop-blur-xl border border-slate-200/80 dark:border-white/10 hover:border-sky-500/50 transition-all shadow-sm hover:shadow-xl hover:-translate-y-1">
					<div class="w-12 h-12 rounded-2xl bg-sky-500/10 text-sky-500 flex items-center justify-center mb-5">
						<Eye class="w-6 h-6" />
					</div>
					<h3 class="text-lg font-bold text-slate-900 dark:text-white tracking-tight">
						Mode Privasi (Incognito)
					</h3>
					<p class="text-xs sm:text-sm text-slate-600 dark:text-slate-400 mt-2 leading-relaxed">
						Sering membuka dashboard di cafe atau kantor? Tombol satu klik menyamarkan seluruh angka saldo menjadi tanda bintang (••••••••).
					</p>
					<div class="mt-4 pt-4 border-t border-slate-100 dark:border-white/5 flex items-center gap-2 text-xs font-semibold text-sky-500">
						<span>1-Click Privacy Toggle</span>
						<ArrowUpRight class="w-3.5 h-3.5" />
					</div>
				</div>

				<!-- Card 6: Audit Trail & Laporan Excel/PDF -->
				<div class="p-6 sm:p-8 rounded-3xl bg-white/80 dark:bg-[#131726]/80 backdrop-blur-xl border border-slate-200/80 dark:border-white/10 hover:border-indigo-500/50 transition-all shadow-sm hover:shadow-xl hover:-translate-y-1">
					<div class="w-12 h-12 rounded-2xl bg-indigo-500/10 text-indigo-500 flex items-center justify-center mb-5">
						<FileSpreadsheet class="w-6 h-6" />
					</div>
					<h3 class="text-lg font-bold text-slate-900 dark:text-white tracking-tight">
						Laporan Ekspor & Audit Log
					</h3>
					<p class="text-xs sm:text-sm text-slate-600 dark:text-slate-400 mt-2 leading-relaxed">
						Unduh rekap bulanan ke format spreadsheet atau cetak laporan PDF rapi untuk pelaporan pajak maupun evaluasi keuangan tahunan.
					</p>
					<div class="mt-4 pt-4 border-t border-slate-100 dark:border-white/5 flex items-center gap-2 text-xs font-semibold text-indigo-500">
						<span>Ekspor Laporan Bebas Ribet</span>
						<ArrowUpRight class="w-3.5 h-3.5" />
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- ========================================================================= -->
	<!-- 5. WORKSPACES SHOWCASE (Personal vs Family vs Enterprise Business) -->
	<!-- ========================================================================= -->
	<section id="workspaces" class="py-20 bg-slate-100/60 dark:bg-[#0f1422] border-y border-slate-200/70 dark:border-white/5">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="text-center max-w-3xl mx-auto mb-12">
				<div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 text-xs font-semibold mb-3">
					<Users class="w-3.5 h-3.5" />
					<span>Fleksibel untuk Segala Kebutuhan</span>
				</div>
				<h2 class="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white tracking-tight">
					Satu Platform, Tiga Solusi Workspace
				</h2>
				<p class="text-sm sm:text-base text-slate-600 dark:text-slate-400 mt-3">
					Sesuaikan alur kerja finansial sesuai fase kehidupan dan skala organisasi Anda.
				</p>
			</div>

			<!-- Workspace Selector Tabs -->
			<div class="flex items-center justify-center gap-2 max-w-md mx-auto p-1.5 rounded-2xl bg-slate-200/80 dark:bg-white/5 mb-10">
				<button
					type="button"
					onclick={() => (activeWorkspaceTab = 'personal')}
					class="flex-1 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all {activeWorkspaceTab === 'personal'
						? 'bg-white dark:bg-[#151926] text-[#007AFF] dark:text-[#0A84FF] shadow-sm'
						: 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'}"
				>
					Personal
				</button>
				<button
					type="button"
					onclick={() => (activeWorkspaceTab = 'family')}
					class="flex-1 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all {activeWorkspaceTab === 'family'
						? 'bg-white dark:bg-[#151926] text-[#007AFF] dark:text-[#0A84FF] shadow-sm'
						: 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'}"
				>
					Family
				</button>
				<button
					type="button"
					onclick={() => (activeWorkspaceTab = 'business')}
					class="flex-1 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all {activeWorkspaceTab === 'business'
						? 'bg-white dark:bg-[#151926] text-[#007AFF] dark:text-[#0A84FF] shadow-sm'
						: 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'}"
				>
					Business
				</button>
			</div>

			<!-- Tab Contents -->
			<div class="rounded-3xl bg-white dark:bg-[#131726] border border-slate-200/80 dark:border-white/10 p-6 sm:p-10 shadow-xl">
				{#if activeWorkspaceTab === 'personal'}
					<div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
						<div class="lg:col-span-7 space-y-4">
							<span class="px-3 py-1 rounded-full text-xs font-semibold bg-blue-500/10 text-[#007AFF]">
								Personal Finance
							</span>
							<h3 class="text-2xl font-bold text-slate-900 dark:text-white">
								Personal Budgeting & Bot Telegram Harian
							</h3>
							<p class="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
								Didesain untuk profesional mandiri, mahasiswa, dan freelancer. Fokus pada kecepatan mencatat pengeluaran mikro (kopi, makan, ojek online) dan kontrol pos belanja bulanan agar tidak overbudget.
							</p>
							<ul class="space-y-2.5 text-xs sm:text-sm text-slate-600 dark:text-slate-300 pt-2">
								<li class="flex items-center gap-2">
									<Check class="w-4 h-4 text-emerald-500" />
									<span>Integrasi instan bot Telegram pribadi tanpa setup rumit</span>
								</li>
								<li class="flex items-center gap-2">
									<Check class="w-4 h-4 text-emerald-500" />
									<span>Visual Donut Chart kategori pengeluaran terbesar</span>
								</li>
								<li class="flex items-center gap-2">
									<Check class="w-4 h-4 text-emerald-500" />
									<span>Kalkulator dana darurat dan tabungan impian</span>
								</li>
							</ul>
							<div class="pt-4">
								<a
									href="#pricing"
									class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-[#007AFF] text-white text-xs sm:text-sm font-semibold"
								>
									<span>Lihat Fitur Personal</span>
									<ArrowRight class="w-4 h-4" />
								</a>
							</div>
						</div>
						<div class="lg:col-span-5 p-6 rounded-2xl bg-slate-50 dark:bg-[#0c0f1a] border border-slate-200/60 dark:border-white/5 space-y-4">
							<div class="flex items-center justify-between pb-3 border-b border-slate-200/60 dark:border-white/5">
								<span class="text-xs font-semibold text-slate-500">Ringkasan Saldo Rekening</span>
								<span class="text-xs font-bold text-emerald-600 dark:text-emerald-400">Aktif</span>
							</div>
							<div class="space-y-3">
								<div class="flex justify-between items-center text-xs">
									<span class="text-slate-600 dark:text-slate-400">Rekening Bank Utama</span>
									<span class="font-bold text-slate-900 dark:text-white">Rp 24.850.000</span>
								</div>
								<div class="flex justify-between items-center text-xs">
									<span class="text-slate-600 dark:text-slate-400">Dompet Digital</span>
									<span class="font-bold text-slate-900 dark:text-white">Rp 472.000</span>
								</div>
								<div class="flex justify-between items-center text-xs">
									<span class="text-slate-600 dark:text-slate-400">Portofolio Reksadana</span>
									<span class="font-bold text-slate-900 dark:text-white">Rp 12.300.000</span>
								</div>
							</div>
						</div>
					</div>
				{:else if activeWorkspaceTab === 'family'}
					<div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
						<div class="lg:col-span-7 space-y-4">
							<span class="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-600">
								Family Collaboration
							</span>
							<h3 class="text-2xl font-bold text-slate-900 dark:text-white">
								Family Collaboration & Shared Wallets
							</h3>
							<p class="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
								Solusi transparansi keuangan rumah tangga bersama pasangan. Kelola pos belanja dapur, SPP anak, dan cicilan KPR bersama tanpa saling curiga, dengan pemisahan rekening pribadi yang tetap aman.
							</p>
							<ul class="space-y-2.5 text-xs sm:text-sm text-slate-600 dark:text-slate-300 pt-2">
								<li class="flex items-center gap-2">
									<Check class="w-4 h-4 text-emerald-500" />
									<span>Multi-akun suami & istri dalam satu grup Telegram</span>
								</li>
								<li class="flex items-center gap-2">
									<Check class="w-4 h-4 text-emerald-500" />
									<span>Hak akses RBAC fleksibel (siapa yang boleh melihat/mencatat)</span>
								</li>
								<li class="flex items-center gap-2">
									<Check class="w-4 h-4 text-emerald-500" />
									<span>Notifikasi tagihan bulanan keluarga secara serentak</span>
								</li>
							</ul>
							<div class="pt-4">
								<a
									href="#pricing"
									class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-600 text-white text-xs sm:text-sm font-semibold"
								>
									<span>Lihat Fitur Family</span>
									<ArrowRight class="w-4 h-4" />
								</a>
							</div>
						</div>
						<div class="lg:col-span-5 p-6 rounded-2xl bg-slate-50 dark:bg-[#0c0f1a] border border-slate-200/60 dark:border-white/5 space-y-4">
							<div class="flex items-center justify-between pb-3 border-b border-slate-200/60 dark:border-white/5">
								<span class="text-xs font-semibold text-slate-500">Workspace Keuangan Keluarga</span>
								<span class="text-xs font-bold text-[#007AFF]">Multi-User</span>
							</div>
							<div class="space-y-3">
								<div class="flex justify-between items-center text-xs">
									<span class="text-slate-600 dark:text-slate-400">Kas Belanja Dapur</span>
									<span class="font-bold text-slate-900 dark:text-white">Rp 6.500.000 / bln</span>
								</div>
								<div class="flex justify-between items-center text-xs">
									<span class="text-slate-600 dark:text-slate-400">Pendidikan & SPP</span>
									<span class="font-bold text-slate-900 dark:text-white">Rp 4.200.000</span>
								</div>
								<div class="flex justify-between items-center text-xs">
									<span class="text-slate-600 dark:text-slate-400">Anggota Terkoneksi</span>
									<span class="font-bold text-slate-900 dark:text-white">2 Pengguna (Suami & Istri)</span>
								</div>
							</div>
						</div>
					</div>
				{:else}
					<div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
						<div class="lg:col-span-7 space-y-4">
							<span class="px-3 py-1 rounded-full text-xs font-semibold bg-purple-500/10 text-purple-600">
								Enterprise & Business
							</span>
							<h3 class="text-2xl font-bold text-slate-900 dark:text-white">
								Manajemen HR, Payroll & Reimbursement Bisnis
							</h3>
							<p class="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
								Satu atap untuk operasional UMKM dan startup: manajemen absensi shift & fingerprint, pengajuan cuti, klaim reimbursement struk pengeluaran karyawan via Telegram, hingga penerbitan slip gaji payroll.
							</p>
							<ul class="space-y-2.5 text-xs sm:text-sm text-slate-600 dark:text-slate-300 pt-2">
								<li class="flex items-center gap-2">
									<Check class="w-4 h-4 text-emerald-500" />
									<span>Modul Perusahaan Lengkap: Karyawan, Shift, Cuti & Dokumen</span>
								</li>
								<li class="flex items-center gap-2">
									<Check class="w-4 h-4 text-emerald-500" />
									<span>Integrasi mesin absensi Fingerprint & GPS Attendance</span>
								</li>
								<li class="flex items-center gap-2">
									<Check class="w-4 h-4 text-emerald-500" />
									<span>Persetujuan reimbursement langsung dari chat Telegram</span>
								</li>
							</ul>
							<div class="pt-4">
								<a
									href="#pricing"
									class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-purple-600 text-white text-xs sm:text-sm font-semibold"
								>
									<span>Lihat Fitur Bisnis</span>
									<ArrowRight class="w-4 h-4" />
								</a>
							</div>
						</div>
						<div class="lg:col-span-5 p-6 rounded-2xl bg-slate-50 dark:bg-[#0c0f1a] border border-slate-200/60 dark:border-white/5 space-y-4">
							<div class="flex items-center justify-between pb-3 border-b border-slate-200/60 dark:border-white/5">
								<span class="text-xs font-semibold text-slate-500">Operasional & Karyawan</span>
								<span class="text-xs font-bold text-purple-500">Corporate</span>
							</div>
							<div class="space-y-3">
								<div class="flex justify-between items-center text-xs">
									<span class="text-slate-600 dark:text-slate-400">Total Karyawan</span>
									<span class="font-bold text-slate-900 dark:text-white">18 Anggota Tim</span>
								</div>
								<div class="flex justify-between items-center text-xs">
									<span class="text-slate-600 dark:text-slate-400">Total Payroll Bulanan</span>
									<span class="font-bold text-slate-900 dark:text-white">Rp 148.500.000</span>
								</div>
								<div class="flex justify-between items-center text-xs">
									<span class="text-slate-600 dark:text-slate-400">Reimbursement Pending</span>
									<span class="font-bold text-amber-500">3 Menunggu Review</span>
								</div>
							</div>
						</div>
					</div>
				{/if}
			</div>
		</div>
	</section>

	<!-- ========================================================================= -->
	<!-- 6. PRICING SECTION (Transparent, Monthly/Yearly Toggle & Genuine Data) -->
	<!-- ========================================================================= -->
	<section id="pricing" class="py-20 sm:py-28">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="text-center max-w-3xl mx-auto mb-12">
				<div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 text-[#007AFF] dark:text-[#0A84FF] text-xs font-semibold mb-3">
					<Coins class="w-3.5 h-3.5" />
					<span>Pilihan Paket Berlangganan</span>
				</div>
				<h2 class="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white tracking-tight">
					Investasi Cerdas untuk Kesehatan Finansial Anda
				</h2>
				<p class="text-sm sm:text-base text-slate-600 dark:text-slate-400 mt-3">
					Mulai gratis dan upgrade kapan pun saat kebutuhan Anda berkembang. Tanpa biaya tersembunyi.
				</p>

				<!-- Monthly / Yearly Billing Toggle -->
				<div class="mt-8 inline-flex items-center gap-3 p-1.5 rounded-2xl bg-slate-200/80 dark:bg-white/5 border border-slate-300/60 dark:border-white/10">
					<button
						type="button"
						onclick={() => (billingCycle = 'monthly')}
						class="px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all {billingCycle === 'monthly'
							? 'bg-white dark:bg-[#151926] text-slate-900 dark:text-white shadow-sm'
							: 'text-slate-600 dark:text-slate-400'}"
					>
						Bulanan
					</button>
					<button
						type="button"
						onclick={() => (billingCycle = 'yearly')}
						class="px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all flex items-center gap-1.5 {billingCycle === 'yearly'
							? 'bg-white dark:bg-[#151926] text-slate-900 dark:text-white shadow-sm'
							: 'text-slate-600 dark:text-slate-400'}"
					>
						<span>Tahunan</span>
						<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500 text-white">
							Hemat 20%
						</span>
					</button>
				</div>
			</div>

			<!-- Pricing Cards Grid -->
			<div class="grid grid-cols-1 lg:grid-cols-3 gap-8 items-stretch">
				{#each plans as plan}
					<div class="relative rounded-3xl p-8 flex flex-col justify-between transition-all duration-300 {plan.popular
						? 'bg-gradient-to-b from-blue-50/80 via-white to-white dark:from-[#151926] dark:via-[#131622] dark:to-[#0f121d] border-2 border-[#007AFF] shadow-2xl shadow-blue-500/15 lg:-translate-y-2'
						: 'bg-white dark:bg-[#131726] border border-slate-200/80 dark:border-white/10 shadow-sm'}">
						
						{#if plan.popular}
							<div class="absolute -top-3.5 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-gradient-to-r from-[#007AFF] to-[#0055B3] text-white text-xs font-bold shadow-md">
								{plan.badge}
							</div>
						{/if}

						<div>
							<div class="flex justify-between items-center mb-4">
								<h3 class="text-xl font-bold text-slate-900 dark:text-white">{plan.name}</h3>
								{#if !plan.popular}
									<span class="text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-100 dark:bg-white/5 text-slate-600 dark:text-slate-400">
										{plan.badge}
									</span>
								{/if}
							</div>

							<p class="text-xs text-slate-500 dark:text-slate-400 mb-6 min-h-[36px]">
								{plan.description}
							</p>

							<!-- Price Display -->
							<div class="mb-6 pb-6 border-b border-slate-100 dark:border-white/5">
								<div class="flex items-baseline gap-1">
									<span class="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white">
										{billingCycle === 'monthly' ? formatRupiah(plan.priceMonthly) : formatRupiah(plan.priceYearly)}
									</span>
									<span class="text-xs text-slate-500 dark:text-slate-400">
										/{billingCycle === 'monthly' ? 'bulan' : 'tahun'}
									</span>
								</div>
								{#if billingCycle === 'yearly' && plan.priceMonthly > 0}
									<p class="text-[11px] text-emerald-600 dark:text-emerald-400 font-semibold mt-1">
										Setara {formatRupiah(Math.round(plan.priceYearly / 12))}/bulan (Hemat 2 bulan!)
									</p>
								{/if}
							</div>

							<!-- Features List -->
							<ul class="space-y-3 mb-8">
								{#each plan.features as feat}
									<li class="flex items-start gap-2.5 text-xs sm:text-sm text-slate-600 dark:text-slate-300">
										<CheckCircle2 class="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
										<span>{feat}</span>
									</li>
								{/each}
							</ul>
						</div>

						<a
							href="/login"
							class="w-full py-3 px-4 rounded-xl text-center text-xs sm:text-sm font-semibold transition-all {plan.popular
								? 'bg-[#007AFF] hover:bg-[#0062CC] text-white shadow-lg shadow-[#007AFF]/25 active:scale-[0.98]'
								: 'bg-slate-100 dark:bg-white/10 hover:bg-slate-200 dark:hover:bg-white/15 text-slate-800 dark:text-white active:scale-[0.98]'}"
						>
							{plan.buttonText}
						</a>
					</div>
				{/each}
			</div>
		</div>
	</section>

	<!-- ========================================================================= -->
	<!-- 7. TESTIMONIALS SECTION -->
	<!-- ========================================================================= -->
	<section class="py-20 bg-slate-100/60 dark:bg-[#0f1422] border-y border-slate-200/70 dark:border-white/5">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="text-center max-w-3xl mx-auto mb-16">
				<div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 text-amber-500 text-xs font-semibold mb-3">
					<Star class="w-3.5 h-3.5 fill-amber-500 text-amber-500" />
					<span>Kisah Pengguna Nyata</span>
				</div>
				<h2 class="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white tracking-tight">
					Dipercaya Ratusan Individu & Tim Keluarga
				</h2>
				<p class="text-sm sm:text-base text-slate-600 dark:text-slate-400 mt-3">
					Dengarkan bagaimana PantauDuit mengubah kebiasaan finansial mereka dari malas mencatat menjadi disiplin setiap hari.
				</p>
			</div>

			<div class="grid grid-cols-1 md:grid-cols-3 gap-6 sm:gap-8">
				<div class="p-6 sm:p-8 rounded-3xl bg-white dark:bg-[#131726] border border-slate-200/80 dark:border-white/10 shadow-sm">
					<div class="flex items-center gap-1 text-amber-400 mb-4">
						{#each Array(5) as _}
							<Star class="w-4 h-4 fill-amber-400" />
						{/each}
					</div>
					<p class="text-xs sm:text-sm text-slate-600 dark:text-slate-300 italic leading-relaxed mb-6">
						"Dulu saya install puluhan aplikasi keuangan, semuanya ditinggalkan setelah 3 hari karena capek input satu-satu. Sejak pakai PantauDuit di Telegram, pas bayar kopi atau bensin langsung kirim chat 3 detik, beres!"
					</p>
					<div class="flex items-center gap-3">
						<div class="w-10 h-10 rounded-full bg-[#007AFF] text-white flex items-center justify-center font-bold text-sm">
							BS
						</div>
						<div>
							<h4 class="text-xs sm:text-sm font-bold text-slate-900 dark:text-white">Budi Santoso</h4>
							<p class="text-[11px] text-slate-400">Software Engineer, Jakarta</p>
						</div>
					</div>
				</div>

				<div class="p-6 sm:p-8 rounded-3xl bg-white dark:bg-[#131726] border border-slate-200/80 dark:border-white/10 shadow-sm">
					<div class="flex items-center gap-1 text-amber-400 mb-4">
						{#each Array(5) as _}
							<Star class="w-4 h-4 fill-amber-400" />
						{/each}
					</div>
					<p class="text-xs sm:text-sm text-slate-600 dark:text-slate-300 italic leading-relaxed mb-6">
						"Fitur Family Workspace beneran game changer buat kami pengantin baru. Istri catat belanja dapur, saya catat cicilan dan tagihan listrik. Di akhir bulan tinggal cek Donut Chart pengeluaran tanpa ribut."
					</p>
					<div class="flex items-center gap-3">
						<div class="w-10 h-10 rounded-full bg-emerald-600 text-white flex items-center justify-center font-bold text-sm">
							HP
						</div>
						<div>
							<h4 class="text-xs sm:text-sm font-bold text-slate-900 dark:text-white">Hendra Pratama</h4>
							<p class="text-[11px] text-slate-400">Kepala Keluarga & Marketer, Surabaya</p>
						</div>
					</div>
				</div>

				<div class="p-6 sm:p-8 rounded-3xl bg-white dark:bg-[#131726] border border-slate-200/80 dark:border-white/10 shadow-sm">
					<div class="flex items-center gap-1 text-amber-400 mb-4">
						{#each Array(5) as _}
							<Star class="w-4 h-4 fill-amber-400" />
						{/each}
					</div>
					<p class="text-xs sm:text-sm text-slate-600 dark:text-slate-300 italic leading-relaxed mb-6">
						"Untuk UMKM kami dengan 18 staf, modul reimbursement dan slip gaji di PantauDuit bikin kerjaan HR beres otomatis. Karyawan foto nota ke Telegram, saya tinggal approve di dashboard."
					</p>
					<div class="flex items-center gap-3">
						<div class="w-10 h-10 rounded-full bg-purple-600 text-white flex items-center justify-center font-bold text-sm">
							RA
						</div>
						<div>
							<h4 class="text-xs sm:text-sm font-bold text-slate-900 dark:text-white">Reza Aditya</h4>
							<p class="text-[11px] text-slate-400">Founder PT Pantau Duit Solusindo</p>
						</div>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- ========================================================================= -->
	<!-- 8. FREQUENTLY ASKED QUESTIONS (Accordion) -->
	<!-- ========================================================================= -->
	<section id="faq" class="py-20 sm:py-28">
		<div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="text-center mb-16">
				<div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 text-[#007AFF] dark:text-[#0A84FF] text-xs font-semibold mb-3">
					<HelpCircle class="w-3.5 h-3.5" />
					<span>Pertanyaan Populer</span>
				</div>
				<h2 class="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white tracking-tight">
					Kerap Ditanyakan seputar PantauDuit
				</h2>
			</div>

			<div class="space-y-4">
				{#each faqs as item, idx}
					<div class="rounded-2xl bg-white dark:bg-[#131726] border border-slate-200/80 dark:border-white/10 overflow-hidden transition-colors">
						<button
							type="button"
							onclick={() => toggleFaq(idx)}
							class="w-full p-5 text-left flex items-center justify-between gap-4 font-semibold text-slate-900 dark:text-white text-sm sm:text-base hover:text-[#007AFF] dark:hover:text-[#0A84FF] transition-colors"
						>
							<span>{item.q}</span>
							<ChevronRight class="w-5 h-5 text-slate-400 shrink-0 transform transition-transform duration-200 {activeFaqIndex === idx ? 'rotate-90 text-[#007AFF]' : ''}" />
						</button>
						{#if activeFaqIndex === idx}
							<div class="px-5 pb-5 text-xs sm:text-sm text-slate-600 dark:text-slate-400 leading-relaxed border-t border-slate-100 dark:border-white/5 pt-3">
								{item.a}
							</div>
						{/if}
					</div>
				{/each}
			</div>
		</div>
	</section>

	<!-- ========================================================================= -->
	<!-- 9. BOTTOM CALL-TO-ACTION BANNER -->
	<!-- ========================================================================= -->
	<section class="py-16 sm:py-24 relative overflow-hidden">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="rounded-3xl p-8 sm:p-14 bg-gradient-to-br from-[#007AFF] via-[#0062CC] to-[#004B99] text-white text-center relative overflow-hidden shadow-2xl shadow-blue-500/30">
				<!-- Ambient Glow within Banner -->
				<div class="absolute -top-24 -right-24 w-80 h-80 bg-white/15 rounded-full blur-3xl pointer-events-none"></div>
				<div class="absolute -bottom-24 -left-24 w-80 h-80 bg-cyan-400/20 rounded-full blur-3xl pointer-events-none"></div>

				<div class="relative z-10 max-w-2xl mx-auto space-y-6">
					<div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/15 text-white text-xs font-semibold backdrop-blur-md">
						<Zap class="w-3.5 h-3.5 text-yellow-300" />
						<span>Mulai Perjalanan Sehat Finansial Hari Ini</span>
					</div>

					<h2 class="text-3xl sm:text-5xl font-extrabold tracking-tight leading-tight">
						Siap Kendalikan Arus Kas Tanpa Rasa Malas?
					</h2>

					<p class="text-sm sm:text-base text-blue-100 leading-relaxed">
						Bergabunglah bersama ribuan orang yang telah merasakan kemudahan mencatat keuangan via Telegram Bot. Gratis, cepat, dan aman.
					</p>

					<div class="flex items-center justify-center pt-3">
						<a
							href="/login"
							class="w-full sm:w-auto px-8 py-3.5 rounded-2xl bg-white hover:bg-slate-100 text-[#007AFF] font-bold text-sm shadow-lg transition-all active:scale-[0.98]"
						>
							Masuk Sekarang
						</a>
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- ========================================================================= -->
	<!-- 10. FOOTER -->
	<!-- ========================================================================= -->
	<footer class="bg-white dark:bg-[#0c0f1a] border-t border-slate-200/80 dark:border-white/10 py-10 text-slate-500 dark:text-slate-400 text-xs">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex flex-col md:flex-row items-center justify-between gap-6 pb-8 border-b border-slate-200/60 dark:border-white/5">
				<!-- Brand Col -->
				<div class="flex items-center gap-3">
					<div class="w-8 h-8 rounded-lg bg-[#007AFF] text-white flex items-center justify-center font-bold text-sm">
						P
					</div>
					<div>
						<span class="text-base font-bold text-slate-900 dark:text-white">
							Pantau<span class="text-[#007AFF]">Duit</span>
						</span>
						<p class="text-[11px] text-slate-400 mt-0.5">
							Telegram-First Financial Command Center
						</p>
					</div>
				</div>

				<!-- Maksimal 5 Pilihan Menu Sesuai Permintaan -->
				<nav class="flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-xs font-medium">
					<a href="#faq" class="hover:text-[#007AFF] transition-colors">Syarat & Ketentuan</a>
					<a href="#faq" class="hover:text-[#007AFF] transition-colors">Kebijakan Privasi</a>
					<a href="/telegram" class="hover:text-[#007AFF] transition-colors">Panduan Bot Telegram</a>
					<a href="#features" class="hover:text-[#007AFF] transition-colors">Keamanan Data</a>
					<a href="#faq" class="hover:text-[#007AFF] transition-colors">Bantuan & FAQ</a>
				</nav>
			</div>

			<div class="pt-6 flex flex-col sm:flex-row items-center justify-between gap-3 text-[11px] text-slate-400">
				<p>© 2026 PT Pantau Duit Solusindo. Hak Cipta Dilindungi Undang-Undang.</p>
				<div class="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-medium">
					<span class="w-2 h-2 rounded-full bg-emerald-500"></span>
					<span>Sistem Operasional (99.98% Uptime)</span>
				</div>
			</div>
		</div>
	</footer>
</div>

