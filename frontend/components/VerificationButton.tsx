import { useEffect, useState } from "react";

interface VProps {
  transactionId: string;
  label: string;
  verificationUrl: string;
  verificationParam: string;
}

const VerificationButton = ({ transactionId, label, verificationUrl, verificationParam }: VProps) => {
  const [data, setData] = useState({});
  const options = {
    method: "POST",
    body: JSON.stringify({
      data: {
        [verificationParam]: transactionId
      }
    }),
    headers: {
      accept: "application/json",
      "Content-Type": "application/json",
    },
  };

  useEffect(() => {
    try {
      fetch(verificationUrl, options).then(r => r.json().then(r => { setData(r) }));
    } catch (e) { }
  }, [transactionId]);


  return <>
    {transactionId &&
      <>
        <label htmlFor={transactionId} className="btn btn-xs modal-button">{label}</label>

        <input type="checkbox" id={transactionId} className="modal-toggle" />
        <div className="modal">
          <div className="relative max-w-full text-left modal-box min-w-fit">
            <label htmlFor={transactionId} className="absolute btn btn-sm btn-circle right-2 top-2">✕</label>
            <h3 className="pb-8 text-lg font-bold">Congratulations this is notarized on {label}!</h3>
            <span className="font-bold">Transaction tag:</span> <span className="font-mono font-bold text-error">{transactionId}</span>
            <h4 className="my-4 font-bold">Notarized data:</h4>
            <pre className="max-w-full p-4 my-2 overflow-auto break-all rounded bg-slate-900 text-slate-200">{JSON.stringify(data, null, 2)}</pre>
          </div>
        </div>
      </>}
  </>
}

export default VerificationButton
