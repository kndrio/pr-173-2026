import React, { createContext, useCallback, useContext, useState } from 'react'
import { getMe, loginUser, registerUser, setAuthToken } from '../lib/api'
import type { UserInfo } from '../types'

interface AuthState {
  user: UserInfo | null
  isAuthenticated: boolean
  isLoading: boolean
}

interface AuthContextValue extends AuthState {
  login: (email: string, password: string) => Promise<void>
  register: (fullName: string, email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: false,
  })

  const login = useCallback(async (email: string, password: string) => {
    setState((s) => ({ ...s, isLoading: true }))
    try {
      const { access_token } = await loginUser(email, password)
      setAuthToken(access_token)
      const user = await getMe()
      setState({ user, isAuthenticated: true, isLoading: false })
    } catch (err) {
      setState((s) => ({ ...s, isLoading: false }))
      throw err
    }
  }, [])

  const register = useCallback(async (fullName: string, email: string, password: string) => {
    setState((s) => ({ ...s, isLoading: true }))
    try {
      await registerUser(fullName, email, password)
      setState((s) => ({ ...s, isLoading: false }))
    } catch (err) {
      setState((s) => ({ ...s, isLoading: false }))
      throw err
    }
  }, [])

  const logout = useCallback(() => {
    setAuthToken(null)
    setState({ user: null, isAuthenticated: false, isLoading: false })
  }, [])

  return (
    <AuthContext.Provider value={{ ...state, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
