// Domain Types matching Backend PostgreSQL Architecture & SvelteKit Domain Models

export type UUID = string;

export type UserStatus = 'ACTIVE' | 'SUSPENDED' | 'DELETED';
export type UserRole = 'SUBSCRIBER' | 'ADMIN' | 'SUPERUSER';

export interface User {
	id: UUID;
	email: string;
	name: string;
	avatar_url?: string;
	status: UserStatus;
	is_superadmin: boolean;
	role: UserRole;
	email_verified_at?: string;
	created_at: string;
}

export type TenantType = 'PERSONAL' | 'FAMILY' | 'BUSINESS';

export interface Tenant {
	id: UUID;
	name: string;
	slug: string;
	type: TenantType;
	currency: string;
	timezone: string;
}

export interface TenantUser {
	id: UUID;
	tenant_id: UUID;
	user_id: UUID;
	status: 'INVITED' | 'ACTIVE' | 'SUSPENDED' | 'REMOVED';
	joined_at: string;
	roles: Role[];
}

export interface Role {
	id: UUID;
	name: string;
	slug: string;
	description?: string;
	is_system: boolean;
	permissions?: Permission[];
}

export interface Permission {
	id: number;
	module: string;
	name: string;
	slug: string;
	description?: string;
}

export type AccountType = 'BANK' | 'CASH' | 'E_WALLET' | 'CREDIT_CARD' | 'INVESTMENT' | 'OTHER';
export type AccountStatus = 'ACTIVE' | 'ARCHIVED' | 'CLOSED';

export interface Account {
	id: UUID;
	tenant_id: UUID;
	name: string;
	type: AccountType;
	account_number?: string;
	institution_name?: string;
	currency: string;
	opening_balance?: number;
	current_balance: number;
	balance?: number;
	status: AccountStatus;
	is_active?: boolean;
	color?: string;
	icon?: string;
	created_at?: string;
	updated_at?: string;
}

export type CategoryType = 'EXPENSE' | 'INCOME' | 'INVESTMENT' | 'BOTH';

export interface Category {
	id: UUID;
	tenant_id?: UUID;
	parent_id?: UUID;
	name: string;
	slug: string;
	type: CategoryType;
	icon?: string;
	color?: string;
	is_system: boolean;
}

export type TransactionType = 'EXPENSE' | 'INCOME' | 'INVESTMENT' | 'TRANSFER' | 'REFUND';
export type TransactionSource = 'TELEGRAM' | 'DASHBOARD' | 'SYSTEM' | 'API' | 'MANUAL_WEB';
export type TransactionStatus = 'COMPLETED' | 'PENDING' | 'VOIDED' | 'DRAFT' | 'POSTED';

export interface Transaction {
	id: UUID;
	tenant_id: UUID;
	account_id: UUID;
	destination_account_id?: UUID;
	category_id?: UUID;
	amount: number;
	currency?: string;
	transaction_type: TransactionType;
	transaction_date: string;
	source: TransactionSource;
	status: TransactionStatus;
	description: string;
	notes?: string;
	receipt_url?: string;
	recurring_transaction_id?: UUID;
	metadata_json?: Record<string, any>;
	created_by?: UUID;
	created_at?: string;
	// Relational joins
	account_name?: string;
	destination_account_name?: string;
	category_name?: string;
	category_icon?: string;
	category_color?: string;
	account?: Account;
	category?: Category;
}

export type BudgetPeriod = 'WEEKLY' | 'MONTHLY' | 'YEARLY' | 'CUSTOM';

export interface Budget {
	id: UUID;
	tenant_id: UUID;
	category_id?: UUID;
	name: string;
	amount: number;
	limit_amount?: number;
	spent_amount: number;
	period: BudgetPeriod;
	start_date?: string;
	end_date?: string;
	alert_threshold_percent: number;
	is_active: boolean;
	category_name?: string;
	category_icon?: string;
	category?: Category;
	created_at?: string;
}

export type GoalStatus = 'IN_PROGRESS' | 'REACHED' | 'COMPLETED' | 'PAUSED' | 'CANCELLED';

export interface FinancialGoal {
	id: UUID;
	tenant_id: UUID;
	name: string;
	target_amount: number;
	current_amount: number;
	target_date?: string;
	status: GoalStatus;
	color?: string;
	icon?: string;
	created_at?: string;
}

export type AssetClass = 'STOCK' | 'CRYPTO' | 'MUTUAL_FUND' | 'BOND' | 'GOLD' | 'COMMODITY' | 'REAL_ESTATE' | 'DEPOSIT' | 'OTHER';

export interface InvestmentAsset {
	id: UUID;
	symbol: string;
	name: string;
	asset_type: AssetClass;
	currency: string;
	current_price: number;
	last_price_updated_at?: string;
}

export interface InvestmentHolding {
	id: UUID;
	tenant_id: UUID;
	account_id?: UUID;
	asset_id?: UUID;
	quantity: number;
	average_buy_price?: number;
	buy_price_avg: number;
	current_price: number;
	symbol: string;
	name: string;
	asset_class: AssetClass;
	unit_label?: string;
	notes?: string;
	currency?: string;
	updated_at?: string;
	asset?: InvestmentAsset;
	account?: Account;
}

export type SubscriptionStatus = 'PENDING' | 'ACTIVE' | 'GRACE_PERIOD' | 'EXPIRED' | 'CANCELLED' | 'SUSPENDED';

export interface PlanFeature {
	id: UUID;
	plan_id: UUID;
	feature_key: string;
	feature_value: string;
}

export interface Plan {
	id: UUID;
	code: string;
	name: string;
	description?: string;
	price: number;
	currency: string;
	interval: 'MONTHLY' | 'YEARLY' | 'LIFETIME';
	interval_count: number;
	trial_period_days: number;
	is_active: boolean;
	sort_order: number;
	features: PlanFeature[];
}

export interface Subscription {
	id: UUID;
	tenant_id: UUID;
	plan_id: UUID;
	status: SubscriptionStatus;
	tier?: 'free' | 'pro' | 'enterprise';
	started_at: string;
	current_period_start: string;
	current_period_end: string;
	grace_period_end?: string;
	cancel_at_period_end: boolean;
	plan?: Plan;
}

export interface Payment {
	id: UUID;
	tenant_id: UUID;
	invoice_number: string;
	external_payment_id?: string;
	amount: number;
	currency: string;
	payment_method?: string;
	payment_channel?: string;
	status: 'PENDING' | 'PAID' | 'FAILED' | 'EXPIRED' | 'REFUNDED';
	paid_at?: string;
	expires_at?: string;
	created_at: string;
}

export interface TelegramAccount {
	id: UUID;
	user_id: UUID;
	telegram_user_id: number;
	telegram_username?: string;
	first_name?: string;
	last_name?: string;
	auth_date?: string;
	is_blocked: boolean;
}

export interface TelegramChat {
	id: UUID;
	telegram_account_id: UUID;
	tenant_id: UUID;
	chat_id: number;
	chat_type: 'PRIVATE' | 'GROUP' | 'SUPERGROUP';
	title?: string;
	current_state: string;
	last_active_at?: string;
}

export interface NotificationItem {
	id: UUID;
	title: string;
	body: string;
	message?: string;
	is_read?: boolean;
	type: 'BUDGET' | 'LOW_BALANCE' | 'SYSTEM' | 'SUBSCRIPTION' | 'TELEGRAM' | 'SUCCESS' | 'WARNING' | 'ERROR' | 'PROMOTION';
	channel: 'TELEGRAM' | 'EMAIL' | 'DASHBOARD';
	status: 'PENDING' | 'SENT' | 'FAILED' | 'READ';
	created_at: string;
	read_at?: string;
}

// Dashboard Aggregation DTOs
export interface DashboardSummary {
	total_balance: number;
	monthly_income: number;
	monthly_expense: number;
	monthly_transfers: number;
	investment_total: number;
	income_change_pct: number;
	expense_change_pct: number;
	balance_change_pct: number;
}
