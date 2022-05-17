import type { NextPage } from 'next'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'

import useSwr from 'swr'
import { useState } from 'react'
import StatusBar from '../components/StatusBar'
import VerificationButton from '../components/VerificationButton'

dayjs.extend(relativeTime)

const API_URL = process.env.NEXT_PUBLIC_API_URL
interface Repository {
  url: string;
  hash: string;
  date_last_updated: string;
  date_created: string;
  reuse_compliant: boolean;
  fabric_tag: string;
  sawroom_tag: string;
  ethereum_tag: string;
  status: {
    state: number;
  }[]
}

const Home: NextPage = () => {
  const { data, error } = useSwr(`${API_URL}/repositories`)
  const [repo, addRepo] = useState("")

  const onAddRepo = async () => {
    const create = `${API_URL}/repository`
    const scan = `${API_URL}/scan`
    const options = {
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      method: "POST",
      body: JSON.stringify({
        url: repo
      })
    }
    await fetch(create, options);
    await fetch(scan, options);
  }

  return (
    <section>
      <div className="bg-gray-50">
        <div className="px-4 py-12 mx-auto max-w-7xl sm:px-6 lg:py-16 lg:px-8 lg:flex lg:items-center lg:justify-between">
          <h2 className="text-3xl font-extrabold tracking-tight text-gray-900 sm:text-4xl">
            <span className="block">Ready to find licenses in a repo?</span>
            <span className="block text-indigo-600">Scan your first repo for free today.</span>
          </h2>
          <div className="flex mt-8 lg:mt-0 lg:flex-shrink-0">
            <div className="inline-flex rounded-md">
              <input type="url" placeholder="git repository" className="w-full input input-bordered" onChange={e => {
                addRepo(e.target.value)
              }} />
            </div>
            <div className="inline-flex ml-3 rounded-md shadow">
              <a href="#" onClick={onAddRepo}
                className="inline-flex items-center justify-center px-5 py-3 text-base font-medium text-white bg-indigo-600 border border-transparent rounded-md hover:bg-indigo-700"> Scan a new repo </a>
            </div>
          </div>
        </div>
      </div>
      <div className="w-full pt-10 mt-10 overflow-x-auto">
        <table className="table min-w-full text-center">
          <thead>
            <tr>
              <th>Repo</th>
              <th>Status</th>
              <th>REUSE compliant</th>
              <th>Blockchain</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {data?.map((repository: Repository) => (
              <tr key={repository.url}>
                <td>
                  <div className="flex items-center space-x-3">
                    <div>
                      <div className="font-bold"><a href={repository.url}>{repository.url}</a></div>
                      <div className="text-sm opacity-50">head: {repository.hash}</div>
                      <div className="text-sm opacity-40">updated {dayjs().to(repository.date_last_updated || repository.date_created)}</div>
                    </div>
                  </div>
                </td>
                <td>
                  <StatusBar status={repository.status} />
                </td>
                <td>{repository.reuse_compliant ? "✅" : "🚫"}</td>
                <td className="flex flex-col">
                  <VerificationButton transactionId={repository.fabric_tag} label="fabric" verificationUrl="https://apiroom.net/api/zenbridge/fabric-read" verificationParam="myFabricTag" />
                  <VerificationButton transactionId={repository.sawroom_tag} label="sawroom" verificationUrl="https://apiroom.net/api/zenbridge/sawroom-read" verificationParam="mySawroomTag" />
                  <VerificationButton transactionId={repository.ethereum_tag} label="ethereum" verificationUrl="https://apiroom.net/api/zenbridge/ethereum-read" verificationParam="txid" />
                </td>
                <td>
                  <button className="btn btn-xs">re-scan</button>
                </td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr>
              <th>Repo</th>
              <th>Status</th>
              <th>REUSE compliant</th>
              <th>Blockchain</th>
              <th></th>
            </tr>
          </tfoot>
        </table>
      </div>
    </section>
  )
}

export default Home