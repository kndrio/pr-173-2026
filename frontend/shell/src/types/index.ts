export interface UserInfo {
  id: string
  email: string
  full_name: string
  role: string
  is_active: boolean
  created_at: string
}

export interface AuthTokenResponse {
  access_token: string
  token_type: string
}
