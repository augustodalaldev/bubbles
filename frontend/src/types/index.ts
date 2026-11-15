// Core Types matching Bubbles Django Backend API

export interface User {
  id: number;
  username: string;
  name: string;
  description: string;
  profile_photo: string | null;
  customization_json: Record<string, any>;
  is_active: boolean;
  created_at: string;
  // Extended fields for current/detail user:
  email?: string;
  birth_date?: string;
  status?: "ACTIVE" | "SUSPENDED" | "BANNED";
  is_suspended?: boolean;
  suspended_until?: string | null;
  soap_balance?: number;
  wallet?: {
    soap_balance: number;
    passive_earn_rate: number | null;
  };
  followers_count?: number;
  following_count?: number;
  is_following?: boolean;
  is_followed_by?: boolean;
}

export interface Community {
  id: number;
  commname: string;
  name: string;
  description: string;
  guidelines?: string;
  community_photo: string | null;
  banner_photo: string | null;
  customization_json: Record<string, any>;
  member_count: number;
  created_at: string;
  is_archived?: boolean;
  is_blocked?: boolean;
  permissions?: {
    can_edit: boolean;
    can_edit_guidelines: boolean;
    can_manage_members: boolean;
    can_manage_admins: boolean;
    can_transfer_leadership: boolean;
    can_archive: boolean;
    can_view_wallet: boolean;
    can_join: boolean;
    can_leave: boolean;
  };
}

export interface BubblegramMedia {
  id: number;
  media: string;
  position: number;
}

export interface Bubblegram {
  id: number;
  user: User;
  community: Community | null;
  text: string;
  type: "TEXT" | "MEDIA";
  media: BubblegramMedia[];
  soap_count: number;
  published_at: string;
  is_suggested?: boolean;
  suggestion_reason?: string | null;
  can_delete?: boolean;
}

export interface Bubblepop {
  id: number;
  user: User;
  image: string;
  description: string;
  created_at: string;
  expires_at: string;
}

export interface CustomizationItem {
  id: number;
  name: string;
  code: string;
  item_type: "AVATAR_FRAME" | "PROFILE_THEME" | "CHAT_BUBBLE" | "BADGE" | "NAME_COLOR";
  description: string;
  price: number;
  metadata: Record<string, any>;
  is_active: boolean;
  created_at: string;
  is_owned?: boolean;
  is_equipped?: boolean;
}

export interface UserInventoryItem {
  id: number;
  item: CustomizationItem;
  acquired_at: string;
  is_equipped: boolean;
}
