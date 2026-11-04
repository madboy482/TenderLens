import { afterEach, describe, expect, it, vi } from 'vitest'
import { getHealth } from './client'

describe('getHealth', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('returns the backend health payload', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(
        JSON.stringify({
          status: 'ok',
          service: 'tenderlens-backend',
          environment: 'development',
        }),
        { status: 200 },
      ),
    )

    await expect(getHealth()).resolves.toEqual({
      status: 'ok',
      service: 'tenderlens-backend',
      environment: 'development',
    })
  })

  it('surfaces an unsuccessful response', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(new Response(null, { status: 503 }))

    await expect(getHealth()).rejects.toThrow('Health check failed with status 503')
  })
})
