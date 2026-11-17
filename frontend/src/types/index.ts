// Types mirroring the Bubbles Django API (see backend serializers).

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface Wallet {
  soap_balance: number;
  passive_earn_rate: number | null;
}

export interface User {
  id: number;
  username: string;
  name: string;
  description: string;
  profile_photo: string | null;
  customization_json: Record<string, any>;
  is_active: boolean;
  created_at: string;
  // Only on the authenticated user (GET /users/me/, login, register):
  email?: string;
  birth_date?: string;
  is_staff?: boolean;
  status?: "ACTIVE" | "SUSPENDED" | "BANNED";
  is_suspended?: boolean;
  suspended_until?: string | null;
  soap_balance?: number;
  wallet?: Wallet | null;
  last_seen_at?: string;
  // On /users/me/ and public profiles:
  followers_count?: number;
  following_count?: number;
  // Only on public profiles (GET /users/{username}/):
  is_following?: boolean;
  is_followed_by?: boolean;
}

export type MemberRole = "LEADER" | "COMM_ADMIN" | "MEMBER";
export type MemberState = "ACTIVE" | "SILENCED" | "BANNED";

export interface CommunityPermissions {
  can_edit: boolean;
  can_edit_guidelines: boolean;
  can_manage_members: boolean;
  can_manage_admins: boolean;
  can_transfer_leadership: boolean;
  can_archive: boolean;
  can_view_wallet: boolean;
  can_join: boolean;
  can_leave: boolean;
}

/** Community as embedded in a bubblegram. */
export interface CommunityRef {
  id: number;
  commname: string;
  name: string;
}

export interface Community extends CommunityRef {
  description: string;
  community_photo: string | null;
  banner_photo: string | null;
  customization_json: Record<string, any>;
  member_count: number;
  created_at: string;
  is_archived: boolean;
  // Only on the detail endpoint:
  guidelines?: string;
  archived_at?: string | null;
  my_membership?: { role: MemberRole; current_state: MemberState; joined_at: string } | null;
  permissions?: CommunityPermissions;
}

export interface CommunityMemberItem {
  id: number;
  user: User;
  role: MemberRole;
  current_state: MemberState;
  joined_at: string;
}

export interface BubblegramMedia {
  id: number;
  media: string;
  position: number;
}

export interface Bubblegram {
  id: number;
  user: User;
  community: CommunityRef | null;
  text: string;
  type: "TEXT" | "MEDIA";
  media: BubblegramMedia[];
  soap_count: number;
  published_at: string;
  is_suggested: boolean;
  suggestion_reason: "popular" | "network" | null;
  can_delete: boolean;
}

export interface Comment {
  id: number;
  bubblegram: number;
  user: User;
  parent: number | null;
  text: string;
  soap_count: number;
  published_at: string;
  can_delete: boolean;
}

export interface Bubblepop {
  id: number;
  user: User;
  image: string;
  description: string;
  created_at: string;
  expires_at: string;
  is_expired: boolean;
  can_delete: boolean;
}

export interface Letter {
  id: number;
  sender: User;
  recipient: User;
  reply_to: number | null;
  text: string;
  image: string | null;
  sent_at: string;
  read_at: string | null;
  is_read: boolean;
}

export type CustomizationType =
  | "AVATAR_FRAME"
  | "PROFILE_THEME"
  | "CHAT_BUBBLE"
  | "BADGE"
  | "NAME_COLOR";

export interface CustomizationItem {
  id: number;
  name: string;
  code: string;
  item_type: CustomizationType;
  description: string;
  price: number;
  metadata: Record<string, any>;
  is_active: boolean;
  created_at: string;
  is_owned: boolean;
  is_equipped: boolean;
}

export interface UserInventoryItem {
  id: number;
  item: CustomizationItem;
  acquired_at: string;
  is_equipped: boolean;
}

export interface FollowItem {
  id: number;
  user: User;
  created_at: string;
}

export interface SearchResult {
  query: string;
  users: User[];
  communities: Community[];
}

export interface EconomySettings {
  signup_grant: number;
  support_cost: number;
  author_credit: number;
  community_credit: number;
  bubblegram_profile_cost: number;
  bubblegram_community_cost: number;
  bubblepop_hours_per_soap: number;
  bubblepop_min_hours: number;
  bubblepop_max_hours: number;
  founding_cost: number;
  default_passive_earn_rate: number;
  passive_interval_minutes: number;
  passive_daily_cap: number;
}
