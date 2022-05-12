import '../styles/globals.css'
import type { AppProps } from 'next/app'
import { SWRConfig } from 'swr'

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <SWRConfig value={{
      refreshInterval: 500,
      fetcher: (resource: string, init) => {
        return fetch(resource, init).then((res) => res.json())
      }
    }}>
      <Component {...pageProps} />
    </SWRConfig>
  )
}

export default MyApp
