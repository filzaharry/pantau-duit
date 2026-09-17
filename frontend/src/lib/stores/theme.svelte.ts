export type Theme = 'light' | 'dark' | 'system';

class ThemeStore {
	current = $state<Theme>('system');
	isDark = $state(false);

	constructor() {
		if (typeof window !== 'undefined') {
			const saved = (localStorage.getItem('pantau_theme') as Theme) || 'system';
			this.setTheme(saved);

			window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
				if (this.current === 'system') {
					this.applyTheme();
				}
			});
		}
	}

	setTheme(theme: Theme) {
		this.current = theme;
		if (typeof window !== 'undefined') {
			localStorage.setItem('pantau_theme', theme);
			this.applyTheme();
		}
	}

	private applyTheme() {
		const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
		this.isDark = this.current === 'dark' || (this.current === 'system' && prefersDark);
		if (this.isDark) {
			document.documentElement.classList.add('dark');
		} else {
			document.documentElement.classList.remove('dark');
		}
	}
}

export const themeStore = new ThemeStore();
